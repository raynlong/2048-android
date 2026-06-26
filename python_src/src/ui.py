"""Kivy UI for 2048 — board, tiles, scores, toggles, and overlays.

Full Chinese localization with dark mode, sound toggle, and one-hand
friendly layout (board pushed toward bottom of screen).
"""

from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.metrics import dp, sp
from kivy.clock import Clock

from .constants import GRID_SIZE, BOARD_BOTTOM_MARGIN
from .game_manager import GameManager


# ── Color Helper ───────────────────────────────────────────────────

def _rgba(rgb, a=1.0):
    """Convert (R,G,B) or (R,G,B,A) tuple to 0–1 range for Kivy."""
    if len(rgb) == 4:
        return (rgb[0] / 255, rgb[1] / 255, rgb[2] / 255, rgb[3])
    return (rgb[0] / 255, rgb[1] / 255, rgb[2] / 255, a)


# ── Tile Widget ────────────────────────────────────────────────────

class TileWidget(Label):
    """A single tile on the board with rounded background."""

    def __init__(self, value, grid_x, grid_y, dark_mode, **kwargs):
        super().__init__(**kwargs)
        self.value = value
        self.grid_x = grid_x
        self.grid_y = grid_y
        self._dark = dark_mode
        self.font_name = "Roboto"
        self._update_appearance()
        self.bind(size=self._redraw_bg, pos=self._redraw_bg)

    def _update_appearance(self):
        self.text = str(self.value)
        length = len(self.text)
        if length <= 2:
            self.font_size = sp(32)
        elif length == 3:
            self.font_size = sp(26)
        elif length == 4:
            self.font_size = sp(20)
        else:
            self.font_size = sp(16)

        # Text color: dark text for low values in light mode,
        # very dark text on the specially-darkened tile-2/tile-4 in dark mode
        tt = self._dark.colors["tile_text"]
        if self.value <= tt["dark_threshold"]:
            self.color = _rgba(tt["dark"])
        else:
            self.color = _rgba(tt["light"])

    def _redraw_bg(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            tile_bg = self._dark.colors["tile_bg"]
            if self.value <= 2048:
                bg = tile_bg.get(self.value, tile_bg[2048])
            else:
                bg = self._dark.colors["supertile_bg"]
            Color(*_rgba(bg))
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(6)])


# ── Score Box ──────────────────────────────────────────────────────

class ScoreBox(BoxLayout):
    """Score display: label on top, value below, with min-width to prevent jumping."""

    def __init__(self, title, dark_mode, **kwargs):
        super().__init__(orientation="vertical", **kwargs)
        self._dark = dark_mode

        label_color = _rgba(self._dark.colors["label"])
        self.title_label = Label(
            text=title,
            font_size=sp(10),
            color=label_color,
            size_hint_y=0.35,
            halign="center", valign="middle",
        )
        self.title_label.bind(size=self.title_label.setter("text_size"))

        value_color = _rgba(self._dark.colors["text_light"])
        self.value_label = Label(
            text="0",
            font_size=sp(18),
            bold=True,
            color=value_color,
            size_hint_y=0.65,
            halign="center", valign="middle",
        )
        self.value_label.bind(size=self.value_label.setter("text_size"))

        self.add_widget(self.title_label)
        self.add_widget(self.value_label)

        self.bind(size=self._redraw_bg, pos=self._redraw_bg)

    def set_value(self, val):
        self.value_label.text = str(val)

    def _redraw_bg(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*_rgba(self._dark.colors["score_bg"]))
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(6)])


# ── Toggle Buttons ─────────────────────────────────────────────────

class SoundToggle(Button):
    """Sound on/off toggle button."""

    def __init__(self, audio_manager, dark_mode, **kwargs):
        super().__init__(**kwargs)
        self.audio = audio_manager
        self._dark = dark_mode
        self.font_name = "Roboto"
        self.font_size = sp(16)
        self.background_normal = ""
        self._refresh()

    def on_press(self):
        self.audio.toggle()
        self._refresh()

    def _refresh(self):
        is_on = self.audio.enabled
        bg = self._dark.colors["score_bg"]
        opacity = 1.0 if is_on else 0.45
        self.background_color = (*_rgba(bg)[:3], opacity)
        self.text = "[b]))) [/b]" if is_on else "[b]--- [/b]"
        self.markup = True
        self.color = _rgba(self._dark.colors["text_light"])


