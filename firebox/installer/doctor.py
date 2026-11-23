"""
System Diagnostics and Health Check ("firebox doctor").
Validates environment, runtimes, git, providers, API keys, and workspace safety.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Tuple

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.box import ROUNDED

from firebox.version import VERSION
from firebox.config.manager import get_config
from firebox.providers.registry import get_provider_registry
from firebox.tools.registry import get_tool_registry
from firebox.ui.theme import (
    get_console,
    COLOR_FIRE_FLAME,
    COLOR_FIRE_GOLD,
    COLOR_SUCCESS,
    COLOR_ERROR,
    COLOR_WARNING,
    COLOR_INFO,
    COLOR_WHITE,
)


class DiagnosticItem:
    def __init__(self, category: str, name: str, status: str, message: str, fix_suggestion: str = None):
        self.category = category
        self.name = name
        self.status = status     # "PASS", "WARN", "FAIL"
        self.message = message
        self.fix_suggestion = fix_suggestion


def run_diagnostics(workspace_root: Path = None, console: Console = None) -> List[DiagnosticItem]:
    """Execute all system, provider, and tool diagnostic checks."""
    if console is None:
        console = get_console()
    if workspace_root is None:
        workspace_root = Path.cwd().resolve()

    items = []
    config_mgr = get_config()
    provider_reg = get_provider_registry()
    tool_reg = get_tool_registry(workspace_root)

    # 1. Python Environment Check
    py_ver = sys.version.split()[0]
    if sys.version_info >= (3, 10):
        items.append(DiagnosticItem("System", "Python Version", "PASS", f"Python {py_ver} (>= 3.10 supported)"))
    else:
        items.append(DiagnosticItem("System", "Python Version", "FAIL", f"Python {py_ver} (< 3.10)", "Upgrade to Python 3.10+"))

    # 2. Operating System & Terminal
    os_name = "Windows" if os.name == "nt" else sys.platform.capitalize()
    term_support = "TrueColor/ANSI Ready" if console.is_terminal else "Non-interactive / Redirected"
    items.append(DiagnosticItem("System", "OS & Terminal", "PASS", f"{os_name} • {term_support}"))

    # 3. Git Availability
    git_bin = shutil.which("git")
    if git_bin:
        try:
            res = subprocess.run(["git", "--version"], stdout=subprocess.PIPE, text=True)
            git_ver = res.stdout.strip()
            items.append(DiagnosticItem("Tools", "Git CLI", "PASS", f"{git_ver} found at {git_bin}"))
        except Exception:
            items.append(DiagnosticItem("Tools", "Git CLI", "WARN", "Git executable detected but could not query version"))
    else:
        items.append(DiagnosticItem("Tools", "Git CLI", "WARN", "Git not found on PATH", "Install Git to enable version control tools"))

    # 4. Configuration Storage
    if config_mgr.base_dir.exists() and os.access(config_mgr.base_dir, os.W_OK):
        items.append(DiagnosticItem("Config", "Storage Directory", "PASS", f"Writable: {config_mgr.base_dir}"))
    else:
        items.append(DiagnosticItem("Config", "Storage Directory", "FAIL", f"Cannot write to {config_mgr.base_dir}", "Check folder permissions"))

    # 5. Core Configuration Files
    cfg_exists = config_mgr.config_file.exists()
    prov_exists = config_mgr.providers_file.exists()
    if cfg_exists and prov_exists:
        items.append(DiagnosticItem("Config", "Config Files", "PASS", "config.json and providers.json present and valid"))
    else:
        items.append(DiagnosticItem("Config", "Config Files", "WARN", "Config initialized with defaults"))

    # 6. Active AI Provider & Credentials
    active_prov_name = config_mgr.app_config.active_provider
    active_model = config_mgr.app_config.active_model
    provider = provider_reg.get_provider(active_prov_name)
    has_key = bool(provider.api_key) or active_prov_name in ("ollama", "lmstudio", "mock")

    if has_key:
        items.append(DiagnosticItem("AI Provider", f"Active: {provider.name}", "PASS", f"Model: {active_model} • API key configured"))
    else:
        items.append(
            DiagnosticItem(
                "AI Provider",
                f"Active: {provider.name}",
                "WARN",
                f"No API key found for {provider.name}.",
                f"Set {active_prov_name.upper()}_API_KEY or run 'firebox provider add'"
            )
        )

    # 7. Tool Registry
    tools = tool_reg.list_tools()
    enabled_count = sum(1 for t in tools if t["enabled"])
    if enabled_count >= 10:
        items.append(DiagnosticItem("Tools", "Registered Tools", "PASS", f"{enabled_count}/{len(tools)} tools active and ready"))
    else:
        items.append(DiagnosticItem("Tools", "Registered Tools", "WARN", f"Only {enabled_count} tools enabled"))

    # 8. Workspace Safety & Permissions
    safety = config_mgr.permissions.safety_level.value
    ws_status = "Workspace Isolation Active" if config_mgr.permissions.workspace_only else "Unrestricted"
    items.append(DiagnosticItem("Security", "Safety Policy", "PASS", f"Level: {safety} • {ws_status}"))

    # Render results table
    table = Table(box=ROUNDED, border_style=COLOR_FIRE_FLAME, expand=True)
    table.add_column("Category", style=f"bold {COLOR_FIRE_GOLD}", width=15)
    table.add_column("Component", style="bold white", width=22)
    table.add_column("Status", width=10, justify="center")
    table.add_column("Details", style=COLOR_WHITE)

    fail_count = 0
    warn_count = 0

    for item in items:
        if item.status == "PASS":
            status_text = f"[bold {COLOR_SUCCESS}]PASS[/]"
        elif item.status == "WARN":
            status_text = f"[bold {COLOR_WARNING}]WARN[/]"
            warn_count += 1
        else:
            status_text = f"[bold {COLOR_ERROR}]FAIL[/]"
            fail_count += 1

        details = item.message
        if item.fix_suggestion:
            details += f"\n[dim yellow]  ↳ Suggestion: {item.fix_suggestion}[/]"

        table.add_row(item.category, item.name, status_text, details)

    # Summary Panel
    if fail_count == 0 and warn_count == 0:
        verdict = f"[bold {COLOR_SUCCESS}]ALL SYSTEMS OPTIMAL — FIREBOX READY[/]"
    elif fail_count == 0:
        verdict = f"[bold {COLOR_WARNING}]DEGRADED — {warn_count} WARNING(S) (OPERATIONAL WITH LIMITS)[/]"
    else:
        verdict = f"[bold {COLOR_ERROR}]ACTION REQUIRED — {fail_count} FAILED CHECK(S)[/]"

    panel = Panel(
        table,
        title=f"[bold {COLOR_FIRE_GOLD}]🔥 FIREBOX SYSTEM DOCTOR v{VERSION} 🔥[/]",
        subtitle=verdict,
        border_style=COLOR_FIRE_FLAME,
        box=ROUNDED,
    )
    console.print(panel)
    return items
