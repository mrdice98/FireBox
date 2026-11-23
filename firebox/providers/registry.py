"""
Provider Registry for FireBox.
Manages provider instantiation, API key injection, model switching,
and connectivity checks across 15+ AI providers.
"""

from typing import Dict, List, Optional, Type
from rich.table import Table
from rich.box import ROUNDED

from firebox.providers.base import BaseProvider
from firebox.providers.openai_provider import OpenAICompatibleProvider
from firebox.providers.anthropic_provider import AnthropicProvider
from firebox.providers.gemini_provider import GeminiProvider
from firebox.providers.mock_provider import MockProvider
from firebox.config.manager import get_config
from firebox.config.credentials import mask_secret
from firebox.ui.theme import COLOR_FIRE_FLAME, COLOR_FIRE_GOLD, COLOR_SUCCESS, COLOR_ERROR


class ProviderRegistry:
    """Central registry of all AI model providers."""

    def __init__(self):
        self.config_mgr = get_config()
        self._instances: Dict[str, BaseProvider] = {}
        self._init_providers()

    def _init_providers(self):
        """Instantiate providers from configuration and credentials."""
        creds = self.config_mgr.credentials

        # 1. OpenAI
        openai_key = creds.get_key("openai")
        self._instances["openai"] = OpenAICompatibleProvider(
            name="OpenAI",
            api_key=openai_key,
            base_url="https://api.openai.com/v1",
            default_model="gpt-4o",
        )

        # 2. Anthropic
        anthropic_key = creds.get_key("anthropic")
        self._instances["anthropic"] = AnthropicProvider(
            name="Anthropic",
            api_key=anthropic_key,
            default_model="claude-3-7-sonnet-20250219",
        )

        # 3. Gemini
        gemini_key = creds.get_key("gemini")
        self._instances["gemini"] = GeminiProvider(
            name="Google Gemini",
            api_key=gemini_key,
            default_model="gemini-2.0-flash",
        )

        # 4. OpenRouter
        openrouter_key = creds.get_key("openrouter")
        self._instances["openrouter"] = OpenAICompatibleProvider(
            name="OpenRouter",
            api_key=openrouter_key,
            base_url="https://openrouter.ai/api/v1",
            default_model="anthropic/claude-3.7-sonnet",
        )

        # 5. Groq
        groq_key = creds.get_key("groq")
        self._instances["groq"] = OpenAICompatibleProvider(
            name="Groq",
            api_key=groq_key,
            base_url="https://api.groq.com/openai/v1",
            default_model="llama-3.3-70b-versatile",
        )

        # 6. DeepSeek
        deepseek_key = creds.get_key("deepseek")
        self._instances["deepseek"] = OpenAICompatibleProvider(
            name="DeepSeek",
            api_key=deepseek_key,
            base_url="https://api.deepseek.com",
            default_model="deepseek-chat",
        )

        # 7. Mistral
        mistral_key = creds.get_key("mistral")
        self._instances["mistral"] = OpenAICompatibleProvider(
            name="Mistral",
            api_key=mistral_key,
            base_url="https://api.mistral.ai/v1",
            default_model="mistral-large-latest",
        )

        # 8. xAI (Grok)
        xai_key = creds.get_key("xai")
        self._instances["xai"] = OpenAICompatibleProvider(
            name="xAI",
            api_key=xai_key,
            base_url="https://api.x.ai/v1",
            default_model="grok-2-latest",
        )

        # 9. Together AI
        together_key = creds.get_key("together")
        self._instances["together"] = OpenAICompatibleProvider(
            name="Together AI",
            api_key=together_key,
            base_url="https://api.together.xyz/v1",
            default_model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
        )

        # 10. Fireworks AI
        fireworks_key = creds.get_key("fireworks")
        self._instances["fireworks"] = OpenAICompatibleProvider(
            name="Fireworks AI",
            api_key=fireworks_key,
            base_url="https://api.fireworks.ai/inference/v1",
            default_model="accounts/fireworks/models/llama-v3p3-70b-instruct",
        )

        # 11. Cerebras
        cerebras_key = creds.get_key("cerebras")
        self._instances["cerebras"] = OpenAICompatibleProvider(
            name="Cerebras",
            api_key=cerebras_key,
            base_url="https://api.cerebras.ai/v1",
            default_model="llama3.1-70b",
        )

        # 12. NVIDIA NIM
        nvidia_key = creds.get_key("nvidia")
        self._instances["nvidia"] = OpenAICompatibleProvider(
            name="NVIDIA NIM",
            api_key=nvidia_key,
            base_url="https://integrate.api.nvidia.com/v1",
            default_model="meta/llama-3.3-70b-instruct",
        )

        # 13. Ollama (Local)
        self._instances["ollama"] = OpenAICompatibleProvider(
            name="Ollama (Local)",
            api_key=None,
            base_url="http://localhost:11434/v1",
            default_model="llama3.1:latest",
        )

        # 14. LM Studio (Local)
        self._instances["lmstudio"] = OpenAICompatibleProvider(
            name="LM Studio (Local)",
            api_key=None,
            base_url="http://localhost:1234/v1",
            default_model="local-model",
        )

        # 15. Mock/Offline Simulator
        self._instances["mock"] = MockProvider()

    def get_provider(self, name: Optional[str] = None) -> BaseProvider:
        """Get provider instance by name, or return active provider."""
        if not name:
            name = self.config_mgr.app_config.active_provider
        name = name.lower()
        if name in self._instances:
            return self._instances[name]
        # Fallback to mock if requested
        if name in ("mock", "test", "sim"):
            return self._instances["mock"]
        # Return first available or fallback to mock
        return self._instances.get("openai", self._instances["mock"])

    def set_active_provider(self, name: str, model: Optional[str] = None):
        """Set active provider and optionally active model."""
        name = name.lower()
        if name not in self._instances:
            raise ValueError(f"Unknown provider: {name}")
        self.config_mgr.app_config.active_provider = name
        if model:
            self.config_mgr.app_config.active_model = model
        else:
            self.config_mgr.app_config.active_model = self._instances[name].default_model
        self.config_mgr.save_app_config()

    def set_active_model(self, model: str):
        """Set active model for current provider."""
        self.config_mgr.app_config.active_model = model
        self.config_mgr.save_app_config()

    def list_all_providers(self) -> List[Dict[str, Any]]:
        """Return status information for all providers."""
        creds = self.config_mgr.credentials
        result = []
        for key, prov in self._instances.items():
            has_key = bool(prov.api_key) or key in ("ollama", "lmstudio", "mock")
            result.append({
                "id": key,
                "name": prov.name,
                "default_model": prov.default_model,
                "configured": has_key,
                "api_key_masked": mask_secret(prov.api_key),
                "is_active": (key == self.config_mgr.app_config.active_provider),
            })
        return result


_provider_registry = None


def get_provider_registry() -> ProviderRegistry:
    global _provider_registry
    if _provider_registry is None:
        _provider_registry = ProviderRegistry()
    return _provider_registry
