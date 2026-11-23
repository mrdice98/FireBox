"""
FireBox Terminal Theme & Color Palette.
Ember, flame, gold, and dark cinematic gradients.
"""

from rich.theme import Theme
from rich.console import Console
from rich.style import Style
import os
import sys

# FireBox Color Palette (Hex & RGB)
COLOR_FIRE_DEEP = "#FF2200"       # Deep ember red
COLOR_FIRE_FLAME = "#FF5500"      # Fiery orange
COLOR_FIRE_BRIGHT = "#FF7700"     # Bright flame orange
COLOR_FIRE_GOLD = "#FFB703"       # Luminous gold / ember spark
COLOR_FIRE_YELLOW = "#FFD166"     # Yellow flame tip
COLOR_CHARCOAL = "#121214"        # Dark charcoal background
COLOR_CHARCOAL_LIGHT = "#1E1E24"  # Panel card background
COLOR_ASH = "#71717A"             # Ash gray text
COLOR_WHITE = "#F8FAFC"           # Crisp white text
COLOR_SUCCESS = "#10B981"         # Emerald success
COLOR_ERROR = "#EF4444"           # Red error
COLOR_WARNING = "#F59E0B"         # Amber warning
COLOR_INFO = "#06B6D4"            # Cyan info

FIREBOX_THEME = Theme({
    "fire.flame": f"bold {COLOR_FIRE_FLAME}",
    "fire.ember": f"bold {COLOR_FIRE_DEEP}",
    "fire.gold": f"bold {COLOR_FIRE_GOLD}",
    "fire.bright": f"bold {COLOR_FIRE_BRIGHT}",
    "fire.yellow": f"bold {COLOR_FIRE_YELLOW}",
    "fire.dim": f"{COLOR_ASH}",
    "fire.tagline": f"bold italic {COLOR_FIRE_GOLD}",
    "fire.badge": f"bold black on {COLOR_FIRE_FLAME}",
    "fire.badge.gold": f"bold black on {COLOR_FIRE_GOLD}",
    "fire.badge.ember": f"bold white on {COLOR_FIRE_DEEP}",
    "fire.card": f"on {COLOR_CHARCOAL_LIGHT}",
    "fire.status": f"bold {COLOR_SUCCESS}",
    "fire.error": f"bold {COLOR_ERROR}",
    "fire.warning": f"bold {COLOR_WARNING}",
    "fire.info": f"bold {COLOR_INFO}",
    "fire.path": f"bold {COLOR_FIRE_YELLOW}",
    "fire.command": f"bold {COLOR_FIRE_GOLD}",
    "fire.shortcut": f"bold cyan",
})

_console_instance = None


def get_console(force_terminal: bool = None) -> Console:
    """Return the global Rich Console with FireBox theme."""
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
    b = int(sb + (eb - sb) * factor)
    return rgb_to_hex(r, g, b)


def gradient_text(text: str, start_hex: str = COLOR_FIRE_DEEP, end_hex: str = COLOR_FIRE_YELLOW) -> str:
    """Apply an inline ANSI truecolor or Rich markup gradient across characters."""
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
