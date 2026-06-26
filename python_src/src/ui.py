"""Kivy UI for 2048 — board, tiles, scores, and overlays.

Replicates the visual design of the original 2048, adapted for Kivy
so it runs on desktop and Android.
"""

from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.properties import NumericProperty, ObjectProperty
from kivy.clock import Clock

from .constants import (
    GRID_SIZE, TILE_COLORS, SUPER_TILE_BG, SUPER_TILE_TEXT,
    TEXT_DARK, TEXT_LIGHT, BG_COLOR, BOARD_COLOR, SCORE_BG,
)
from .game_manager import GameManager
from .tile import Tile


# ── Color Helper ───────────────────────────────────────────────────

def _rgba(rgb, a=1.0):
    """Convert (R,G,B) tuple to (R/255, G/255, B/255, a)."""
    if len(rgb) == 4:
        return (rgb[0] / 255, rgb[1] / 255, rgb[2] / 255, rgb[3])
    return (rgb[0] / 255, rgb[1] / 255, rgb[2] / 255, a)


# ── Tile Widget ────────────────────────────────────────────────────

class TileWidget(Label):
    """A single tile on the board — Kivy Label with rounded bg."""

    def __init__(self, value, grid_x, grid_y, **kwargs):
        super().__init__(**kwargs)
        self.value = value
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.font_name = "Roboto"
        self._update_appearance()
        self.bind(size=self._redraw_bg, pos=self._redraw_bg)

    def _update_appearance(self):
        """Set text, font size, and colors based on tile value."""
        self.text = str(self.value)

        # Font size scales with digit count
        length = len(str(self.value))
        if length <= 2:
            self.font_size = sp(32)
        elif length == 3:
            self.font_size = sp(26)
        elif length == 4:
            self.font_size = sp(20)
        else:
            self.font_size = sp(16)

        if self.value <= 4:
            self.color = _rgba(TEXT_DARK)
        else:
            self.color = _rgba(TEXT_LIGHT)

    def _redraw_bg(self, *args):
        """Redraw the rounded-rectangle background."""
        self.canvas.before.clear()
        with self.canvas.before:
            if self.value <= 2048:
                bg = TILE_COLORS.get(self.value, TILE_COLORS[2048])
            else:
                bg = SUPER_TILE_BG
            Color(*_rgba(bg))
            RoundedRectangle(
                pos=self.pos, size=self.size,
                radius=[dp(6)],
            )


# ── Score Box ──────────────────────────────────────────────────────

class ScoreBox(BoxLayout):
    """Score display box: label on top, value below."""

    def __init__(self, title, **kwargs):
        super().__init__(orientation="vertical", **kwargs)
        self.title_label = Label(
            text=title,
            font_size=sp(11),
            color=_rgba((238, 228, 218)),
            size_hint_y=0.35,
            halign="center", valign="middle",
        )
        self.title_label.bind(size=self.title_label.setter("text_size"))
        self.value_label = Label(
            text="0",
            font_size=sp(20),
            bold=True,
            color=_rgba(TEXT_LIGHT),
            size_hint_y=0.65,
            halign="center", valign="middle",
        )
        self.value_label.bind(size=self.value_label.setter("text_size"))
        self.add_widget(self.title_label)
        self.add_widget(self.value_label)
        self._draw_bg()

    def set_value(self, val):
        self.value_label.text = str(val)

    def _draw_bg(self, *args):
        self.bind(size=self._redraw, pos=self._redraw)

    def _redraw(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*_rgba(SCORE_BG))
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(6)])


# ── Header Bar ─────────────────────────────────────────────────────

class HeaderBar(BoxLayout):
    """Top bar: "2048" title + score boxes."""

    def __init__(self, **kwargs):
        super().__init__(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(80),
            padding=[dp(15), dp(8)],
            spacing=dp(10),
            **kwargs
        )
        self.title = Label(
            text="2048",
            font_size=sp(56),
            bold=True,
            color=_rgba(TEXT_DARK),
            size_hint_x=0.4,
            halign="left", valign="middle",
        )
        self.title.bind(size=self.title.setter("text_size"))

        self.score_box = ScoreBox("SCORE", size_hint_x=0.3)
        self.best_box = ScoreBox("BEST", size_hint_x=0.3)

        self.add_widget(self.title)
        self.add_widget(self.score_box)
        self.add_widget(self.best_box)


# ── Game Board Widget ──────────────────────────────────────────────

