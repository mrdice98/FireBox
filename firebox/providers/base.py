"""
Base AI Provider Interface for FireBox.
Unified protocol for multi-provider streaming, tool calling, and reasoning.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, AsyncGenerator, Generator
from pydantic import BaseModel, Field
import json


class ToolCall(BaseModel):
    id: str
    name: str
    arguments: Dict[str, Any]


class ChatMessage(BaseModel):
    role: str               # "system", "user", "assistant", "tool"
    content: str
    name: Optional[str] = None
    tool_call_id: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None
    reasoning_content: Optional[str] = None


class ChatResponse(BaseModel):
    content: str = ""
    tool_calls: List[ToolCall] = Field(default_factory=list)
    finish_reason: str = "stop"
    reasoning_content: Optional[str] = None
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class BaseProvider(ABC):
    """Abstract Base Class for AI Providers."""

    def __init__(
        self,
        name: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        default_model: str = "default",
    ):
        self.name = name
        self.api_key = api_key
        self.base_url = base_url
        self.default_model = default_model

    @abstractmethod
    def chat_complete(
        self,
        messages: List[ChatMessage],
        tools: Optional[List[Dict[str, Any]]] = None,
        model: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: Optional[int] = 4096,
        **kwargs,
    ) -> ChatResponse:
        """Execute a non-streaming chat completion."""
        pass

    @abstractmethod
    def stream_chat(
        self,
        messages: List[ChatMessage],
        tools: Optional[List[Dict[str, Any]]] = None,
        model: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: Optional[int] = 4096,
        **kwargs,
    ) -> Generator[Dict[str, Any], None, ChatResponse]:
        """Stream response tokens and tool calls. Yields chunks, returns final ChatResponse."""
        pass

    @abstractmethod
    def list_models(self) -> List[str]:
        """List available models for this provider."""
        pass

    @abstractmethod
    def test_connection(self) -> bool:
        """Validate credentials and endpoint connectivity."""
        pass

    def supports_tools(self) -> bool:
        """Whether this provider supports function/tool calling."""
        return True

    def supports_reasoning(self) -> bool:
        """Whether this provider supports extended reasoning tokens."""
        return False
