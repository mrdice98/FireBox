"""
Diff Viewer for FireBox & Burner Engine.
Unified and side-by-side terminal syntax-highlighted diffs with subtle borders.
"""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.syntax import Syntax
from rich.box import ROUNDED
import difflib

from firebox.ui.theme import (
    get_console,
    COLOR_BORDER,
    COLOR_BLUE,
    COLOR_ORANGE,
    COLOR_SUCCESS,
    COLOR_ERROR,
    COLOR_GRAY,
    COLOR_WHITE,
)


def render_diff(
    old_content: str,
    new_content: str,
    filename: str = "file",
    console: Console = None,
    title: str = None,
) -> None:
    """Render a clean unified diff in the terminal with line numbers and color highlights."""
    if console is None:
        console = get_console()

    old_lines = old_content.splitlines(keepends=True)
    new_lines = new_content.splitlines(keepends=True)
    diff = list(difflib.unified_diff(old_lines, new_lines, fromfile=f"a/{filename}", tofile=f"b/{filename}", n=3))

    if not diff:
        console.print(f"[dim {COLOR_GRAY}]No changes in [bold]{filename}[/][/dim]")
        return

    diff_text = Text()
    additions = 0
    deletions = 0

    for line in diff:
        clean = line.rstrip("\r\n")
        if line.startswith("---") or line.startswith("+++"):
            diff_text.append(clean + "\n", style=f"bold {COLOR_GRAY}")
        elif line.startswith("@@"):
            diff_text.append(clean + "\n", style=f"bold {COLOR_BLUE}")
        elif line.startswith("+"):
            diff_text.append(clean + "\n", style=f"bold {COLOR_SUCCESS}")
            additions += 1
        elif line.startswith("-"):
            diff_text.append(clean + "\n", style=f"bold {COLOR_ERROR}")
            deletions += 1
        else:
            diff_text.append(clean + "\n", style=f"dim {COLOR_WHITE}")

    header = title or f"Diff: {filename} (+{additions} / -{deletions})"
    panel = Panel(
        diff_text,
        title=f"[bold {COLOR_BLUE}]{header}[/]",
        title_align="left",
        border_style=COLOR_BORDER,
        box=ROUNDED,
    )
    console.print(panel)


def format_file_preview(filename: str, content: str, language: str = "text", line_numbers: bool = True) -> Panel:
    """Format file content with syntax highlighting in a FireBox panel."""
    syntax = Syntax(content, language, theme="monokai", line_numbers=line_numbers, word_wrap=True)
    return Panel(
        syntax,
        title=f"[bold {COLOR_BLUE}]📄 {filename}[/]",
        title_align="left",
        border_style=COLOR_BORDER,
        box=ROUNDED,
    )
