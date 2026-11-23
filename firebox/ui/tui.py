"""
Interactive Terminal UI (TUI) for FireBox & Burner Engine.
Inspired by OpenCode and GitHub Copilot CLI design language:
- Persistent prompt container with blue vertical accent
- Real-time status bar displaying Mode, Model, and Burner Engine
- Searchable slash command autocomplete menu with categories and descriptions
- Tab key to toggle agent modes (Build, Autonomous, Ask, Plan, Review)
- Ctrl+P quick command/model selector, Ctrl+L clear, Ctrl+C cancel
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

from firebox.ui.theme import (
    get_console,
    COLOR_BORDER,
    COLOR_BORDER_ACTIVE,
    COLOR_BLUE,
    COLOR_ORANGE,
    COLOR_GRAY,
    COLOR_GRAY_LIGHT,
    COLOR_WHITE,
    COLOR_CHARCOAL,
    COLOR_CHARCOAL_LIGHT,
)

# Registry of all supported slash commands with categories and descriptions
SLASH_COMMANDS = {
    # General
    "/help": ("General", "Show comprehensive command & feature guide"),
    "/doctor": ("General", "Run diagnostic health checks on environment & tools"),
    "/status": ("General", "Show current workspace, model, provider, and mode"),
    "/settings": ("General", "Configure FireBox behavior, animation mode, and themes"),
    "/clear": ("General", "Clear terminal screen and redraw compact dashboard"),
    "/exit": ("General", "Exit FireBox safely"),
    "/quit": ("General", "Quit the application"),

    # Mode Switching
    "/mode": ("Workflow", "Switch agent mode (build, autonomous, ask, plan, review)"),
    "/build": ("Workflow", "Switch to Build mode (implement features & verify)"),
    "/plan": ("Workflow", "Switch to Plan mode (strategic milestone planning)"),
    "/ask": ("Workflow", "Switch to Ask mode (read-only explanation and Q&A)"),
    "/review": ("Workflow", "Switch to Review mode (deep code & security review)"),

    # Coding & Tools
    "/test": ("Coding", "Detect and run test suite in the current workspace"),
    "/fix": ("Coding", "Diagnose and fix errors or test failures"),
    "/refactor": ("Coding", "Refactor targeted code for readability & performance"),
    "/diff": ("Coding", "Show unified diff of current workspace changes"),
    "/files": ("Coding", "List or inspect files in workspace"),
    "/search": ("Coding", "Search files and code symbols across the project"),
    "/git": ("Coding", "Run or inspect Git operations (status, diff, branch)"),
    "/commit": ("Coding", "Generate intelligent commit message and commit changes"),
    "/terminal": ("Coding", "Run a one-off shell command in the project"),
    "/undo": ("Safety", "Rollback the last file change or action"),

    # Models & Providers
    "/models": ("Provider", "Browse available models for current provider"),
    "/model": ("Provider", "Switch active model (e.g. /model gpt-4o, /model claude-3-7-sonnet)"),
    "/providers": ("Provider", "List all supported and configured AI providers (by number 1-19)"),
    "/provider": ("Provider", "Switch active AI provider by number or name (e.g. /provider 1)"),
    "/setup": ("Provider", "Interactive setup wizard to select provider by number and plug in API key"),
    "/key": ("Provider", "Plug in or update API key for a provider with visible confirmation"),

    # Sessions & Memory
    "/new": ("Session", "Start a clean new conversation session"),
    "/resume": ("Session", "Resume a previous session from history"),
    "/sessions": ("Session", "List, manage, or switch active sessions"),
    "/compact": ("Session", "Compact conversation context to save tokens"),
    "/context": ("Session", "View current token usage and active context files"),

    # Extensions & System
    "/tools": ("System", "List registered tools and toggle availability"),
    "/plugins": ("System", "Manage FireBox plugins and extensions"),
    "/permissions": ("System", "View or change security permissions profile"),
    "/config": ("System", "Inspect or edit global and project configuration"),
    "/logs": ("System", "View agent execution and audit logs"),
}


class SlashCommandCompleter(Completer):
    """Searchable autocomplete for FireBox slash commands."""

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor.lstrip()
        if text.startswith("/"):
            word = text.split()[0]
            for cmd, (cat, desc) in SLASH_COMMANDS.items():
                if cmd.lower().startswith(word.lower()):
                    display_meta = f"[{cat}] {desc}"
                    yield Completion(
                        cmd,
                        start_position=-len(word),
                        display=cmd,
                        display_meta=display_meta,
                    )


class FireBoxTUI:
    """Terminal User Interface manager for interactive session."""

    AVAILABLE_MODES = ["build", "autonomous", "ask", "plan", "review"]

    def __init__(
        self,
        history_file: Optional[Path] = None,
        initial_mode: str = "build",
        on_mode_change: Optional[Callable[[str], None]] = None,
    ):
        if history_file is None:
            from firebox.config.manager import get_config
            history_file = get_config().base_dir / "history"

        self.history_file = history_file
        self.completer = SlashCommandCompleter()
        self.current_mode = initial_mode.lower()
        self.on_mode_change = on_mode_change

        self.kb = self._create_key_bindings()

        # Modern OpenCode/Copilot inspired styling
        self.style = PtStyle.from_dict({
            # Prompt accents
            "prompt.bar": "#38BDF8 bold",         # Blue accent bar on the left
            "prompt.arrow": "#A1A1AA",             # Subdued arrow
            "prompt.input": "#F8FAFC",             # Clean white input text

            # Bottom toolbar styling
            "bottom-toolbar": "bg:#18181B #A1A1AA",
            "toolbar.mode": "#38BDF8 bold",        # Blue mode label
            "toolbar.model": "#F8FAFC bold",       # White model name
            "toolbar.burner": "#FF6B00 bold",      # Orange Burner engine
            "toolbar.hints": "#71717A",            # Subtle gray hints

            # Completion menu styling
            "completion-menu.completion": "bg:#18181B #F8FAFC",
            "completion-menu.completion.current": "bg:#2563EB #FFFFFF bold",
            "completion-menu.meta": "bg:#121214 #71717A",
            "completion-menu.meta.current": "bg:#1D4ED8 #FFFFFF",
            "scrollbar.background": "bg:#121214",
            "scrollbar.button": "bg:#38BDF8",
        })

        self.session = PromptSession(
            history=FileHistory(str(self.history_file)),
            auto_suggest=AutoSuggestFromHistory(),
            completer=self.completer,
            key_bindings=self.kb,
            style=self.style,
            enable_history_search=True,
            bottom_toolbar=self._get_bottom_toolbar,
        )

    def cycle_mode(self):
        """Cycle agent mode to next option."""
        try:
            curr_idx = self.AVAILABLE_MODES.index(self.current_mode)
            next_idx = (curr_idx + 1) % len(self.AVAILABLE_MODES)
            self.current_mode = self.AVAILABLE_MODES[next_idx]
        except ValueError:
            self.current_mode = "build"

        if self.on_mode_change:
            self.on_mode_change(self.current_mode)

    def _create_key_bindings(self) -> KeyBindings:
        """Create custom keyboard shortcuts for the interactive prompt."""
        kb = KeyBindings()

        @kb.add("c-l")
        def _clear(event):
            """Ctrl+L: Clear terminal screen."""
            event.app.renderer.clear()

        @kb.add("c-p")
        def _command_palette(event):
            """Ctrl+P: Command palette trigger."""
            get_console().print("\n[bold cyan]Tip:[/] Type [bold white]/[/] to browse all slash commands, or [bold white]/model[/] to switch model.")

        @kb.add("tab")
        def _tab_cycle(event):
            """Tab: Cycle mode when prompt line is empty or at start."""
            buf = event.current_buffer
            if not buf.text or buf.text.isspace():
                self.cycle_mode()
                event.app.invalidate()
            else:
                # If typing, allow normal completion
                buf.complete_next()

        return kb

    def _get_bottom_toolbar(self) -> HTML:
        """Render bottom status toolbar inside the prompt container (Image 1 OpenCode style)."""
        mode_label = self.current_mode.capitalize()
        from firebox.config.manager import get_config
        model_name = get_config().app_config.active_model

        return HTML(
            f" <style class='toolbar.mode'>{mode_label}</style>  "
            f"<style class='toolbar.model'>{model_name}</style>  "
            f"<style class='toolbar.burner'>🔥 Burner</style>    "
            f"<style class='toolbar.hints'>[Tab: switch mode · / commands · Ctrl+C: cancel]</style>"
        )

    def get_prompt_text(self) -> HTML:
        """
        Render vertical blue accent line with prompt arrow:
        │ > [input]
        """
        return HTML(
            "<style class='prompt.bar'>│</style> "
            "<style class='prompt.arrow'>></style> "
        )

    def prompt(self, mode: Optional[str] = None, model_name: Optional[str] = None) -> str:
        """Prompt user for input with full autocomplete, history, and bottom toolbar."""
        if mode:
            self.current_mode = mode.lower()
        try:
            return self.session.prompt(self.get_prompt_text()).strip()
        except KeyboardInterrupt:
            return "/cancel"
        except EOFError:
            return "/exit"