class DarkToggle(Button):
    """Dark/light mode toggle button."""

    def __init__(self, dark_mode, on_toggle_callback, **kwargs):
        super().__init__(**kwargs)
        self._dark = dark_mode
        self._on_toggle = on_toggle_callback
        self.font_name = "Roboto"
        self.font_size = sp(18)
        self.background_normal = ""
        self._refresh()

    def on_press(self):
        self._dark.toggle()
        self._on_toggle()
        self._refresh()

    def _refresh(self):
        bg = self._dark.colors["score_bg"]
        self.background_color = _rgba(bg)
        self.text = "\u263E" if self._dark.enabled else "\u2600"
        self.color = _rgba(self._dark.colors["text_light"])


# ── Header Bar ─────────────────────────────────────────────────────

class HeaderBar(BoxLayout):
    """Top bar: "2048" title, toggles, and score boxes."""

    def __init__(self, audio_manager, dark_mode, on_dark_toggle, **kwargs):
        super().__init__(
            orientation="vertical",
            size_hint_y=None,
            height=dp(130),
            padding=[dp(12), dp(6)],
            spacing=dp(8),
            **kwargs
        )

        # Row 1: title + controls
        row1 = BoxLayout(
            orientation="horizontal",
            size_hint_y=0.55,
            spacing=dp(8),
        )

        self.title = Label(
            text="2048",
            font_size=sp(48),
            bold=True,
            color=_rgba(dark_mode.colors["text_dark"]),
            size_hint_x=0.28,
            halign="left", valign="middle",
        )
        self.title.bind(size=self.title.setter("text_size"))

        self.sound_btn = SoundToggle(
            audio_manager=audio_manager,
            dark_mode=dark_mode,
            size_hint=(None, None),
            size=(dp(44), dp(44)),
        )

        self.dark_btn = DarkToggle(
            dark_mode=dark_mode,
            on_toggle_callback=on_dark_toggle,
            size_hint=(None, None),
            size=(dp(44), dp(44)),
        )

        self.score_box = ScoreBox("\u5f97\u5206", dark_mode, size_hint_x=0.28)
        self.best_box = ScoreBox("\u6700\u9ad8", dark_mode, size_hint_x=0.28)

        row1.add_widget(self.title)
        row1.add_widget(self.sound_btn)
        row1.add_widget(self.dark_btn)
        row1.add_widget(self.score_box)
        row1.add_widget(self.best_box)

        self.add_widget(row1)

    def update_scores(self, score, best):
        self.score_box.set_value(score)
        self.best_box.set_value(best)


# ── Game Board Widget ──────────────────────────────────────────────

