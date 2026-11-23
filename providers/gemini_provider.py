"""
Google Gemini Provider for FireBox.
Supports Gemini 2.0 Flash, Gemini 2.0 Pro, Gemini 1.5 Pro with large context windows.
"""

import json
from typing import List, Dict, Any, Optional, Generator
import httpx

from firebox.providers.base import BaseProvider, ChatMessage, ChatResponse, ToolCall


class GeminiProvider(BaseProvider):
    """Google Gemini API Provider using Gemini REST/SDK endpoints."""

    def __init__(
        self,
        name: str = "Google Gemini",
        api_key: Optional[str] = None,
        base_url: Optional[str] = "https://generativelanguage.googleapis.com/v1beta",
        default_model: str = "gemini-2.0-flash",
    ):
        super().__init__(name=name, api_key=api_key, base_url=base_url.rstrip("/"), default_model=default_model)

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
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not configured.")

        # Convert chat messages to Gemini contents structure
        contents = []
        system_instruction = None

        for m in messages:
            if m.role == "system":
                system_instruction = {"parts": [{"text": m.content}]}
            elif m.role == "tool":
                contents.append({
                    "role": "function",
                    "parts": [{"functionResponse": {"name": m.name or "tool", "response": {"result": m.content}}}],
                })
            else:
                role = "user" if m.role == "user" else "model"
                contents.append({"role": role, "parts": [{"text": m.content}]})

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens or 4096,
            },
        }
        if system_instruction:
            payload["systemInstruction"] = system_instruction

        url = f"{self.base_url}/models/{model}:generateContent?key={self.api_key}"
        with httpx.Client(timeout=90.0) as client:
            resp = client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()

        text_content = ""
        candidates = data.get("candidates", [])
        if candidates:
            parts = candidates[0].get("content", {}).get("parts", [])
            for p in parts:
                if "text" in p:
                    text_content += p["text"]

        return ChatResponse(
            content=text_content,
            finish_reason=candidates[0].get("finishReason", "STOP") if candidates else "STOP",
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
        if res.content:
            yield {"type": "content", "token": res.content}
        return res

    def list_models(self) -> List[str]:
        return ["gemini-2.0-flash", "gemini-2.0-pro-exp-02-05", "gemini-1.5-pro", "gemini-1.5-flash"]

    def test_connection(self) -> bool:
        if not self.api_key:
            return False
        try:
            return len(self.list_models()) > 0
        except Exception:
            return False
