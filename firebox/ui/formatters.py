"""
Output Formatters & UI components for FireBox & Burner Engine.
Clean cards, tool execution summaries, plan trees, and status banners.
"""

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.tree import Tree
from rich.table import Table
from rich.box import ROUNDED, SIMPLE
from rich.text import Text
import json

from firebox.ui.theme import (
    get_console,
    COLOR_BORDER,
    COLOR_BORDER_ACTIVE,
    COLOR_BLUE,
    COLOR_ORANGE,
    COLOR_GRAY,
    COLOR_GRAY_LIGHT,
    COLOR_SUCCESS,
    COLOR_ERROR,
    COLOR_WARNING,
    COLOR_WHITE,
    COLOR_CHARCOAL_LIGHT,
)


def render_markdown(text: str, console: Console = None) -> None:
    """Render markdown agent responses with clean terminal typography."""
    if console is None:
        console = get_console()
    md = Markdown(text, code_theme="monokai")
    console.print(md)


def render_plan(plan_dict: dict, console: Console = None) -> None:
    """Render a Burner execution plan as a visual hierarchical tree."""
    if console is None:
        console = get_console()

    title = plan_dict.get("title", "Execution Plan")
    tree = Tree(f"[bold {COLOR_ORANGE}]📋 {title}[/]")

    milestones = plan_dict.get("steps", [])
    for idx, step in enumerate(milestones, 1):
        status = step.get("status", "pending").lower()
        desc = step.get("title", step.get("description", ""))

        if status == "done":
            icon = f"[bold {COLOR_SUCCESS}]✔ [DONE][/]"
            style = f"{COLOR_SUCCESS}"
        elif status == "in_progress":
            icon = f"[bold {COLOR_BLUE}]⚡ [IN PROGRESS][/]"
            style = f"bold {COLOR_BLUE}"
        elif status == "failed":
            icon = f"[bold {COLOR_ERROR}]✖ [FAILED][/]"
            style = f"{COLOR_ERROR}"
        else:
            icon = f"[dim {COLOR_GRAY}]○ [PENDING][/]"
            style = f"dim {COLOR_WHITE}"

        node = tree.add(f"{icon} [bold]{idx}.[/] [{style}]{desc}[/]")

        # Subtasks
        subtasks = step.get("subtasks", [])
        for sub in subtasks:
            sub_status = sub.get("status", "pending")
            sub_icon = "✔" if sub_status == "done" else "○"
            node.add(f"[dim {COLOR_GRAY_LIGHT}]{sub_icon} {sub.get('text', '')}[/]")

    panel = Panel(
        tree,
        title=f"[bold {COLOR_ORANGE}]🔥 Burner Plan[/]",
        title_align="left",
        border_style=COLOR_BORDER,
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
    """Render tool execution output inside a clean, modern card with subtle border."""
    if console is None:
        console = get_console()

    status_badge = f"[bold {COLOR_SUCCESS}]SUCCESS[/]" if success else f"[bold {COLOR_ERROR}]FAILURE[/]"

    lines = output.splitlines()
    if len(lines) > max_preview_lines:
        truncated = "\n".join(lines[:max_preview_lines])
        truncated += f"\n[dim {COLOR_GRAY}]... ({len(lines) - max_preview_lines} more lines hidden)[/]"
    else:
        truncated = output

    title_text = Text()
    title_text.append(tool_name, style=f"bold {COLOR_BLUE}")
    title_text.append(" · ", style=f"{COLOR_BORDER}")
    title_text.append("SUCCESS" if success else "FAILURE", style=f"bold {COLOR_SUCCESS if success else COLOR_ERROR}")
    title_text.append(" · ", style=f"{COLOR_BORDER}")
    title_text.append(f"{duration_ms:.1f}ms", style=f"dim {COLOR_GRAY}")

    panel = Panel(
        Text.from_markup(truncated) if "[" in truncated else Text(truncated),
        title=title_text,
        title_align="left",
        border_style=COLOR_BORDER,
        box=ROUNDED,
        padding=(0, 1),
    )
    console.print(panel)


def render_task_complete_card(task_summary: str, duration_sec: float = 0.0, console: Console = None) -> None:
    """Render a clean summary when Burner completes a task."""
    if console is None:
        console = get_console()

    table = Table(box=None, show_header=False, padding=(0, 1), expand=True)
    table.add_column("Col")
    table.add_row(f"[bold {COLOR_SUCCESS}]✔ Task Completed[/] [dim {COLOR_GRAY}]({duration_sec:.1f}s)[/]")
    table.add_row(f"[bold {COLOR_WHITE}]{task_summary}[/]")

    panel = Panel(
        table,
        border_style=COLOR_SUCCESS,
        box=ROUNDED,
    )
    console.print(panel)


def render_approval_prompt(action_desc: str, details: str = None, console: Console = None) -> bool:
    """Prompt the user for sensitive operation approval with clear warning styling."""
    if console is None:
        console = get_console()

    console.print()
    alert_box = Table(box=None, show_header=False, padding=(0, 1), expand=True)
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