class GameBoard(Widget):
    """The 4x4 game board with canvas-drawn grid and tile widgets."""

    def __init__(self, dark_mode, **kwargs):
        super().__init__(**kwargs)
        self._dark = dark_mode
        self._tile_widgets = {}
        self._overlay = None
        self._touch_start = None
        self._touch_threshold = dp(15)
        self.bind(size=self._redraw_board, pos=self._redraw_board)

    # ── Public API ──────────────────────────────────────────────────

    def update_board(self, game: GameManager):
        """Sync tile widgets with current game state."""
        for key in list(self._tile_widgets.keys()):
            w = self._tile_widgets.pop(key)
            self.remove_widget(w)

        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                tile = game.grid.cell_content(x, y)
                if tile:
                    px, py, size = self._cell_to_pixel(x, y)
                    tw = TileWidget(
                        value=tile.value,
                        grid_x=x, grid_y=y,
                        dark_mode=self._dark,
                        size=(size, size),
                        pos=(px, py),
                    )
                    self._tile_widgets[(x, y)] = tw
                    self.add_widget(tw)

        self._update_overlays(game)

    def show_overlay(self, text, buttons):
        """Show overlay with text and action buttons."""
        if self._overlay:
            self.remove_widget(self._overlay)

        overlay = _OverlayWidget(
            text=text, buttons=buttons, dark_mode=self._dark,
            size=self.size, pos=self.pos, size_hint=(None, None),
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
            if self._overlay:
                self._overlay.check_click(touch.x, touch.y)
            return True

        if abs(dx) > abs(dy):
            direction = "right" if dx > 0 else "left"
        else:
            direction = "up" if dy > 0 else "down"

        self.parent.parent.dispatch_move(direction)
        return True

    # ── Overlays ────────────────────────────────────────────────────

    def _update_overlays(self, game: GameManager):
        self.hide_overlay()
        if game.over:
            self.show_overlay("\u6e38\u620f\u7ed3\u675f!", [
                ("\u518d\u6765\u4e00\u5c40", lambda: self.parent.parent.dispatch_action("restart")),
            ])
        elif game.won and not game.keep_playing:
            self.show_overlay("\u606d\u559c\u83b7\u80dc!", [
                ("\u7ee7\u7eed\u6e38\u620f", lambda: self.parent.parent.dispatch_action("keep_playing")),
                ("\u518d\u6765\u4e00\u5c40", lambda: self.parent.parent.dispatch_action("restart")),
            ])

    # ── Coordinate Conversions ──────────────────────────────────────

    def _cell_to_pixel(self, x, y):
        spacing = dp(14)
        board_margin = spacing
        total_spacing = spacing * (GRID_SIZE + 1)
        cell_size = (self.width - total_spacing) / GRID_SIZE
        px = self.x + board_margin + x * (cell_size + spacing)
        py = self.y + board_margin + y * (cell_size + spacing)
        return px, py, cell_size

    # ── Board Background ────────────────────────────────────────────

    def _redraw_board(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*_rgba(self._dark.colors["board"]))
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(8)])

        self.canvas.clear()
        with self.canvas:
            spacing = dp(14)
            total_spacing = spacing * (GRID_SIZE + 1)
            cell_size = (self.width - total_spacing) / GRID_SIZE

            cell_bg = self._dark.colors["tile_bg"].get(0, (205, 193, 180))
            for gx in range(GRID_SIZE):
                for gy in range(GRID_SIZE):
                    px = self.x + spacing + gx * (cell_size + spacing)
                    py = self.y + spacing + gy * (cell_size + spacing)
                    Color(*_rgba(cell_bg))
                    RoundedRectangle(
                        pos=(px, py), size=(cell_size, cell_size), radius=[dp(6)],
                    )


# ── Overlay Widget ─────────────────────────────────────────────────

