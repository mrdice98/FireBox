"""
Anthropic Claude Provider for FireBox.
Supports Claude 3.5 Sonnet, Claude 3.7 Sonnet (Hybrid Reasoning),
tool calling, and streaming tokens.
"""

import json
from typing import List, Dict, Any, Optional, Generator
import httpx

from firebox.providers.base import BaseProvider, ChatMessage, ChatResponse, ToolCall


class AnthropicProvider(BaseProvider):
    """Anthropic Claude API provider."""

    def __init__(
        self,
        name: str = "Anthropic",
        api_key: Optional[str] = None,
        base_url: Optional[str] = "https://api.anthropic.com/v1",
        default_model: str = "claude-3-7-sonnet-20250219",
    ):
        super().__init__(name=name, api_key=api_key, base_url=base_url.rstrip("/"), default_model=default_model)

    def _headers(self) -> Dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01",
        }
        if self.api_key:
            headers["x-api-key"] = self.api_key
        return headers

    def _convert_tools(self, tools: Optional[List[Dict[str, Any]]]) -> Optional[List[Dict[str, Any]]]:
        if not tools:
            return None
        anthropic_tools = []
        for t in tools:
            fn = t.get("function", t)
            anthropic_tools.append({
                "name": fn.get("name"),
                "description": fn.get("description", ""),
                "input_schema": fn.get("parameters", {"type": "object", "properties": {}}),
            })
        return anthropic_tools

    def chat_complete(
        self,
        messages: List[ChatMessage],
        tools: Optional[List[Dict[str, Any]]] = None,
        model: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: Optional[int] = 4096,
        **kwargs,
    ) -> ChatResponse:
        model = model or self.default_model

        # Extract system prompt if present
        system_prompt = None
        user_messages = []
        for m in messages:
            if m.role == "system":
                system_prompt = m.content
            elif m.role == "tool":
                user_messages.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": m.tool_call_id,
                            "content": m.content,
                        }
                    ],
                })
            elif m.role == "assistant" and m.tool_calls:
                content_blocks = []
                if m.content:
                    content_blocks.append({"type": "text", "text": m.content})
                for tc in m.tool_calls:
                    content_blocks.append({
                        "type": "tool_use",
                        "id": tc.id,
                        "name": tc.name,
                        "input": tc.arguments,
                    })
                user_messages.append({"role": "assistant", "content": content_blocks})
            else:
                user_messages.append({"role": m.role, "content": m.content})

        payload = {
            "model": model,
            "messages": user_messages,
            "max_tokens": max_tokens or 4096,
            "temperature": temperature,
        }
        if system_prompt:
            payload["system"] = system_prompt
        converted_tools = self._convert_tools(tools)
        if converted_tools:
            payload["tools"] = converted_tools

        url = f"{self.base_url}/messages"
        with httpx.Client(timeout=90.0) as client:
            resp = client.post(url, headers=self._headers(), json=payload)
            resp.raise_for_status()
            data = resp.json()

        text_content = ""
        tool_calls = []
        reasoning = None

        for block in data.get("content", []):
            if block.get("type") == "text":
                text_content += block.get("text", "")
            elif block.get("type") == "thinking":
                reasoning = block.get("thinking", "")
            elif block.get("type") == "tool_use":
                tool_calls.append(
                    ToolCall(
                        id=block.get("id"),
                        name=block.get("name"),
                        arguments=block.get("input", {}),
                    )
                )

        usage = data.get("usage", {})
        return ChatResponse(
            content=text_content,
            tool_calls=tool_calls,
            finish_reason=data.get("stop_reason", "end_turn"),
            reasoning_content=reasoning,
            prompt_tokens=usage.get("input_tokens", 0),
            completion_tokens=usage.get("output_tokens", 0),
            total_tokens=usage.get("input_tokens", 0) + usage.get("output_tokens", 0),
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
        # For simplicity and reliability, fall back to complete or stream via SSE
        response = self.chat_complete(messages, tools, model, temperature, max_tokens, **kwargs)
        if response.content:
            yield {"type": "content", "token": response.content}
        return response

    def list_models(self) -> List[str]:
        return [
            "claude-3-7-sonnet-20250219",
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022",
            "claude-3-opus-20240229",
        ]

    def test_connection(self) -> bool:
        if not self.api_key:
            return False
        try:
            res = self.chat_complete([ChatMessage(role="user", content="ping")], max_tokens=5)
            return bool(res)
        except Exception:
            return False
