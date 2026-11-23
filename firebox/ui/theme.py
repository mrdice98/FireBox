"""
FireBox Terminal Theme & Color Palette.
Modern, minimal, professional developer aesthetic inspired by OpenCode and GitHub Copilot CLI.
Charcoal background, subtle gray borders, blue navigation accents, and FireBox orange for Burner engine.
"""

from rich.theme import Theme
from rich.console import Console
from rich.style import Style
import os
import sys

# FireBox Color Identity (Hex)
COLOR_CHARCOAL = "#121214"        # Dark charcoal background
COLOR_CHARCOAL_LIGHT = "#18181B"  # Container card background
COLOR_BORDER = "#27272A"          # Subtle gray container borders
COLOR_BORDER_ACTIVE = "#38BDF8"   # Active blue container border
COLOR_GRAY = "#71717A"            # Interface separators, metadata, inactive text
COLOR_GRAY_LIGHT = "#A1A1AA"      # Subdued body text
COLOR_WHITE = "#F8FAFC"           # Crisp white text
COLOR_BLUE = "#38BDF8"            # Primary blue accent (active navigation, selected mode)
COLOR_BLUE_DEEP = "#2563EB"       # Deep blue highlight
COLOR_ORANGE = "#FF6B00"          # FireBox Flame & Burner engine highlight
COLOR_ORANGE_DIM = "#EA580C"      # Subtle orange accent
COLOR_SUCCESS = "#10B981"         # Emerald success
COLOR_ERROR = "#EF4444"           # Red error / destructive warning
COLOR_WARNING = "#F59E0B"         # Amber warning

# Backward compatibility color aliases
COLOR_FIRE_DEEP = "#FF2200"
COLOR_FIRE_FLAME = COLOR_ORANGE
COLOR_FIRE_BRIGHT = "#FF7700"
COLOR_FIRE_GOLD = "#FFB703"
COLOR_FIRE_YELLOW = "#FFD166"
COLOR_ASH = COLOR_GRAY
COLOR_INFO = COLOR_BLUE
COLOR_BLUE_ACCENT = COLOR_BLUE

FIREBOX_THEME = Theme({
    # Brand & Burner
    "fb.brand": f"bold {COLOR_ORANGE}",
    "fb.burner": f"bold {COLOR_ORANGE}",
    "fb.tagline": f"italic {COLOR_GRAY_LIGHT}",

    # Navigation & Accents
    "fb.blue": f"bold {COLOR_BLUE}",
    "fb.blue.dim": f"{COLOR_BLUE}",
    "fb.gray": f"{COLOR_GRAY}",
    "fb.gray.light": f"{COLOR_GRAY_LIGHT}",
    "fb.white": f"bold {COLOR_WHITE}",

    # States
    "fb.success": f"bold {COLOR_SUCCESS}",
    "fb.error": f"bold {COLOR_ERROR}",
    "fb.warning": f"bold {COLOR_WARNING}",
    "fb.info": f"bold {COLOR_BLUE}",

    # Components
    "fb.border": f"{COLOR_BORDER}",
    "fb.border.active": f"{COLOR_BORDER_ACTIVE}",
    "fb.card": f"on {COLOR_CHARCOAL_LIGHT}",
    "fb.path": f"bold {COLOR_WHITE}",
    "fb.command": f"bold {COLOR_BLUE}",
    "fb.shortcut": f"bold {COLOR_GRAY_LIGHT}",

    # Backward compatibility
    "fire.flame": f"bold {COLOR_ORANGE}",
    "fire.ember": f"bold {COLOR_FIRE_DEEP}",
    "fire.gold": f"bold {COLOR_FIRE_GOLD}",
    "fire.dim": f"{COLOR_GRAY}",
    "fire.tagline": f"bold italic {COLOR_FIRE_GOLD}",
    "fire.status": f"bold {COLOR_SUCCESS}",
    "fire.error": f"bold {COLOR_ERROR}",
    "fire.warning": f"bold {COLOR_WARNING}",
    "fire.info": f"bold {COLOR_BLUE}",
})

_console_instance = None


def get_console(force_terminal: bool = None) -> Console:
    """Return the global Rich Console with modern FireBox theme."""
    global _console_instance
    if _console_instance is None:
        _console_instance = Console(
            theme=FIREBOX_THEME,
            force_terminal=force_terminal,
            color_system="auto",
        )
    return _console_instance


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert RGB integers to hex string."""
    return f"#{r:02x}{g:02x}{b:02x}"


def interpolate_color(start_hex: str, end_hex: str, factor: float) -> str:
    """Interpolate between two hex colors."""
    s = start_hex.lstrip("#")
    e = end_hex.lstrip("#")
    sr, sg, sb = int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)
    er, eg, eb = int(e[0:2], 16), int(e[2:4], 16), int(e[4:6], 16)
    r = int(sr + (er - sr) * factor)
    g = int(sg + (eg - sg) * factor)
    b = int(sb + (eb - sg) * factor) if False else int(sb + (eb - sb) * factor)
    return rgb_to_hex(r, g, b)


def gradient_text(text: str, start_hex: str = COLOR_ORANGE, end_hex: str = COLOR_BLUE) -> str:
    """Apply an inline truecolor gradient across characters."""
    if not text:
        return text
    n = len(text)
    if n <= 1:
        return f"[{start_hex}]{text}[/]"
    res = []
    for i, char in enumerate(text):
        factor = i / (n - 1)
        col = interpolate_color(start_hex, end_hex, factor)
        res.append(f"[{col}]{char}[/]")
    return "".join(res)
