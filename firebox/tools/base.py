"""
Base Tool Interface for FireBox.
Schema definitions, execution protocol, and result packaging.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class ToolResult(BaseModel):
    """Result of a tool execution."""
    output: str
    success: bool = True
    error: Optional[str] = None
    artifacts: Dict[str, Any] = Field(default_factory=dict)
    duration_ms: float = 0.0


class BaseTool(ABC):
    """Abstract base class for all FireBox tools."""

    name: str = ""
    description: str = ""
    category: str = "general"
    is_destructive: bool = False
    requires_permission: bool = False

    @abstractmethod
    def get_parameters_schema(self) -> Dict[str, Any]:
        """Return OpenAI-compatible JSON Schema for parameters."""
        pass

    @abstractmethod
    def run(self, **kwargs) -> ToolResult:
        """Execute the tool logic."""
        pass

    def to_openai_schema(self) -> Dict[str, Any]:
        """Convert tool to OpenAI function calling format."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.get_parameters_schema(),
            },
        }
