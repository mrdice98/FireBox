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

        # 7. Perplexity AI (New!)
        perplexity_key = creds.get_key("perplexity")
        self._instances["perplexity"] = OpenAICompatibleProvider(
            name="Perplexity AI",
            api_key=perplexity_key,
            base_url="https://api.perplexity.ai",
            default_model="sonar-pro",
        )

        # 8. Cohere (New!)
        cohere_key = creds.get_key("cohere")
        self._instances["cohere"] = OpenAICompatibleProvider(
            name="Cohere",
            api_key=cohere_key,
            base_url="https://api.cohere.ai/v1",
            default_model="command-r-plus",
        )

        # 9. SambaNova Cloud (New!)
        sambanova_key = creds.get_key("sambanova")
        self._instances["sambanova"] = OpenAICompatibleProvider(
            name="SambaNova Systems",
            api_key=sambanova_key,
            base_url="https://api.sambanova.ai/v1",
            default_model="Meta-Llama-3.3-70B-Instruct",
        )

        # 10. Alibaba Cloud Qwen (New!)
        qwen_key = creds.get_key("qwen")
        self._instances["qwen"] = OpenAICompatibleProvider(
            name="Alibaba Cloud Qwen",
            api_key=qwen_key,
            base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
            default_model="qwen-plus",
        )

        # 11. Mistral
        mistral_key = creds.get_key("mistral")
        self._instances["mistral"] = OpenAICompatibleProvider(
            name="Mistral",
            api_key=mistral_key,
            base_url="https://api.mistral.ai/v1",
            default_model="mistral-large-latest",
        )

        # 12. xAI (Grok)
        xai_key = creds.get_key("xai")
        self._instances["xai"] = OpenAICompatibleProvider(
            name="xAI",
            api_key=xai_key,
            base_url="https://api.x.ai/v1",
            default_model="grok-2-latest",
        )

        # 13. Together AI
        together_key = creds.get_key("together")
        self._instances["together"] = OpenAICompatibleProvider(
            name="Together AI",
            api_key=together_key,
            base_url="https://api.together.xyz/v1",
            default_model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
        )

        # 14. Fireworks AI
        fireworks_key = creds.get_key("fireworks")
        self._instances["fireworks"] = OpenAICompatibleProvider(
            name="Fireworks AI",
            api_key=fireworks_key,
            base_url="https://api.fireworks.ai/inference/v1",
            default_model="accounts/fireworks/models/llama-v3p3-70b-instruct",
        )

        # 15. Cerebras
        cerebras_key = creds.get_key("cerebras")
        self._instances["cerebras"] = OpenAICompatibleProvider(
            name="Cerebras",
            api_key=cerebras_key,
            base_url="https://api.cerebras.ai/v1",
            default_model="llama3.1-70b",
        )

        # 16. NVIDIA NIM
        nvidia_key = creds.get_key("nvidia")
        self._instances["nvidia"] = OpenAICompatibleProvider(
            name="NVIDIA NIM",
            api_key=nvidia_key,
            base_url="https://integrate.api.nvidia.com/v1",
            default_model="meta/llama-3.3-70b-instruct",
        )

        # 17. Ollama (Local)
        self._instances["ollama"] = OpenAICompatibleProvider(
            name="Ollama (Local)",
            api_key=None,
            base_url="http://localhost:11434/v1",
            default_model="llama3.1:latest",
        )

        # 18. LM Studio (Local)
        self._instances["lmstudio"] = OpenAICompatibleProvider(
            name="LM Studio (Local)",
            api_key=None,
            base_url="http://localhost:1234/v1",
            default_model="local-model",
        )

        # 19. Mock/Offline Simulator
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

    @classmethod
    def get_catalog(cls) -> List[Dict[str, Any]]:
        """Return the official numbered provider catalog."""
        return PROVIDER_CATALOG

    @classmethod
    def resolve_provider_choice(cls, user_input: str) -> Optional[str]:
        """Resolve a user selection (either by index number or provider name/id) to a valid provider ID."""
        clean = user_input.strip()
        if not clean:
            return None

        # Check by numeric index (e.g. "1", "3", "7")
        if clean.isdigit():
            idx = int(clean)
            for item in PROVIDER_CATALOG:
                if item["index"] == idx:
                    return item["id"]

        # Check by ID or Name
        clean_lower = clean.lower()
        for item in PROVIDER_CATALOG:
            if item["id"].lower() == clean_lower or item["name"].lower() == clean_lower:
                return item["id"]

        return clean_lower


