"""
Cinematic Animations & Visual Sequences for FireBox.
Logo reveal, ember particles, tagline animation, and system status card.
"""

import time
import random
import os
import sys
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich.box import ROUNDED, HEAVY

from firebox.ui.theme import (
    get_console,
    gradient_text,
    COLOR_FIRE_DEEP,
    COLOR_FIRE_FLAME,
    COLOR_FIRE_BRIGHT,
    COLOR_FIRE_GOLD,
    COLOR_FIRE_YELLOW,
    COLOR_ASH,
    COLOR_WHITE,
    COLOR_SUCCESS,
    COLOR_CHARCOAL_LIGHT,
)
from firebox import __version__, __tagline__

ASCII_LOGO = [
    r"  ███████╗██╗██████╗ ███████╗██████╗  ██████╗ ██╗  ██╗",
    r"  ██╔════╝██║██╔══██╗██╔════╝██╔══██╗██╔══██╗╚██╗██╔╝",
    r"  █████╗  ██║██████╔╝█████╗  ██████╔╝██████╔╝ ╚███╔╝ ",
    r"  ██╔══╝  ██║██╔══██╗██╔══╝  ██╔══██╗██╔═══╝  ██╔██╗ ",
    r"  ██║     ██║██║  ██║███████╗██║  ██║██║     ██║  ██╗",
    r"  ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═════╝ ╚═╝  ╚═╝",
]

EMBER_PARTICLES = ["*", "·", "°", "✦", "▲", "🔥", "░", "▒", "·", "•", "✧"]


def render_logo(console: Console = None, mode: str = "cinematic") -> None:
    """Render the FireBox logo with fire gradients and optional cinematic animation."""
    if console is None:
        console = get_console()

    gradient_steps = [
        (COLOR_FIRE_DEEP, COLOR_FIRE_FLAME),
        (COLOR_FIRE_DEEP, COLOR_FIRE_BRIGHT),
        (COLOR_FIRE_FLAME, COLOR_FIRE_GOLD),
        (COLOR_FIRE_BRIGHT, COLOR_FIRE_GOLD),
        (COLOR_FIRE_GOLD, COLOR_FIRE_YELLOW),
        (COLOR_FIRE_GOLD, COLOR_FIRE_YELLOW),
    ]

    if mode == "none":
        console.print(f"[bold red]FIREBOX v{__version__}[/bold red] — {__tagline__}")
        return

    # In cinematic mode, do a quick ember sparkle effect
    if mode == "cinematic" and sys.stdout.isatty():
        # Quick 3-frame ember wave
        for _ in range(3):
            embers = "".join(random.choice(EMBER_PARTICLES) + " " for _ in range(25))
            sys.stdout.write(f"\r\033[K\033[38;2;255;100;0m   {embers}\033[0m")
            sys.stdout.flush()
            time.sleep(0.04)
        sys.stdout.write("\r\033[K")
        sys.stdout.flush()

    for i, line in enumerate(ASCII_LOGO):
        start_col, end_col = gradient_steps[min(i, len(gradient_steps) - 1)]
        styled_line = gradient_text(line, start_col, end_col)
        console.print(styled_line)
        if mode == "cinematic" and sys.stdout.isatty():
            time.sleep(0.03)

    # Tagline with gold flame glow
    tagline_text = f"             {__tagline__}"
    console.print(f"[bold {COLOR_FIRE_GOLD}]{tagline_text}[/]\n")


def display_startup_card(
    provider_name: str = "OpenAI",
    model_name: str = "gpt-4o",
    cwd: str = None,
    session_id: str = "default",
    tools_count: int = 12,
    mode: str = "cinematic",
    safety_level: str = "BALANCED",
    console: Console = None,
) -> None:
    """Display the cinematic startup info card with current workspace state."""
    if console is None:
        console = get_console()

    if cwd is None:
        cwd = os.getcwd()

    render_logo(console, mode=mode)

    table = Table(
        box=ROUNDED,
        show_header=False,
        border_style=COLOR_FIRE_FLAME,
        padding=(0, 1),
        expand=True,
    )
    table.add_column("Key", style=f"bold {COLOR_FIRE_GOLD}", width=18)
    table.add_column("Value", style=COLOR_WHITE)

    table.add_row("Version", f"[bold {COLOR_FIRE_YELLOW}]v{__version__}[/] [dim]• Prometheus Ember[/]")
    table.add_row("Active Provider", f"[bold {COLOR_FIRE_FLAME}]{provider_name}[/] [dim]• Multiple profiles ready[/]")
    table.add_row("Active Model", f"[bold cyan]{model_name}[/]")
    table.add_row("Workspace", f"[bold white]{cwd}[/]")
    table.add_row("Session", f"[bold {COLOR_FIRE_GOLD}]{session_id}[/] [dim](persistent state)[/]")
    table.add_row("Registered Tools", f"[bold {COLOR_SUCCESS}]{tools_count} active tools[/] [dim]• File, Search, Git, Exec, Web, Project[/]")
    table.add_row("Safety Policy", f"[bold yellow]{safety_level}[/] [dim]• Workspace restricted • Approvals on sensitive ops[/]")

    panel = Panel(
        table,
        title=f"[bold {COLOR_FIRE_GOLD}]🔥 FIREBOX AUTONOMOUS AGENT ONLINE 🔥[/]",
        subtitle="[dim]Type [bold cyan]/help[/] for commands • [bold cyan]Ctrl+P[/] switch model • [bold cyan]Ctrl+C[/] cancel[/]",
        border_style=COLOR_FIRE_FLAME,
        box=ROUNDED,
    )
    console.print(panel)
    console.print()


def print_thinking(message: str = "Analyzing task and inspecting codebase...", console: Console = None) -> None:
    """Print an ember animated thinking indicator."""
    if console is None:
        console = get_console()
    console.print(f"[bold {COLOR_FIRE_GOLD}]🔥 [fire.flame]Thinking:[/] [dim white]{message}[/]")


def print_tool_start(tool_name: str, args_summary: str, console: Console = None) -> None:
    """Print a styled indicator when a tool execution begins."""
    if console is None:
        console = get_console()
    console.print(f" [bold {COLOR_FIRE_FLAME}]⚡ TOOL EXEC:[/] [bold cyan]{tool_name}[/] [dim]({args_summary})[/]")


def print_tool_finish(tool_name: str, success: bool = True, elapsed_ms: float = 0.0, console: Console = None) -> None:
    """Print a styled indicator when a tool execution finishes."""
    if console is None:
        console = get_console()
    if success:
        console.print(f"   [bold {COLOR_SUCCESS}]✔ DONE[/] [dim]{tool_name} ({elapsed_ms:.1f}ms)[/]")
    else:
        console.print(f"   [bold {COLOR_ERROR}]✖ FAILED[/] [dim]{tool_name} ({elapsed_ms:.1f}ms)[/]")