class _OverlayWidget(Widget):
    """Semi-transparent overlay for Game Over / You Win messages."""

    def __init__(self, text, buttons, dark_mode, **kwargs):
        super().__init__(**kwargs)
        self._buttons = buttons
        self._dark = dark_mode

        # Background color
        if "\u83b7\u80dc" in text:
            bg = dark_mode.colors["overlay_win_bg"]
        else:
            bg = dark_mode.colors["overlay_lose_bg"]

        with self.canvas:
            Color(*_rgba(bg, 0.82))
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(8)])

        # Message
        msg_color = (1, 1, 1, 1)
        self.msg = Label(
            text=text,
            font_size=sp(36),
            bold=True,
            color=msg_color,
            size_hint=(None, None),
            halign="center", valign="middle",
        )
        self.msg.bind(size=self.msg.setter("text_size"))
        self.add_widget(self.msg)

        # Buttons
        btn_color = _rgba(dark_mode.colors["restart_bg"])
        btn_text = _rgba(dark_mode.colors["button_text"])
        self.btn_widgets = []
        for i, (label, callback) in enumerate(buttons):
            btn = Button(
                text=label,
                font_size=sp(14),
                color=btn_text,
                background_color=btn_color,
                background_normal="",
                size_hint=(None, None),
                size=(dp(130), dp(42)),
            )
            btn.bind(on_release=lambda _, cb=callback: cb())
            self.add_widget(btn)
            self.btn_widgets.append(btn)

        self.bind(size=self._layout, pos=self._layout)

    def _layout(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

        cx = self.x + self.width / 2
        cy = self.y + self.height / 2

        n_btns = len(self.btn_widgets)
        if n_btns == 1:
            self.msg.size = (self.width * 0.8, dp(50))
            self.msg.pos = (cx - self.msg.width / 2, cy + dp(10))
            self.btn_widgets[0].pos = (cx - dp(65), cy - dp(40))
        else:
            self.msg.size = (self.width * 0.8, dp(50))
            self.msg.pos = (cx - self.msg.width / 2, cy + dp(15))
            total_w = n_btns * dp(130) + (n_btns - 1) * dp(15)
            start_x = cx - total_w / 2
            for i, btn in enumerate(self.btn_widgets):
                btn.pos = (start_x + i * (dp(130) + dp(15)), cy - dp(40))

    def check_click(self, x, y):
        for btn in self.btn_widgets:
            if btn.collide_point(x, y):
                btn.dispatch("on_release")
                return True
        return False


# ── Main Game Screen ───────────────────────────────────────────────

class GameScreen(BoxLayout):
    """Top-level layout: header at top, board pushed toward bottom for one-hand use."""

    def __init__(self, game, storage, audio_manager, dark_mode, **kwargs):
        super().__init__(
            orientation="vertical",
            padding=[0, 0, 0, 0],
            spacing=0,
            **kwargs
        )
        self.game = game
        self.storage = storage
        self.audio = audio_manager
        self._dark = dark_mode

        self._build_ui()
        self._refresh()

    def _build_ui(self):
        # --- Header (fixed height at top) ---
        self.header = HeaderBar(
            audio_manager=self.audio,
            dark_mode=self._dark,
            on_dark_toggle=self._apply_dark_mode,
            size_hint_y=None,
            height=dp(130),
        )
        self.add_widget(self.header)

        # --- Above-game action bar ---
        action_bar = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(42),
            padding=[dp(12), 0],
            spacing=dp(10),
        )
        restart_btn = Button(
            text="\u65b0\u6e38\u620f",
            font_size=sp(12),
            bold=True,
            color=_rgba(self._dark.colors["text_light"]),
            background_color=_rgba(self._dark.colors["restart_bg"]),
            background_normal="",
            size_hint=(None, None),
            size=(dp(90), dp(34)),
            pos_hint={"center_y": 0.5},
        )
        restart_btn.bind(on_release=lambda _: self.dispatch_action("restart"))
        self._restart_btn = restart_btn
        action_bar.add_widget(restart_btn)
        action_bar.add_widget(Widget(size_hint_x=1))
        self._action_bar = action_bar
        self.add_widget(action_bar)

        # --- Spacer to push board to bottom ---
        self._spacer = Widget(size_hint_y=1)
        self.add_widget(self._spacer)

        # --- Board area (square, auto-sized, at bottom with margin) ---
        board_container = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            padding=[dp(12), 0, dp(12), dp(BOARD_BOTTOM_MARGIN)],
        )
        self.board = GameBoard(
            dark_mode=self._dark,
            size_hint=(1, None),
        )
        # Bind board size to maintain square aspect
        self.board.bind(width=self._resize_board)
        board_container.add_widget(self.board)
        self._board_container = board_container
        self.add_widget(board_container)

    def _resize_board(self, instance, width):
        """Keep board square and sized to fit."""
        # Board height = width (square), capped by available space
        max_h = self._board_container.height - dp(BOARD_BOTTOM_MARGIN)
        side = min(width, max_h)
        instance.height = side

    def _refresh(self):
        """Sync all UI with game state."""
        best = self.storage.get_best_score()
        if self.game.score > best:
            best = self.game.score
            self.storage.set_best_score(best)
        self.header.update_scores(self.game.score, best)
        self.board.update_board(self.game)

    def _apply_dark_mode(self):
        """Refresh all colors after dark mode toggle."""
        # Update Window background
        self._dark.apply_window_color(Window)

        # Rebuild visual elements affected by dark mode
        # (Redraw header button colors)
        self.header.sound_btn._dark = self._dark
        self.header.sound_btn._refresh()
        self.header.dark_btn._dark = self._dark
        self.header.dark_btn._refresh()
        self.header.title.color = _rgba(self._dark.colors["text_dark"])
        self._restart_btn.background_color = _rgba(self._dark.colors["restart_bg"])
        self._restart_btn.color = _rgba(self._dark.colors["text_light"])

        # Force board redraw
        self.board._dark = self._dark
        self.board._redraw_board()
        self.board.update_board(self.game)

        # Header score boxes
        self.header.score_box._dark = self._dark
        self.header.best_box._dark = self._dark
        self._refresh()

    def dispatch_move(self, direction):
        """Handle a swipe / keyboard action."""
        self.game.move(direction)
        self._refresh()
        self.storage.set_game_state(self.game.serialize())

    def dispatch_action(self, action):
        """Handle restart / keep_playing."""
        if action == "restart":
            self.game.restart()
            self.storage.clear_game_state()
        elif action == "keep_playing":
            self.game.keep_playing_action()
        self._refresh()


# Import at bottom to avoid circular dependency
from kivy.core.window import Window
