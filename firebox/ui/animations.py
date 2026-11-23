"""
Modern Minimal UI Sequences and Headers for FireBox & Burner Engine.
Inspired by OpenCode and GitHub Copilot CLI design language:
Clean lines, subtle borders, gray metadata, blue accents, and orange Burner branding.
"""

import time
import os
import sys
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.box import ROUNDED, HORIZONTALS

from firebox.ui.theme import (
    get_console,
    COLOR_CHARCOAL,
    COLOR_CHARCOAL_LIGHT,
    COLOR_BORDER,
    COLOR_BORDER_ACTIVE,
    COLOR_GRAY,
    COLOR_GRAY_LIGHT,
    COLOR_BLUE,
    COLOR_ORANGE,
    COLOR_SUCCESS,
    COLOR_ERROR,
    COLOR_WHITE,
)
from firebox.version import VERSION, CODENAME
from firebox import __tagline__

# Clean compact modern banner
COMPACT_BANNER = [
    r"  ███████╗██╗██████╗ ███████╗██████╗  ██████╗ ██╗  ██╗",
    r"  ██╔════╝██║██╔══██╗██╔════╝██╔══██╗██╔══██╗╚██╗██╔╝",
    r"  █████╗  ██║██████╔╝█████╗  ██████╔╝██████╔╝ ╚███╔╝ ",
    r"  ██╔══╝  ██║██╔══██╗██╔══╝  ██╔══██╗██╔═══╝  ██╔██╗ ",
    r"  ██║     ██║██║  ██║███████╗██║  ██║██║     ██║  ██╗",
    r"  ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═════╝ ╚═╝  ╚═╝",
]


def render_logo(console: Console = None, mode: str = "cinematic") -> None:
    """Render a clean, modern FireBox wordmark banner."""
    if console is None:
        console = get_console()

    if mode == "none":
        console.print(f"[bold {COLOR_ORANGE}]FireBox[/] [dim {COLOR_GRAY}]v{VERSION}[/] · [bold {COLOR_BLUE}]Burner[/] · {__tagline__}")
        return

    # Compact modern header
    title_text = Text()
    title_text.append("FireBox", style=f"bold {COLOR_ORANGE}")
    title_text.append("  /  ", style=f"{COLOR_BORDER}")
    title_text.append("🔥 Burner Engine", style=f"bold {COLOR_ORANGE}")
    title_text.append(f"  v{VERSION}", style=f"dim {COLOR_GRAY}")
    console.print(title_text)
    console.print(f"[dim {COLOR_GRAY_LIGHT}]{__tagline__}[/]\n")


def display_startup_card(
    provider_name: str = "OpenAI",
    model_name: str = "gpt-4o",
    cwd: str = None,
    session_id: str = "default",
    tools_count: int = 19,
    mode: str = "cinematic",
    safety_level: str = "BALANCED",
    agent_mode: str = "Build",
    console: Console = None,
) -> None:
    """
    Display the modern OpenCode/Copilot inspired compact dashboard card:
    ╭─ FireBox ────────────────────────────────────────────────────────╮
    │  🔥 Burner  ·  OpenAI  ·  Model: gpt-4o                          │
    │  Project: my-project  ·  Mode: Build                             │
    │  Ready to work on your code.                                     │
    ╰──────────────────────────────────────────────────────────────────╯
    """
    if console is None:
        console = get_console()

    if cwd is None:
        cwd = os.getcwd()

    project_name = Path(cwd).name or "workspace"

    # Card content table
    table = Table(
        box=None,
        show_header=False,
        padding=(0, 1),
        expand=True,
    )
    table.add_column("Col1", ratio=1)

    # Line 1: Engine · Provider · Model
    engine_line = Text()
    engine_line.append("🔥 Burner", style=f"bold {COLOR_ORANGE}")
    engine_line.append("  ·  ", style=f"{COLOR_GRAY}")
    engine_line.append(provider_name, style=f"bold {COLOR_WHITE}")
    engine_line.append("  ·  ", style=f"{COLOR_GRAY}")
    engine_line.append("Model: ", style=f"{COLOR_GRAY_LIGHT}")
    engine_line.append(model_name, style=f"bold {COLOR_BLUE}")
    table.add_row(engine_line)

    # Line 2: Empty spacer
    table.add_row("")

    # Line 3: Project · Mode · Tools
    project_line = Text()
    project_line.append("Project: ", style=f"{COLOR_GRAY_LIGHT}")
    project_line.append(project_name, style=f"bold {COLOR_WHITE}")
    project_line.append(f" ({cwd})", style=f"dim {COLOR_GRAY}")
    project_line.append("  ·  ", style=f"{COLOR_GRAY}")
    project_line.append("Mode: ", style=f"{COLOR_GRAY_LIGHT}")
    project_line.append(agent_mode.capitalize(), style=f"bold {COLOR_BLUE}")
    table.add_row(project_line)

    # Line 4: Status / Ready text
    ready_line = Text()
    ready_line.append("Ready to work on your code. ", style=f"{COLOR_GRAY_LIGHT}")
    ready_line.append(f"[{tools_count} tools active · {safety_level} safety]", style=f"dim {COLOR_GRAY}")
    table.add_row(ready_line)

    panel = Panel(
        table,
        title=f"[bold {COLOR_ORANGE}]FireBox[/] [dim {COLOR_GRAY}]· v{VERSION}[/]",
        title_align="left",
        border_style=COLOR_BORDER,
        box=ROUNDED,
        padding=(1, 2),
    )
    console.print(panel)
    console.print(f"[dim {COLOR_GRAY}] /help   /model   /plan   /tools   /review   /test   /settings[/]\n")


def print_thinking(message: str = "Analyzing task and inspecting codebase...", console: Console = None) -> None:
    """Print clean thinking indicator for the Burner engine."""
    if console is None:
        console = get_console()
    console.print(f"[bold {COLOR_ORANGE}]🔥 Burner[/] [dim {COLOR_GRAY}]·[/] [dim {COLOR_BLUE}]Thinking:[/] [dim {COLOR_WHITE}]{message}[/]")


def print_tool_start(tool_name: str, args_summary: str, console: Console = None) -> None:
    """Print clean tool execution start line."""
    if console is None:
        console = get_console()
    console.print(f" [bold {COLOR_BLUE}]⚡ TOOL EXEC:[/] [bold {COLOR_WHITE}]{tool_name}[/] [dim {COLOR_GRAY}]({args_summary})[/]")


def print_tool_finish(tool_name: str, success: bool = True, elapsed_ms: float = 0.0, console: Console = None) -> None:
    """Print clean tool execution finish indicator."""
    if console is None:
        console = get_console()
    if success:
        console.print(f"   [bold {COLOR_SUCCESS}]✔ DONE[/] [dim {COLOR_GRAY}]{tool_name} ({elapsed_ms:.1f}ms)[/]")
    else:
        console.print(f"   [bold {COLOR_ERROR}]✖ FAILED[/] [dim {COLOR_GRAY}]{tool_name} ({elapsed_ms:.1f}ms)[/]")
