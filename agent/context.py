"""
Context & Project Instruction Manager for FireBox.
Loads project instruction files (FIREBOX.md, AGENTS.md, CLAUDE.md),
calculates token usage, and performs context compression/summarization.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
import os

from firebox.providers.base import ChatMessage
from firebox.agent.modes import AgentMode


class ContextManager:
    """Manages workspace instruction injection, token counting, and compression."""

    def __init__(self, workspace_root: Optional[Path] = None, max_token_limit: int = 100000):
        if workspace_root is None:
            workspace_root = Path.cwd().resolve()
        self.workspace_root = workspace_root.resolve()
        self.max_token_limit = max_token_limit

    def estimate_tokens(self, text: str) -> int:
        """Heuristic token estimation (~4 characters per token)."""
        if not text:
            return 0
        return max(1, len(text) // 4)

    def load_project_instructions(self) -> str:
        """Discover and load FIREBOX.md, AGENTS.md, CLAUDE.md, and README.md."""
        instruction_candidates = [
            "FIREBOX.md",
            ".firebox/FIREBOX.md",
            "AGENTS.md",
            "CLAUDE.md",
        ]
        loaded_instructions = []

        for fname in instruction_candidates:
            p = self.workspace_root / fname
            if p.exists() and p.is_file():
                try:
                    content = p.read_text(encoding="utf-8", errors="replace")
                    loaded_instructions.append(f"=== Project Instruction File: {fname} ===\n{content}")
                    break # Prioritize first matching instruction file
                except Exception:
                    pass

        # Optional brief README excerpt
        readme_p = self.workspace_root / "README.md"
        if readme_p.exists() and readme_p.is_file():
            try:
                readme_text = readme_p.read_text(encoding="utf-8", errors="replace")
                # First 50 lines of README
                first_lines = "\n".join(readme_text.splitlines()[:50])
                loaded_instructions.append(f"=== Workspace README.md Summary ===\n{first_lines}")
            except Exception:
                pass

        return "\n\n".join(loaded_instructions)

    def build_system_prompt(self, mode: AgentMode = AgentMode.AUTONOMOUS) -> str:
        """Compose the master FireBox system prompt tailored to the active mode."""
        base_prompt = (
            "You are FireBox, the premier next-generation autonomous AI coding agent.\n"
            "Tagline: IGNITE YOUR CODE. BURN THROUGH TASKS.\n\n"
            "CORE PRINCIPLES:\n"
            "1. Real Actions: You have access to real tools (file operations, search, shell execution, git, project analysis).\n"
            "   Never pretend to execute changes; always use tools to read, edit, write, and verify.\n"
            "2. Safety First: Never execute destructive system commands. Operate strictly inside the user's project workspace.\n"
            "3. Verify Everything: After writing or editing code, run tests, builds, or linting using provided tools to confirm success.\n"
            "4. Dynamic-First, Coordinate-Fallback: When inspecting code, locate definitions accurately.\n"
            "5. Concise & Professional: Provide clear, actionable answers and report concrete outcomes.\n\n"
            f"ACTIVE MODE: {mode.value.upper()}\n"
        )

        if mode == AgentMode.ASK:
            base_prompt += "You are in ASK mode. Answer questions and explain code. DO NOT modify files or run destructive tools.\n"
        elif mode == AgentMode.PLAN:
            base_prompt += "You are in PLAN mode. Analyze requirements and output a comprehensive step-by-step milestone plan without modifying code.\n"
        elif mode == AgentMode.BUILD:
            base_prompt += "You are in BUILD mode. Implement code changes, create files, and verify results directly.\n"
        elif mode == AgentMode.AUTONOMOUS:
            base_prompt += "You are in AUTONOMOUS mode. Perform multi-step execution: inspect codebase -> plan -> run tools -> test -> verify -> finish.\n"
        elif mode == AgentMode.REVIEW:
            base_prompt += "You are in REVIEW mode. Analyze code for bugs, security vulnerabilities, performance bottlenecks, and style.\n"

        instructions = self.load_project_instructions()
        if instructions:
            base_prompt += f"\nPROJECT SPECIFIC INSTRUCTIONS:\n{instructions}\n"

        return base_prompt

    def count_conversation_tokens(self, messages: List[ChatMessage]) -> int:
        """Calculate total tokens across all messages in conversation."""
        total = 0
        for m in messages:
            total += self.estimate_tokens(m.content)
            if m.tool_calls:
                for tc in m.tool_calls:
                    total += self.estimate_tokens(str(tc.arguments))
        return total

    def compact_context(self, messages: List[ChatMessage]) -> List[ChatMessage]:
        """Summarize and compact history if it exceeds context token budget."""
        total_tokens = self.count_conversation_tokens(messages)
        if total_tokens <= self.max_token_limit or len(messages) <= 6:
            return messages

        # Preserve system prompt (messages[0]) and recent turns (last 4 messages)
        system_msg = messages[0] if messages and messages[0].role == "system" else None
        recent_messages = messages[-4:]

        # Compact middle messages into an executive summary
        middle = messages[1:-4] if system_msg else messages[:-4]
        summary_snippets = []
        for m in middle:
            if m.role in ("user", "assistant") and m.content:
                preview = m.content[:150].replace("\n", " ")
                summary_snippets.append(f"[{m.role.upper()}]: {preview}...")

        summary_content = (
            "=== COMPACTED EARLIER CONVERSATION SUMMARY ===\n" +
            "\n".join(summary_snippets) +
            "\n=============================================="
        )

        summary_msg = ChatMessage(role="system", content=summary_content)
        new_history = []
        if system_msg:
            new_history.append(system_msg)
        new_history.append(summary_msg)
        new_history.extend(recent_messages)
        return new_history
