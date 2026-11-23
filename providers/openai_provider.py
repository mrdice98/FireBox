"""
OpenAI & OpenAI-Compatible Provider for FireBox.
Supports OpenAI, OpenRouter, Groq, DeepSeek, Mistral, xAI, Together,
Fireworks, Cerebras, Ollama, LM Studio, and any custom OpenAI endpoint.
"""

import json
from typing import List, Dict, Any, Optional, Generator
import httpx

from firebox.providers.base import BaseProvider, ChatMessage, ChatResponse, ToolCall


class OpenAICompatibleProvider(BaseProvider):
    """Universal OpenAI-compatible API provider."""

    def __init__(
        self,
        name: str = "OpenAI",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        default_model: str = "gpt-4o",
    ):
        if base_url is None:
            base_url = "https://api.openai.com/v1"
        super().__init__(name=name, api_key=api_key, base_url=base_url.rstrip("/"), default_model=default_model)

    def _headers(self) -> Dict[str, str]:
        headers = {
            "Content-Type": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _format_messages(self, messages: List[ChatMessage]) -> List[Dict[str, Any]]:
        formatted = []
        for m in messages:
            msg_dict = {"role": m.role, "content": m.content}
            if m.name:
                msg_dict["name"] = m.name
            if m.tool_call_id:
                msg_dict["tool_call_id"] = m.tool_call_id
            if m.tool_calls:
                msg_dict["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.name,
                            "arguments": json.dumps(tc.arguments) if isinstance(tc.arguments, dict) else str(tc.arguments),
                        },
                    }
                    for tc in m.tool_calls
                ]
            formatted.append(msg_dict)
        return formatted

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
        payload = {
            "model": model,
            "messages": self._format_messages(messages),
            "temperature": temperature,
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        payload.update(kwargs)

        url = f"{self.base_url}/chat/completions"
        with httpx.Client(timeout=90.0) as client:
            resp = client.post(url, headers=self._headers(), json=payload)
            resp.raise_for_status()
            data = resp.json()

        choice = data["choices"][0]
        msg = choice["message"]
        content = msg.get("content") or ""
        reasoning = msg.get("reasoning_content")

        tool_calls = []
        if "tool_calls" in msg and msg["tool_calls"]:
            for tc in msg["tool_calls"]:
                try:
                    args = json.loads(tc["function"]["arguments"])
                except Exception:
                    args = {"raw": tc["function"]["arguments"]}
                tool_calls.append(
                    ToolCall(id=tc["id"], name=tc["function"]["name"], arguments=args)
                )

        usage = data.get("usage", {})
        return ChatResponse(
            content=content,
            tool_calls=tool_calls,
            finish_reason=choice.get("finish_reason", "stop"),
            reasoning_content=reasoning,
            prompt_tokens=usage.get("prompt_tokens", 0),
            completion_tokens=usage.get("completion_tokens", 0),
            total_tokens=usage.get("total_tokens", 0),
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
        model = model or self.default_model
        payload = {
            "model": model,
            "messages": self._format_messages(messages),
            "temperature": temperature,
            "stream": True,
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        payload.update(kwargs)

        url = f"{self.base_url}/chat/completions"
        accumulated_content = []
        accumulated_reasoning = []
        tool_calls_map: Dict[int, Dict[str, Any]] = {}
        finish_reason = "stop"

        with httpx.Client(timeout=90.0) as client:
            with client.stream("POST", url, headers=self._headers(), json=payload) as resp:
                resp.raise_for_status()
                for line in resp.iter_lines():
                    if not line or not line.startswith("data: "):
                        continue
                    data_str = line[6:].strip()
                    if data_str == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data_str)
                    except json.JSONDecodeError:
                        continue

                    choices = chunk.get("choices", [])
                    if not choices:
                        continue
                    delta = choices[0].get("delta", {})
                    finish = choices[0].get("finish_reason")
                    if finish:
                        finish_reason = finish

                    # Streaming content
                    token = delta.get("content")
                    if token:
                        accumulated_content.append(token)
                        yield {"type": "content", "token": token}

                    # Streaming reasoning
                    reasoning_token = delta.get("reasoning_content")
                    if reasoning_token:
                        accumulated_reasoning.append(reasoning_token)
                        yield {"type": "reasoning", "token": reasoning_token}

                    # Streaming tool calls
                    if "tool_calls" in delta and delta["tool_calls"]:
                        for tc_chunk in delta["tool_calls"]:
                            idx = tc_chunk.get("index", 0)
                            if idx not in tool_calls_map:
                                tool_calls_map[idx] = {
                                    "id": tc_chunk.get("id", ""),
                                    "name": tc_chunk.get("function", {}).get("name", ""),
                                    "arguments": "",
                                }
                            if tc_chunk.get("id"):
                                tool_calls_map[idx]["id"] = tc_chunk["id"]
                            fn = tc_chunk.get("function", {})
                            if fn.get("name"):
                                tool_calls_map[idx]["name"] = fn["name"]
                            if fn.get("arguments"):
                                tool_calls_map[idx]["arguments"] += fn["arguments"]

        # Parse collected tool calls
        final_tool_calls = []
        for idx in sorted(tool_calls_map.keys()):
            tc_data = tool_calls_map[idx]
            try:
                args = json.loads(tc_data["arguments"])
            except Exception:
                args = {"raw": tc_data["arguments"]}
            final_tool_calls.append(
                ToolCall(id=tc_data["id"] or f"call_{idx}", name=tc_data["name"], arguments=args)
            )

        full_content = "".join(accumulated_content)
        full_reasoning = "".join(accumulated_reasoning) or None

        return ChatResponse(
            content=full_content,
            tool_calls=final_tool_calls,
            finish_reason=finish_reason,
            reasoning_content=full_reasoning,
        )

    def list_models(self) -> List[str]:
        url = f"{self.base_url}/models"
        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.get(url, headers=self._headers())
                if resp.status_code == 200:
                    data = resp.json()
                    return [m["id"] for m in data.get("data", [])]
        except Exception:
            pass
        return [self.default_model]

    def test_connection(self) -> bool:
        if not self.api_key and "localhost" not in self.base_url and "127.0.0.1" not in self.base_url:
            return False
        try:
            models = self.list_models()
            return len(models) > 0
        except Exception:
            return False
