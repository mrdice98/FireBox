"""
Configuration Schemas for FireBox.
Pydantic models defining providers, models, permissions, and app settings.
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
import enum


class AnimationMode(str, enum.Enum):
    CINEMATIC = "cinematic"
    MINIMAL = "minimal"
    NONE = "none"


class SafetyLevel(str, enum.Enum):
    STRICT = "STRICT"         # Prompt on all modifications, external commands, deletions
    BALANCED = "BALANCED"     # Prompt on deletions, shell commands, git pushes, outside workspace
    AUTONOMOUS = "AUTONOMOUS" # Prompt only on destructive/irreversible system actions


class ModelProfile(BaseModel):
    id: str
    name: str
    provider: str
    context_window: int = 128000
    supports_tools: bool = True
    supports_vision: bool = True
    supports_reasoning: bool = False
    is_default: bool = False
    extra_params: Dict[str, Any] = Field(default_factory=dict)


class ProviderConfig(BaseModel):
    name: str
    provider_type: str        # openai, anthropic, gemini, openrouter, groq, deepseek, ollama, custom, etc.
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    organization: Optional[str] = None
    enabled: bool = True
    default_model: str = "gpt-4o"
    models: List[ModelProfile] = Field(default_factory=list)


class PermissionsConfig(BaseModel):
    safety_level: SafetyLevel = SafetyLevel.BALANCED
    workspace_only: bool = True
    allow_shell_commands: bool = False
    allow_file_deletions: bool = False
    allow_git_push: bool = False
    allow_env_modifications: bool = False
    blocked_commands: List[str] = Field(default_factory=lambda: [
        "rmdir /s /q c:\\", "format", "del /f /s /q c:\\", "rm -rf /",
        "mkfs", "dd if=", ":(){ :|:& };:"
    ])
    whitelisted_commands: List[str] = Field(default_factory=lambda: [
        "git status", "git diff", "git log", "npm test", "pytest", "cargo test",
        "python -m pytest", "npm run build", "go test"
    ])


class AppConfig(BaseModel):
    version: str = "1.0.0"
    active_provider: str = "openai"
    active_model: str = "gpt-4o"
    animation_mode: AnimationMode = AnimationMode.CINEMATIC
    theme: str = "fire"
    max_agent_iterations: int = 30
    auto_compact_context: bool = True
    context_token_limit: int = 100000
    audit_logging: bool = True
    telemetry_enabled: bool = False
