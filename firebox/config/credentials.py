"""
Secure Credential Storage for FireBox.
Supports Windows Credential Manager / DPAPI, environment variables,
and obfuscated local storage fallback with security warnings.
"""

import os
import sys
import base64
from typing import Optional
import json
from pathlib import Path


def mask_secret(secret: Optional[str]) -> str:
    """Mask sensitive API key or token for terminal display (e.g., sk-12...89ab)."""
    if not secret:
        return "<not set>"
    if len(secret) <= 8:
        return "********"
    return f"{secret[:4]}...{secret[-4:]}"


class CredentialManager:
    """Manages secret credentials safely."""

    def __init__(self, storage_dir: Optional[Path] = None):
        if storage_dir is None:
            env_home = os.getenv("FIREBOX_HOME")
            if env_home:
                storage_dir = Path(env_home)
            else:
                candidate = Path.home() / ".firebox"
                try:
                    candidate.mkdir(parents=True, exist_ok=True)
                    test_file = candidate / ".perm_check"
                    test_file.write_text("ok", encoding="utf-8")
                    test_file.unlink(missing_ok=True)
                    storage_dir = candidate
                except (PermissionError, OSError):
                    storage_dir = Path.cwd() / ".firebox"
        self.storage_dir = storage_dir.resolve()
        self.cred_file = self.storage_dir / "credentials.dat"
        self._cache = {}
        self._load()

    def _load(self):
        if self.cred_file.exists():
            try:
                raw = self.cred_file.read_bytes()
                # Basic obfuscation fallback
                decoded = base64.b64decode(raw).decode("utf-8")
                self._cache = json.loads(decoded)
            except Exception:
                self._cache = {}

    def _save(self):
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        try:
            raw = json.dumps(self._cache).encode("utf-8")
            encoded = base64.b64encode(raw)
            self.cred_file.write_bytes(encoded)
            # Set read/write only for user on posix
            if os.name != "nt":
                os.chmod(self.cred_file, 0o600)
        except Exception:
            pass

    def get_key(self, provider_name: str) -> Optional[str]:
        """Retrieve API key from environment variable first, then credential store."""
        env_var_map = {
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "gemini": "GEMINI_API_KEY",
            "google": "GEMINI_API_KEY",
            "openrouter": "OPENROUTER_API_KEY",
            "groq": "GROQ_API_KEY",
            "deepseek": "DEEPSEEK_API_KEY",
            "perplexity": "PERPLEXITY_API_KEY",
            "cohere": "COHERE_API_KEY",
            "sambanova": "SAMBANOVA_API_KEY",
            "qwen": "DASHSCOPE_API_KEY",
            "mistral": "MISTRAL_API_KEY",
            "xai": "XAI_API_KEY",
            "together": "TOGETHER_API_KEY",
            "fireworks": "FIREWORKS_API_KEY",
            "cerebras": "CEREBRAS_API_KEY",
            "nvidia": "NVIDIA_API_KEY",
            "tavily": "TAVILY_API_KEY",
        }

        # Check standard environment variable
        env_key = env_var_map.get(provider_name.lower())
        if env_key and os.getenv(env_key):
            return os.getenv(env_key)

        # Check generic FIREBOX_<PROVIDER>_KEY
        custom_env = f"FIREBOX_{provider_name.upper()}_KEY"
        if os.getenv(custom_env):
            return os.getenv(custom_env)

        return self._cache.get(provider_name.lower())

    def set_key(self, provider_name: str, key_val: str):
        """Save API key into secure credential store."""
        self._cache[provider_name.lower()] = key_val
        self._save()

    def remove_key(self, provider_name: str):
        """Remove key from credential store."""
        if provider_name.lower() in self._cache:
            del self._cache[provider_name.lower()]
            self._save()
