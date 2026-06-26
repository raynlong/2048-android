"""Dark mode manager for 2048.

Handles color schemes and persistence for dark/light mode switching.
Dark mode reduces eye strain with deep blue-black background and
adjusted tile/text colors for readability.
"""

import os
import tempfile

PREF_FILE = "2048_dark_pref.txt"


# ── Light mode colors (original 2048 palette) ──────────────────────

LIGHT_COLORS = {
    "bg": (250, 248, 239),
    "board": (187, 173, 160),
    "score_bg": (187, 173, 160),
    "text_dark": (119, 110, 101),
    "text_light": (249, 246, 242),
    "label": (119, 110, 101),
    "restart_bg": (143, 122, 102),
    "button_text": (238, 228, 218),
    # Tile backgrounds by value
    "tile_bg": {
        0: (205, 193, 180, 0),
        2: (238, 228, 218),
        4: (237, 224, 200),
        8: (242, 177, 121),
        16: (245, 149, 99),
        32: (246, 124, 95),
        64: (246, 94, 59),
        128: (237, 207, 114),
        256: (237, 204, 97),
        512: (237, 200, 80),
        1024: (237, 197, 63),
        2048: (237, 194, 46),
    },
    "supertile_bg": (60, 58, 50),
    # Tile text colors: (dark_threshold, dark_color, light_color)
    "tile_text": {
        "dark_threshold": 4,
        "dark": (119, 110, 101),
        "light": (249, 246, 242),
    },
    # Overlay
    "overlay_win_bg": (237, 194, 46),
    "overlay_lose_bg": (238, 228, 218),
}


# ── Dark mode colors ───────────────────────────────────────────────

DARK_COLORS = {
    "bg": (18, 18, 32),
    "board": (90, 82, 72),
    "score_bg": (50, 50, 65),
    "text_dark": (201, 192, 179),
    "text_light": (249, 246, 242),
    "label": (170, 160, 150),
    "restart_bg": (100, 85, 70),
    "button_text": (220, 215, 210),
    # Tile backgrounds: low values darker/greyer for contrast
    "tile_bg": {
        0: (30, 30, 50, 0),
        2: (90, 85, 75),
        4: (95, 82, 65),
        8: (242, 177, 121),
        16: (245, 149, 99),
        32: (246, 124, 95),
        64: (246, 94, 59),
        128: (237, 207, 114),
        256: (237, 204, 97),
        512: (237, 200, 80),
        1024: (237, 197, 63),
        2048: (237, 194, 46),
    },
    "supertile_bg": (40, 38, 35),
    # Tile text: low-value tiles (≤4) use very dark text for visibility
    "tile_text": {
        "dark_threshold": 4,
        "dark": (50, 42, 35),
        "light": (249, 246, 242),
    },
    # Overlay
    "overlay_win_bg": (190, 155, 40),
    "overlay_lose_bg": (60, 55, 48),
}


class DarkModeManager:
    """Manages dark/light mode state and provides current color scheme."""

    def __init__(self):
        self._dark = False
        self._load_preference()

    # ── Properties ──────────────────────────────────────────────────

    @property
    def enabled(self):
        return self._dark

    @property
    def colors(self):
        """Return the current color dictionary based on mode."""
        return DARK_COLORS if self._dark else LIGHT_COLORS

    def get(self, key, default=None):
        """Get a color value from the current scheme."""
        return self.colors.get(key, default)

    # ── Actions ─────────────────────────────────────────────────────

    def toggle(self):
        """Toggle between dark and light mode. Returns new state."""
        self._dark = not self._dark
        self._save_preference()
        return self._dark

    def apply_window_color(self, window):
        """Apply background color to Kivy Window."""
        c = self.colors["bg"]
        window.clearcolor = (c[0] / 255, c[1] / 255, c[2] / 255, 1)

    # ── Persistence ─────────────────────────────────────────────────

    def _load_preference(self):
        try:
            path = os.path.join(tempfile.gettempdir(), PREF_FILE)
            if os.path.exists(path):
                with open(path, "r") as f:
                    self._dark = f.read().strip() == "1"
        except OSError:
            self._dark = False

    def _save_preference(self):
        try:
            path = os.path.join(tempfile.gettempdir(), PREF_FILE)
            with open(path, "w") as f:
                f.write("1" if self._dark else "0")
        except OSError:
            pass
