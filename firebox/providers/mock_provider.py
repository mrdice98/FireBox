"""
High-Fidelity Mock AI Provider for FireBox.
Enables full offline execution, unit testing, and sandbox verification
without incurring API costs or requiring live tokens.
"""

from typing import List, Dict, Any, Optional, Generator
import json
import re

from firebox.providers.base import BaseProvider, ChatMessage, ChatResponse, ToolCall


class MockProvider(BaseProvider):
    """Deterministic offline simulation provider for testing and demos."""

    def __init__(
        self,
        name: str = "Mock/Offline",
        api_key: Optional[str] = "mock-key",
        base_url: Optional[str] = "http://localhost:0",
        default_model: str = "firebox-sim-1.0",
    ):
        super().__init__(name=name, api_key=api_key, base_url=base_url, default_model=default_model)

    def chat_complete(
        self,
        messages: List[ChatMessage],
        tools: Optional[List[Dict[str, Any]]] = None,
        model: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: Optional[int] = 4096,
        **kwargs,
    ) -> ChatResponse:
        # Check if last message was a tool result (conclude the loop)
        if messages and messages[-1].role == "tool":
            tool_msg = messages[-1]
            return ChatResponse(
                content=f"Tool '{tool_msg.name}' completed with result. Task successfully executed and verified.",
                finish_reason="stop",
                prompt_tokens=50,
                completion_tokens=25,
                total_tokens=75,
            )

        last_user_msg = ""
        for m in reversed(messages):
            if m.role == "user":
                last_user_msg = m.content.lower()
                break

        # Check for simulated tool invocation requests
        if tools and "read" in last_user_msg:
            # Simulate read_file call
            match = re.search(r'read\s+(?:file\s+)?([a-zA-Z0-9_\-\.\/\\]+)', last_user_msg)
            path = match.group(1) if match else "README.md"
            return ChatResponse(
                content="I will read the requested file to inspect its contents.",
                tool_calls=[ToolCall(id="call_mock_1", name="read_file", arguments={"path": path})],
                finish_reason="tool_calls",
            )
        elif tools and ("create" in last_user_msg or "write" in last_user_msg):
            return ChatResponse(
                content="I will create the necessary project file.",
                tool_calls=[ToolCall(id="call_mock_2", name="write_file", arguments={"path": "example.txt", "content": "Created by FireBox"})],
                finish_reason="tool_calls",
            )
        elif tools and "test" in last_user_msg:
            return ChatResponse(
                content="I will run the project tests now.",
                tool_calls=[ToolCall(id="call_mock_3", name="run_tests", arguments={})],
                finish_reason="tool_calls",
            )

        return ChatResponse(
            content=f"FireBox AI Agent acknowledged: '{last_user_msg}'. All systems operational.",
            finish_reason="stop",
            prompt_tokens=42,
            completion_tokens=18,
            total_tokens=60,
        )

    def stream_chat(
        self,
        messages: List[ChatMessage],
        tools: Optional[List[Dict[str, Any]]] = None,
        model: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: Optional[int] = 4096,
        **kwargs,
    ) -> Generator[Dict[str, Any], None, ChatResponse]:
        res = self.chat_complete(messages, tools, model, temperature, max_tokens, **kwargs)
        words = res.content.split(" ")
        for w in words:
            yield {"type": "content", "token": w + " "}
        return res

    def list_models(self) -> List[str]:
        return ["firebox-sim-1.0", "firebox-sim-pro"]

    def test_connection(self) -> bool:
        return True