PROVIDER_CATALOG = [
    {"index": 1, "id": "openai", "name": "OpenAI", "models": "gpt-4o, o1, o3-mini", "default_model": "gpt-4o", "requires_key": True},
    {"index": 2, "id": "anthropic", "name": "Anthropic", "models": "claude-3-7-sonnet, claude-3-5-sonnet", "default_model": "claude-3-7-sonnet-20250219", "requires_key": True},
    {"index": 3, "id": "gemini", "name": "Google Gemini", "models": "gemini-2.0-flash, gemini-2.0-pro", "default_model": "gemini-2.0-flash", "requires_key": True},
    {"index": 4, "id": "deepseek", "name": "DeepSeek", "models": "deepseek-chat (V3), deepseek-reasoner (R1)", "default_model": "deepseek-chat", "requires_key": True},
    {"index": 5, "id": "groq", "name": "Groq LPU", "models": "llama-3.3-70b-versatile, deepseek-r1-distill", "default_model": "llama-3.3-70b-versatile", "requires_key": True},
    {"index": 6, "id": "openrouter", "name": "OpenRouter", "models": "Universal multi-model gateway", "default_model": "anthropic/claude-3.7-sonnet", "requires_key": True},
    {"index": 7, "id": "perplexity", "name": "Perplexity AI", "models": "sonar-pro, sonar, sonar-reasoning", "default_model": "sonar-pro", "requires_key": True},
    {"index": 8, "id": "cohere", "name": "Cohere", "models": "command-r-plus, command-r", "default_model": "command-r-plus", "requires_key": True},
    {"index": 9, "id": "sambanova", "name": "SambaNova Systems", "models": "Meta-Llama-3.3-70B, Qwen2.5-Coder", "default_model": "Meta-Llama-3.3-70B-Instruct", "requires_key": True},
    {"index": 10, "id": "qwen", "name": "Alibaba Cloud Qwen", "models": "qwen-plus, qwen-max, qwen2.5-coder", "default_model": "qwen-plus", "requires_key": True},
    {"index": 11, "id": "mistral", "name": "Mistral AI", "models": "mistral-large-latest, codestral", "default_model": "mistral-large-latest", "requires_key": True},
    {"index": 12, "id": "xai", "name": "xAI (Grok)", "models": "grok-2-latest", "default_model": "grok-2-latest", "requires_key": True},
    {"index": 13, "id": "together", "name": "Together AI", "models": "meta-llama/Llama-3.3-70B, Qwen 2.5 Coder", "default_model": "meta-llama/Llama-3.3-70B-Instruct-Turbo", "requires_key": True},
    {"index": 14, "id": "fireworks", "name": "Fireworks AI", "models": "llama-v3p3-70b-instruct", "default_model": "accounts/fireworks/models/llama-v3p3-70b-instruct", "requires_key": True},
    {"index": 15, "id": "cerebras", "name": "Cerebras", "models": "llama3.1-70b ultra-speed", "default_model": "llama3.1-70b", "requires_key": True},
    {"index": 16, "id": "nvidia", "name": "NVIDIA NIM", "models": "meta/llama-3.3-70b-instruct", "default_model": "meta/llama-3.3-70b-instruct", "requires_key": True},
    {"index": 17, "id": "ollama", "name": "Ollama (Local)", "models": "Local offline models (e.g. llama3.1)", "default_model": "llama3.1:latest", "requires_key": False},
    {"index": 18, "id": "lmstudio", "name": "LM Studio (Local)", "models": "Local desktop models (port 1234)", "default_model": "local-model", "requires_key": False},
    {"index": 19, "id": "mock", "name": "Mock/Offline Simulator", "models": "firebox-sim-1.0 (Testing)", "default_model": "firebox-sim-1.0", "requires_key": False},
]


_provider_registry = None


def get_provider_registry() -> ProviderRegistry:
    global _provider_registry
    if _provider_registry is None:
        _provider_registry = ProviderRegistry()
    return _provider_registry
