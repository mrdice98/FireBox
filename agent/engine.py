"""
FireBox Autonomous Agent Engine.
Core closed-loop execution engine: Observe -> Plan -> Act -> Verify -> Iterate.
"""

import time
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional, Generator

from firebox.agent.modes import AgentMode
from firebox.agent.planner import ExecutionPlan, PlanStep
from firebox.agent.context import ContextManager
from firebox.agent.session import get_session_manager
from firebox.providers.base import BaseProvider, ChatMessage, ChatResponse, ToolCall
from firebox.providers.registry import get_provider_registry
from firebox.tools.registry import get_tool_registry
from firebox.config.manager import get_config
from firebox.ui.theme import get_console, COLOR_FIRE_FLAME, COLOR_FIRE_GOLD, COLOR_SUCCESS, COLOR_ERROR
from firebox.ui.animations import print_thinking, print_tool_start, print_tool_finish
from firebox.ui.formatters import render_markdown, render_plan, render_tool_result_card


class AgentEngine:
    """Orchestrates autonomous coding agents across multi-turn tool-calling loops."""

    def __init__(
        self,
        workspace_root: Optional[Path] = None,
        session_id: Optional[str] = None,
        mode: AgentMode = AgentMode.AUTONOMOUS,
    ):
        if workspace_root is None:
            workspace_root = Path.cwd().resolve()
        self.workspace_root = workspace_root.resolve()
        self.session_id = session_id or f"session_{uuid.uuid4().hex[:8]}"
        self.mode = mode

        self.config_mgr = get_config()
        self.provider_reg = get_provider_registry()
        self.tool_reg = get_tool_registry(self.workspace_root)
        self.context_mgr = ContextManager(
            workspace_root=self.workspace_root,
            max_token_limit=self.config_mgr.app_config.context_token_limit,
        )
        self.session_mgr = get_session_manager()

        self.messages: List[ChatMessage] = []
        self.plan: Optional[ExecutionPlan] = None
        self.iteration_count = 0
        self.max_iterations = self.config_mgr.app_config.max_agent_iterations

        self._init_session()

    def _init_session(self):
        """Load existing session or initialize new one with master system prompt."""
        existing = self.session_mgr.load_session(self.session_id)
        if existing:
            self.mode = AgentMode(existing.mode)
            self.messages = [ChatMessage(**m) for m in existing.messages]
            if existing.plan:
                self.plan = ExecutionPlan(**existing.plan)
        else:
            system_prompt = self.context_mgr.build_system_prompt(self.mode)
            self.messages.append(ChatMessage(role="system", content=system_prompt))

    def set_mode(self, mode: AgentMode):
        """Update active mode and adjust system prompt."""
        self.mode = mode
        system_prompt = self.context_mgr.build_system_prompt(self.mode)
        if self.messages and self.messages[0].role == "system":
            self.messages[0].content = system_prompt
        else:
            self.messages.insert(0, ChatMessage(role="system", content=system_prompt))

    def _filter_tools_for_mode(self) -> List[Dict[str, Any]]:
        """Filter available tools according to the active mode."""
        schemas = self.tool_reg.get_openai_schemas()
        if self.mode in (AgentMode.ASK, AgentMode.PLAN):
            # Only allow read-only tools
            read_only_tools = {
                "read_file", "list_dir", "file_search", "text_search",
                "code_symbol_search", "detect_project", "inspect_dependencies",
                "web_search", "fetch_url", "git_status", "git_diff", "git_log"
            }
            return [s for s in schemas if s["function"]["name"] in read_only_tools]
        return schemas

    def run_turn(
        self,
        user_input: str,
        stream_callback: Optional[Any] = None,
    ) -> str:
        """Execute a full autonomous agent turn in response to user input."""
        console = get_console()

        # Append user message
        self.messages.append(ChatMessage(role="user", content=user_input))

        # Check and compact context if needed
        if self.config_mgr.app_config.auto_compact_context:
            self.messages = self.context_mgr.compact_context(self.messages)

        provider = self.provider_reg.get_provider()
        model_name = self.config_mgr.app_config.active_model
        tools = self._filter_tools_for_mode()

        final_response_text = ""
        self.iteration_count = 0

        while self.iteration_count < self.max_iterations:
            self.iteration_count += 1
            print_thinking(f"Step {self.iteration_count}/{self.max_iterations} — querying model ({model_name})...")

            try:
                # Call provider
                response: ChatResponse = provider.chat_complete(
                    messages=self.messages,
                    tools=tools,
                    model=model_name,
                    temperature=0.2,
                )
            except Exception as e:
                err_msg = f"Provider error from {provider.name}: {str(e)}"
                console.print(f"[bold {COLOR_ERROR}]✖ {err_msg}[/]")
                return err_msg

            # Print reasoning if available
            if response.reasoning_content:
                console.print(f"[dim {COLOR_FIRE_GOLD}]✦ Reasoning: {response.reasoning_content[:200]}...[/dim]")

            # Record assistant turn in history
            self.messages.append(
                ChatMessage(
                    role="assistant",
                    content=response.content,
                    tool_calls=response.tool_calls or None,
                    reasoning_content=response.reasoning_content,
                )
            )

            # Case A: Model requested tool calls
            if response.tool_calls:
                for tc in response.tool_calls:
                    print_tool_start(tc.name, str(tc.arguments))
                    t_start = time.time()

                    # Execute tool
                    tool_res = self.tool_reg.execute_tool(tc.name, tc.arguments)
                    elapsed = (time.time() - t_start) * 1000

                    print_tool_finish(tc.name, success=tool_res.success, elapsed_ms=elapsed)
                    render_tool_result_card(tc.name, tool_res.output or str(tool_res.error), success=tool_res.success, duration_ms=elapsed)

                    # Feed tool output back to model
                    tool_msg_content = tool_res.output if tool_res.success else f"Error: {tool_res.error}"
                    self.messages.append(
                        ChatMessage(
                            role="tool",
                            name=tc.name,
                            tool_call_id=tc.id,
                            content=tool_msg_content,
                        )
                    )

                # Continue agent loop with tool results
                continue

            # Case B: Model returned plain text response
            final_response_text = response.content
            if final_response_text:
                render_markdown(final_response_text)
            break

        # Persist session state
        self.session_mgr.save_session(
            session_id=self.session_id,
            workspace_root=self.workspace_root,
            messages=self.messages,
            plan=self.plan,
            mode=self.mode,
            provider=provider.name,
            model=model_name,
        )

        return final_response_text
