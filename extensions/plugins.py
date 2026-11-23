"""
Plugin & Extension Architecture for FireBox.
Discovers and loads third-party plugins, custom tools, and lifecycles.
"""

import os
import sys
import json
import importlib.util
from pathlib import Path
from typing import Dict, List, Any, Optional

from firebox.tools.base import BaseTool
from firebox.tools.registry import get_tool_registry
from firebox.config.manager import get_config


class PluginManager:
    """Discovers, loads, and registers external FireBox plugins."""

    def __init__(self, plugins_dir: Optional[Path] = None):
        if plugins_dir is None:
            config_mgr = get_config()
            plugins_dir = config_mgr.plugins_dir
        self.plugins_dir = plugins_dir
        self.plugins_dir.mkdir(parents=True, exist_ok=True)
        self.loaded_plugins: Dict[str, Dict[str, Any]] = {}

    def discover_and_load_all(self):
        """Scan plugins directory for plugins and register them."""
        tool_reg = get_tool_registry()

        # Iterate through subdirectories
        for p in self.plugins_dir.iterdir():
            if p.is_dir():
                manifest = p / "plugin.json"
                entry_py = p / "plugin.py"

                meta = {
                    "id": p.name,
                    "name": p.name,
                    "version": "1.0.0",
                    "description": "",
                    "tools": [],
                }

                if manifest.exists():
                    try:
                        meta.update(json.loads(manifest.read_text(encoding="utf-8")))
                    except Exception:
                        pass

                if entry_py.exists():
                    try:
                        spec = importlib.util.spec_from_file_location(f"firebox_plugin_{p.name}", str(entry_py))
                        if spec and spec.loader:
                            mod = importlib.util.module_from_spec(spec)
                            spec.loader.exec_module(mod)
                            # Register tools if defined
                            if hasattr(mod, "get_tools"):
                                tools = mod.get_tools()
                                for t in tools:
                                    if isinstance(t, BaseTool):
                                        tool_reg.register(t)
                                        meta["tools"].append(t.name)
                    except Exception as e:
                        meta["error"] = str(e)

                self.loaded_plugins[p.name] = meta

    def list_plugins(self) -> List[Dict[str, Any]]:
        """Return list of loaded and discovered plugins."""
        self.discover_and_load_all()
        return list(self.loaded_plugins.values())

    def install_plugin_from_directory(self, source_path: Path) -> bool:
        """Install a plugin folder into the FireBox plugins directory."""
        if not source_path.exists() or not source_path.is_dir():
            return False
        dest = self.plugins_dir / source_path.name
        import shutil
        shutil.copytree(source_path, dest, dirs_exist_ok=True)
        self.discover_and_load_all()
        return True

    def remove_plugin(self, plugin_id: str) -> bool:
        """Remove an installed plugin."""
        target = self.plugins_dir / plugin_id
        if target.exists() and target.is_dir():
            import shutil
            shutil.rmtree(target)
            if plugin_id in self.loaded_plugins:
                del self.loaded_plugins[plugin_id]
            return True
        return False


_plugin_manager = None


def get_plugin_manager() -> PluginManager:
    global _plugin_manager
    if _plugin_manager is None:
        _plugin_manager = PluginManager()
    return _plugin_manager
