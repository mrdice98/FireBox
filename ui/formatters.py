"""
Output Formatters & UI components for FireBox.
Markdown responses, plan trees, tool result cards, and status banners.
"""

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.tree import Tree
from rich.table import Table
from rich.box import ROUNDED, SIMPLE, DOUBLE_EDGE
from rich.text import Text
import json

from firebox.ui.theme import (
    get_console,
    COLOR_FIRE_FLAME,
    COLOR_FIRE_DEEP,
    COLOR_FIRE_GOLD,
    COLOR_FIRE_YELLOW,
    COLOR_SUCCESS,
    COLOR_ERROR,
    COLOR_WARNING,
    COLOR_INFO,
    COLOR_ASH,
    COLOR_WHITE,
    COLOR_CHARCOAL_LIGHT,
)


def render_markdown(text: str, console: Console = None) -> None:
    """Render markdown text with terminal styling."""
    if console is None:
        console = get_console()
    md = Markdown(text, code_theme="monokai")
    console.print(md)


def render_plan(plan_dict: dict, console: Console = None) -> None:
    """Render an autonomous agent execution plan as a visual hierarchical tree."""
    if console is None:
        console = get_console()

    title = plan_dict.get("title", "Execution Plan")
    tree = Tree(f"[bold {COLOR_FIRE_GOLD}]📋 {title}[/]")

    milestones = plan_dict.get("steps", [])
    for idx, step in enumerate(milestones, 1):
        status = step.get("status", "pending").lower()
        desc = step.get("title", step.get("description", ""))
        
        if status == "done":
            icon = f"[bold {COLOR_SUCCESS}]✔ [DONE][/]"
            style = f"{COLOR_SUCCESS}"
        elif status == "in_progress":
            icon = f"[bold {COLOR_FIRE_FLAME}]⚡ [IN PROGRESS][/]"
            style = f"bold {COLOR_FIRE_YELLOW}"
        elif status == "failed":
            icon = f"[bold {COLOR_ERROR}]✖ [FAILED][/]"
            style = f"{COLOR_ERROR}"
        else:
            icon = f"[dim {COLOR_ASH}]○ [PENDING][/]"
            style = f"dim {COLOR_WHITE}"

        node = tree.add(f"{icon} [bold]{idx}.[/] [{style}]{desc}[/]")
        
        # Subtasks or verification items
        subtasks = step.get("subtasks", [])
        for sub in subtasks:
            sub_status = sub.get("status", "pending")
            sub_icon = "✔" if sub_status == "done" else "○"
            node.add(f"[dim]{sub_icon} {sub.get('text', '')}[/]")

    panel = Panel(
        tree,
        title=f"[bold {COLOR_FIRE_FLAME}]🔥 FIREBOX MISSION PLAN 🔥[/]",
        border_style=COLOR_FIRE_FLAME,
        box=ROUNDED,
    )
    console.print(panel)


def render_tool_result_card(
    tool_name: str,
    output: str,
    success: bool = True,
    duration_ms: float = 0.0,
    console: Console = None,
    max_preview_lines: int = 15,
) -> None:
    """Render tool execution result in a clean terminal card."""
    if console is None:
        console = get_console()

    status_badge = f"[bold {COLOR_SUCCESS}]SUCCESS[/]" if success else f"[bold {COLOR_ERROR}]FAILURE[/]"
    border_col = COLOR_SUCCESS if success else COLOR_ERROR

    lines = output.splitlines()
    if len(lines) > max_preview_lines:
        truncated = "\n".join(lines[:max_preview_lines])
        truncated += f"\n[dim italic]... ({len(lines) - max_preview_lines} more lines hidden)[/]"
    else:
        truncated = output

    panel = Panel(
        Text.from_markup(truncated) if "[" in truncated else Text(truncated),
        title=f"[bold cyan]{tool_name}[/] • {status_badge} • [dim]{duration_ms:.1f}ms[/]",
        border_style=border_col,
        box=ROUNDED,
    )
    console.print(panel)


def render_approval_prompt(action_desc: str, details: str = None, console: Console = None) -> bool:
    """Prompt the user for sensitive operation approval with clear warning styling."""
    if console is None:
        console = get_console()

    console.print()
    alert_box = Table(box=ROUNDED, show_header=False, border_style=COLOR_WARNING, expand=True)
    alert_box.add_column("Warning")
    alert_box.add_row(f"[bold {COLOR_WARNING}]⚠️  SENSITIVE OPERATION APPROVAL REQUIRED[/]")
    alert_box.add_row(f"[bold white]{action_desc}[/]")
    if details:
        alert_box.add_row(f"[dim yellow]{details}[/]")
    console.print(Panel(alert_box, border_style=COLOR_WARNING, box=ROUNDED))

    # Ask interactively
    try:
        ans = input("   Approve execution? [y/N/always]: ").strip().lower()
        return ans in ("y", "yes", "always")
    except (KeyboardInterrupt, EOFError):
        return False
