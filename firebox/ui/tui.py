"""
Interactive Terminal UI (TUI) for FireBox.
Powered by prompt_toolkit with rich auto-completion, key bindings,
multiline input, history persistence, and cinematic styling.
"""

import os
import sys
from pathlib import Path
from typing import List, Callable, Optional, Dict, Any

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style as PtStyle
from prompt_toolkit.formatted_text import HTML

from firebox.ui.theme import get_console, COLOR_FIRE_FLAME, COLOR_FIRE_GOLD

# Registry of all supported slash commands with categories and descriptions
SLASH_COMMANDS = {
    "/help": ("General", "Show comprehensive command & feature guide"),
    "/exit": ("General", "Exit FireBox safely"),
    "/quit": ("General", "Quit the application"),
    "/clear": ("General", "Clear terminal screen and redraw status"),
    "/status": ("General", "Show current workspace, model, provider and agent status"),
    "/doctor": ("General", "Run diagnostic health checks on tools, API keys, and environment"),
    "/settings": ("General", "Configure FireBox behavior, animation mode, and themes"),
    
    "/new": ("Session", "Start a clean new conversation session"),
    "/resume": ("Session", "Resume a previous session from history"),
    "/sessions": ("Session", "List, manage, or switch active sessions"),
    "/compact": ("Session", "Compact conversation context to save tokens"),
    "/context": ("Session", "View current token usage and active context files"),
    
    "/models": ("Provider", "List available models for current provider"),
    "/model": ("Provider", "Switch active model (e.g. /model gpt-4o, /model claude-3-7-sonnet)"),
    "/provider": ("Provider", "Switch or configure active AI provider"),
    "/providers": ("Provider", "List all supported and configured AI providers"),
    
    "/plan": ("Workflow", "Generate or display step-by-step task execution plan"),
    "/execute": ("Workflow", "Execute pending steps in the current plan"),
    "/approve": ("Workflow", "Approve pending sensitive operations"),
    "/reject": ("Workflow", "Reject pending sensitive operations"),
    "/undo": ("Workflow", "Rollback the last file change or action"),
    "/retry": ("Workflow", "Retry the last failed step or tool execution"),
    
    "/review": ("Coding", "Perform deep code review on modified or target files"),
    "/test": ("Coding", "Detect and run test suite in the current workspace"),
    "/fix": ("Coding", "Automatically diagnose and fix errors or test failures"),
    "/refactor": ("Coding", "Refactor targeted code for readability and performance"),
    "/search": ("Coding", "Search files and code symbols across the project"),
    "/files": ("Coding", "List or inspect files in workspace"),
    "/diff": ("Coding", "Show unified diff of current workspace changes"),
    "/git": ("Coding", "Run or inspect Git operations (status, diff, branch)"),
    "/commit": ("Coding", "Generate intelligent commit message and commit changes"),
    "/terminal": ("Coding", "Run a one-off shell command in the project"),
    
    "/tools": ("System", "List registered tools and toggle availability"),
    "/plugins": ("System", "Manage FireBox plugins and extensions"),
    "/permissions": ("System", "View or change security permissions profile"),
    "/config": ("System", "Inspect or edit global and project configuration"),
    "/logs": ("System", "View agent execution and audit logs"),
}


class SlashCommandCompleter(Completer):
    """Smart autocomplete for FireBox slash commands."""

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        if text.startswith("/"):
            word = text.split()[0]
            for cmd, (cat, desc) in SLASH_COMMANDS.items():
                if cmd.startswith(word):
                    display_meta = f"[{cat}] {desc}"
                    yield Completion(
                        cmd,
                        start_position=-len(word),
                        display=cmd,
                        display_meta=display_meta,
                    )


def create_key_bindings(
    on_model_switch: Optional[Callable] = None,
    on_command_menu: Optional[Callable] = None,
    on_plan_toggle: Optional[Callable] = None,
    on_task_info: Optional[Callable] = None,
) -> KeyBindings:
    """Create keyboard shortcut bindings for the interactive prompt."""
    kb = KeyBindings()

    @kb.add("c-l")
    def _clear(event):
        """Ctrl+L: Clear screen."""
        event.app.renderer.clear()

    @kb.add("c-p")
    def _model_selector(event):
        """Ctrl+P: Model selector trigger."""
        if on_model_switch:
            on_model_switch()
        else:
            get_console().print("\n[bold yellow]Model switcher triggered (type /model <name>)[/]")

    @kb.add("c-o")
    def _command_menu(event):
        """Ctrl+O: Open command menu."""
        if on_command_menu:
            on_command_menu()
        else:
            get_console().print("\n[bold cyan]Command menu: type / for autocomplete[/]")

    @kb.add("c-g")
    def _toggle_plan(event):
        """Ctrl+G: Toggle plan view."""
        if on_plan_toggle:
            on_plan_toggle()

    @kb.add("c-t")
    def _toggle_task(event):
        """Ctrl+T: Toggle task info."""
        if on_task_info:
            on_task_info()

    return kb


class FireBoxTUI:
    """Terminal User Interface manager for interactive session."""

    def __init__(self, history_file: Optional[Path] = None):
        if history_file is None:
            from firebox.config.manager import get_config
            history_file = get_config().base_dir / "history"

        self.history_file = history_file
        self.completer = SlashCommandCompleter()
        self.kb = create_key_bindings()

        # Prompt style with fire accents
        self.style = PtStyle.from_dict({
            "prompt.fire": "#FF5500 bold",
            "prompt.arrow": "#FFB703 bold",
            "prompt.cwd": "#FAFAFA",
            "completion-menu.completion": "bg:#1E1E24 #F8FAFC",
            "completion-menu.completion.current": "bg:#FF5500 #000000 bold",
            "completion-menu.meta": "bg:#121214 #71717A",
            "completion-menu.meta.current": "bg:#FFB703 #000000",
        })

        self.session = PromptSession(
            history=FileHistory(str(self.history_file)),
            auto_suggest=AutoSuggestFromHistory(),
            completer=self.completer,
            key_bindings=self.kb,
            style=self.style,
            enable_history_search=True,
        )

    def get_prompt_text(self, mode: str = "agent", model_name: str = "gpt-4o") -> HTML:
        """Generate styled prompt text."""
        return HTML(
            f"<prompt.fire><b>firebox</b></prompt.fire> "
            f"<prompt.arrow>🔥</prompt.arrow> "
            f"[<style color='#06B6D4'>{model_name}</style>] "
            f"<prompt.arrow>❯</prompt.arrow> "
        )

    def prompt(self, mode: str = "agent", model_name: str = "gpt-4o") -> str:
        """Prompt user for input with autocompletion and history."""
        try:
            return self.session.prompt(self.get_prompt_text(mode, model_name)).strip()
        except KeyboardInterrupt:
            return "/cancel"
        except EOFError:
            return "/exit"