class GameBoard(Widget):
    """The 4x4 game board with canvas drawing and tile widgets."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._tile_widgets = {}  # (x, y) -> TileWidget
        self._overlay = None
        self._touch_start = None
        self._touch_threshold = dp(15)
        self.bind(size=self._redraw_board, pos=self._redraw_board)

    # ── Public API ──────────────────────────────────────────────────

    def update_board(self, game: GameManager):
        """Sync all tile widgets with the current game state."""
        # Remove old tiles
        for key in list(self._tile_widgets.keys()):
            w = self._tile_widgets.pop(key)
            self.remove_widget(w)

        # Add tiles from grid
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                tile = game.grid.cell_content(x, y)
                if tile:
                    px, py, size = self._cell_to_pixel(x, y)
                    tw = TileWidget(
                        value=tile.value,
                        grid_x=x, grid_y=y,
                        size=(size, size),
                        pos=(px, py),
                    )
                    self._tile_widgets[(x, y)] = tw
                    self.add_widget(tw)

        # Show/hide overlays
        self._update_overlays(game)

    def show_overlay(self, text, sub_text, buttons):
        """Show a semi-transparent overlay with message and buttons.

        buttons: list of (text, callback) tuples.
        """
        if self._overlay:
            self.remove_widget(self._overlay)

        overlay = _OverlayWidget(
            text=text,
            sub_text=sub_text,
            buttons=buttons,
            size=self.size,
            pos=self.pos,
            size_hint=(None, None),
        )
        self._overlay = overlay
        self.add_widget(overlay)

    def hide_overlay(self):
        if self._overlay:
            self.remove_widget(self._overlay)
            self._overlay = None

    # ── Touch / Swipe ───────────────────────────────────────────────

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self._touch_start = (touch.x, touch.y)
            return True
        return False

    def on_touch_up(self, touch):
        if self._touch_start is None:
            return False

        dx = touch.x - self._touch_start[0]
        dy = touch.y - self._touch_start[1]
        self._touch_start = None

        if abs(dx) < self._touch_threshold and abs(dy) < self._touch_threshold:
            # Tap - check if it hit an overlay button
            if self._overlay:
                self._overlay.check_click(touch.x, touch.y)
            return True

        # Detect swipe direction
        if abs(dx) > abs(dy):
            direction = "right" if dx > 0 else "left"
        else:
            direction = "up" if dy > 0 else "down"

        # Dispatch via custom event
        self.parent.parent.dispatch_move(direction)
        return True

    # ── Overlays ────────────────────────────────────────────────────

    def _update_overlays(self, game: GameManager):
        self.hide_overlay()
        if game.over:
            self.show_overlay(
                "Game Over!",
                "",
                [
                    ("Try Again", lambda: self.parent.parent.dispatch_action("restart")),
                ],
            )
        elif game.won and not game.keep_playing:
            self.show_overlay(
                "You Win!",
                "",
                [
                    ("Keep Playing", lambda: self.parent.parent.dispatch_action("keep_playing")),
                    ("Try Again", lambda: self.parent.parent.dispatch_action("restart")),
                ],
            )

    # ── Coordinate Conversions ──────────────────────────────────────

    def _cell_to_pixel(self, x: int, y: int):
        """Convert grid coords to pixel position + size."""
        spacing = dp(15)
        board_margin = spacing
        total_spacing = spacing * (GRID_SIZE + 1)
        cell_size = (self.width - total_spacing) / GRID_SIZE
        px = self.x + board_margin + x * (cell_size + spacing)
        py = self.y + board_margin + y * (cell_size + spacing)
        return px, py, cell_size

    # ── Board Background Drawing ────────────────────────────────────

    def _redraw_board(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            # Board background
            Color(*_rgba(BOARD_COLOR))
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(8)])

        # Draw empty cell placeholders on a separate canvas layer
        self.canvas.clear()
        with self.canvas:
            spacing = dp(15)
            total_spacing = spacing * (GRID_SIZE + 1)
            cell_size = (self.width - total_spacing) / GRID_SIZE

            for gx in range(GRID_SIZE):
                for gy in range(GRID_SIZE):
                    px = self.x + spacing + gx * (cell_size + spacing)
                    py = self.y + spacing + gy * (cell_size + spacing)
                    Color(*_rgba((205, 193, 180)))
                    RoundedRectangle(
                        pos=(px, py),
                        size=(cell_size, cell_size),
                        radius=[dp(6)],
                    )


# ── Overlay Widget ─────────────────────────────────────────────────

class _OverlayWidget(Widget):
    """Semi-transparent overlay for Game Over / You Win."""

    def __init__(self, text, sub_text, buttons, **kwargs):
        super().__init__(**kwargs)
        self._buttons = buttons
        self._button_rects = []

        # Draw overlay background
        with self.canvas:
            if "Win" in text:
                Color(*_rgba((237, 194, 46), 0.75))
            else:
                Color(*_rgba((238, 228, 218), 0.75))
            self.bg_rect = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[dp(8)],
            )

        # Message label
        color = (1, 1, 1, 1) if "Win" in text else _rgba(TEXT_DARK)
        self.msg = Label(
            text=text,
            font_size=sp(36),
            bold=True,
            color=color,
            size_hint=(None, None),
            halign="center", valign="middle",
        )
        self.msg.bind(size=self.msg.setter("text_size"))
        self.add_widget(self.msg)

        # Sub message
        if sub_text:
            self.sub = Label(
                text=sub_text,
                font_size=sp(16),
                color=color,
                size_hint=(None, None),
                halign="center", valign="middle",
            )
            self.sub.bind(size=self.sub.setter("text_size"))
            self.add_widget(self.sub)

        # Buttons
        self.btn_widgets = []
        for i, (label, callback) in enumerate(buttons):
            btn = Button(
                text=label,
                font_size=sp(14),
                color=(1, 1, 1, 1),
                background_color=_rgba((143, 122, 102)),
                background_normal="",
                size_hint=(None, None),
                size=(dp(130), dp(42)),
            )
            btn.bind(on_release=lambda _, cb=callback: cb())
            self.add_widget(btn)
            self.btn_widgets.append(btn)

        self.bind(size=self._layout, pos=self._layout)

    def _layout(self, *args):
        """Position the message and buttons."""
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

        cx = self.x + self.width / 2
        cy = self.y + self.height / 2

        n_btns = len(self.btn_widgets)
        if n_btns == 1:
            self.msg.size = (self.width * 0.8, dp(50))
            self.msg.pos = (cx - self.msg.width / 2, cy + dp(10))
            btn = self.btn_widgets[0]
            btn.pos = (cx - btn.width / 2, cy - dp(40))
        else:
            self.msg.size = (self.width * 0.8, dp(50))
            self.msg.pos = (cx - self.msg.width / 2, cy + dp(15))
            total_w = n_btns * dp(130) + (n_btns - 1) * dp(15)
            start_x = cx - total_w / 2
            for i, btn in enumerate(self.btn_widgets):
                btn.pos = (start_x + i * (dp(130) + dp(15)), cy - dp(40))

    def check_click(self, x, y):
        """Check if a point hits any button."""
        for btn in self.btn_widgets:
            if btn.collide_point(x, y):
                btn.dispatch("on_release")
                return True
        return False


# ── Main Game Screen ───────────────────────────────────────────────

class GameScreen(BoxLayout):
    """Top-level layout: header + board."""

    def __init__(self, game, storage, **kwargs):
        super().__init__(
            orientation="vertical",
            padding=[0, dp(10), 0, 0],
            spacing=0,
            **kwargs
        )
        self.game = game
        self.storage = storage

        # Header
        self.header = HeaderBar(size_hint_y=None, height=dp(80))
        self.add_widget(self.header)

        # Board
        self.board = GameBoard(size_hint=(1, 1))
        self.add_widget(self.board)

        # Init display
        self._refresh()

    def _refresh(self):
        """Update all UI elements from game state."""
        self.header.score_box.set_value(self.game.score)
        self.board.update_board(self.game)
        self._update_best_score()

    def _update_best_score(self):
        best = self.storage.get_best_score()
        if self.game.score > best:
            best = self.game.score
            self.storage.set_best_score(best)
        self.header.best_box.set_value(best)

    def dispatch_move(self, direction):
        """Handle a swipe / keyboard move action."""
        self.game.move(direction)
        self._refresh()
        # Auto-save
        self.storage.set_game_state(self.game.serialize())

    def dispatch_action(self, action):
        """Handle restart / keep_playing actions."""
        if action == "restart":
            self.game.restart()
            self.storage.clear_game_state()
        elif action == "keep_playing":
            self.game.keep_playing_action()
        self._refresh()
