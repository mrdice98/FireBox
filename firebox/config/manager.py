"""
Configuration Manager for FireBox.
Manages global configuration (~/.firebox/) and local project configurations.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

from firebox.config.schemas import (
    AppConfig,
    ProviderConfig,
    PermissionsConfig,
    ModelProfile,
    AnimationMode,
    SafetyLevel,
)
from firebox.config.credentials import CredentialManager


class ConfigManager:
    """Handles persistent configuration and directories for FireBox."""

    def __init__(self, base_dir: Optional[Path] = None):
        if base_dir is None:
            env_home = os.getenv("FIREBOX_HOME")
            if env_home:
                base_dir = Path(env_home)
            else:
                candidate = Path.home() / ".firebox"
                try:
                    candidate.mkdir(parents=True, exist_ok=True)
                    base_dir = candidate
                except (PermissionError, OSError):
                    base_dir = Path.cwd() / ".firebox"

        self.base_dir = base_dir.resolve()

        # Standard subdirectories
        self.sessions_dir = self.base_dir / "sessions"
        self.projects_dir = self.base_dir / "projects"
        self.plugins_dir = self.base_dir / "plugins"
        self.tools_dir = self.base_dir / "tools"
        self.logs_dir = self.base_dir / "logs"
        self.cache_dir = self.base_dir / "cache"
        self.memory_dir = self.base_dir / "memory"
        self.backups_dir = self.base_dir / "backups"

        # Config files
        self.config_file = self.base_dir / "config.json"
        self.providers_file = self.base_dir / "providers.json"
        self.permissions_file = self.base_dir / "permissions.json"

        self.credentials = CredentialManager(self.base_dir)

        self.app_config: AppConfig = AppConfig()
        self.providers: Dict[str, ProviderConfig] = {}
        self.permissions: PermissionsConfig = PermissionsConfig()

        self._ensure_directories()
        self.load()

    def _ensure_directories(self):
        """Create all required configuration subdirectories."""
        for d in [
            self.base_dir,
            self.sessions_dir,
            self.projects_dir,
            self.plugins_dir,
            self.tools_dir,
            self.logs_dir,
            self.cache_dir,
            self.memory_dir,
            self.backups_dir,
        ]:
            d.mkdir(parents=True, exist_ok=True)

    def load(self):
        """Load configuration files or initialize defaults."""
        # 1. App Config
        if self.config_file.exists():
            try:
                data = json.loads(self.config_file.read_text(encoding="utf-8"))
                self.app_config = AppConfig(**data)
            except Exception:
                self.app_config = AppConfig()
        else:
            self.save_app_config()

        # 2. Permissions
        if self.permissions_file.exists():
            try:
                data = json.loads(self.permissions_file.read_text(encoding="utf-8"))
                self.permissions = PermissionsConfig(**data)
            except Exception:
                self.permissions = PermissionsConfig()
        else:
            self.save_permissions()

        # 3. Providers
        if self.providers_file.exists():
            try:
                data = json.loads(self.providers_file.read_text(encoding="utf-8"))
                self.providers = {k: ProviderConfig(**v) for k, v in data.items()}
            except Exception:
                self._load_default_providers()
        else:
            self._load_default_providers()
            self.save_providers()

    def _load_default_providers(self):
        """Populate rich default providers."""
        self.providers = {
            "openai": ProviderConfig(
                name="OpenAI",
                provider_type="openai",
                default_model="gpt-4o",
                models=[
                    ModelProfile(id="gpt-4o", name="GPT-4o (Omni)", provider="openai", context_window=128000, is_default=True),
                    ModelProfile(id="gpt-4o-mini", name="GPT-4o Mini", provider="openai", context_window=128000),
                    ModelProfile(id="o1", name="o1 (Reasoning)", provider="openai", context_window=200000, supports_reasoning=True),
                    ModelProfile(id="o3-mini", name="o3-mini (High-speed Reasoning)", provider="openai", context_window=200000, supports_reasoning=True),
                ],
            ),
            "anthropic": ProviderConfig(
                name="Anthropic",
                provider_type="anthropic",
                default_model="claude-3-7-sonnet",
                models=[
                    ModelProfile(id="claude-3-7-sonnet", name="Claude 3.7 Sonnet (Hybrid Reasoning)", provider="anthropic", context_window=200000, supports_reasoning=True, is_default=True),
                    ModelProfile(id="claude-3-5-sonnet", name="Claude 3.5 Sonnet", provider="anthropic", context_window=200000),
                    ModelProfile(id="claude-3-5-haiku", name="Claude 3.5 Haiku", provider="anthropic", context_window=200000),
                ],
            ),
            "gemini": ProviderConfig(
                name="Google Gemini",
                provider_type="gemini",
                default_model="gemini-2.0-flash",
                models=[
                    ModelProfile(id="gemini-2.0-flash", name="Gemini 2.0 Flash", provider="gemini", context_window=1000000, is_default=True),
                    ModelProfile(id="gemini-2.0-pro-exp-02-05", name="Gemini 2.0 Pro", provider="gemini", context_window=2000000),
                    ModelProfile(id="gemini-1.5-pro", name="Gemini 1.5 Pro", provider="gemini", context_window=2000000),
                ],
            ),
            "openrouter": ProviderConfig(
                name="OpenRouter",
                provider_type="openrouter",
                base_url="https://openrouter.ai/api/v1",
                default_model="anthropic/claude-3.7-sonnet",
                models=[
                    ModelProfile(id="anthropic/claude-3.7-sonnet", name="Claude 3.7 Sonnet (OpenRouter)", provider="openrouter", context_window=200000, is_default=True),
                    ModelProfile(id="openai/gpt-4o", name="GPT-4o (OpenRouter)", provider="openrouter", context_window=128000),
                    ModelProfile(id="deepseek/deepseek-r1", name="DeepSeek R1 (OpenRouter)", provider="openrouter", context_window=128000, supports_reasoning=True),
                ],
            ),
            "groq": ProviderConfig(
                name="Groq",
                provider_type="groq",
                base_url="https://api.groq.com/openai/v1",
                default_model="llama-3.3-70b-versatile",
                models=[
                    ModelProfile(id="llama-3.3-70b-versatile", name="Llama 3.3 70B (Groq LPU)", provider="groq", context_window=128000, is_default=True),
                    ModelProfile(id="deepseek-r1-distill-llama-70b", name="DeepSeek R1 Distill 70B", provider="groq", context_window=128000, supports_reasoning=True),
                ],
            ),
            "deepseek": ProviderConfig(
                name="DeepSeek",
                provider_type="deepseek",
                base_url="https://api.deepseek.com",
                default_model="deepseek-chat",
                models=[
                    ModelProfile(id="deepseek-chat", name="DeepSeek V3", provider="deepseek", context_window=64000, is_default=True),
                    ModelProfile(id="deepseek-reasoner", name="DeepSeek R1", provider="deepseek", context_window=64000, supports_reasoning=True),
                ],
            ),
            "ollama": ProviderConfig(
                name="Ollama (Local)",
                provider_type="ollama",
                base_url="http://localhost:11434/v1",
                default_model="llama3.1:latest",
                models=[
                    ModelProfile(id="llama3.1:latest", name="Llama 3.1 (Local)", provider="ollama", context_window=32768, is_default=True),
                    ModelProfile(id="qwen2.5-coder:latest", name="Qwen 2.5 Coder (Local)", provider="ollama", context_window=32768),
                    ModelProfile(id="deepseek-r1:latest", name="DeepSeek R1 (Local)", provider="ollama", context_window=32768, supports_reasoning=True),
                ],
            ),
            "lmstudio": ProviderConfig(
                name="LM Studio (Local)",
                provider_type="lmstudio",
                base_url="http://localhost:1234/v1",
                default_model="local-model",
                models=[
                    ModelProfile(id="local-model", name="Loaded Model (LM Studio)", provider="lmstudio", context_window=32768, is_default=True),
                ],
            ),
        }

    def save_app_config(self):
        """Persist app configuration."""
        self.config_file.write_text(
            json.dumps(self.app_config.model_dump(), indent=2), encoding="utf-8"
        )

    def save_providers(self):
        """Persist providers configuration."""
        dump = {k: v.model_dump() for k, v in self.providers.items()}
        self.providers_file.write_text(json.dumps(dump, indent=2), encoding="utf-8")

    def save_permissions(self):
        """Persist permissions configuration."""
        self.permissions_file.write_text(
            json.dumps(self.permissions.model_dump(), indent=2), encoding="utf-8"
        )

    def reset_to_defaults(self):
        """Reset all configuration to fresh defaults."""
        self.app_config = AppConfig()
        self.permissions = PermissionsConfig()
        self._load_default_providers()
        self.save_app_config()
        self.save_providers()
        self.save_permissions()


_global_config_instance = None


def get_config() -> ConfigManager:
    """Return singleton ConfigManager."""
    global _global_config_instance
    if _global_config_instance is None:
        _global_config_instance = ConfigManager()
    return _global_config_instance
