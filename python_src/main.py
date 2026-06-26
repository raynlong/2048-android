"""2048 Game — Kivy version for desktop and Android.

A complete Python/Kivy port of the 2048 game, faithfully replicating
the original's game logic and visual design with Chinese localization.

Features:
    - Swipe / Arrow Keys / WASD / HJKL — Move tiles
    - R — Restart
    - Sound effects (slide + merge, toggleable)
    - Dark mode (toggleable, persistent)
    - Score & best score persistence
    - One-hand friendly layout (board near bottom)
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kivy.app import App
from kivy.core.window import Window
from kivy.config import Config

# Disable multi-touch emulation (red dots on right-click)
Config.set("input", "mouse", "mouse,disable_multitouch")

from src.game_manager import GameManager
from src.storage import StorageManager
from src.audio_manager import AudioManager
from src.dark_mode import DarkModeManager
from src.ui import GameScreen


class Game2048App(App):
    """Main Kivy application for 2048."""

    def build(self):
        # Audio & dark mode managers
        self.audio = AudioManager()
        self._dark = DarkModeManager()

        # Window setup
        self._dark.apply_window_color(Window)
        Window.minimum_width = 320
        Window.minimum_height = 480

        # Keyboard
        self._keyboard = Window.request_keyboard(self._on_keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_key_down)

        # Load / create game
        self.storage = StorageManager()
        saved_state = self.storage.get_game_state()
        if saved_state:
            self.game = GameManager(saved_state)
        else:
            self.game = GameManager()

        # Wire sound callbacks
        self.game.on_move = self.audio.play_move
        self.game.on_merge = self.audio.play_merge

        return GameScreen(
            game=self.game,
            storage=self.storage,
            audio_manager=self.audio,
            dark_mode=self._dark,
        )

    def on_stop(self):
        """Save game state when app closes."""
        if not self.game.over:
            self.storage.set_game_state(self.game.serialize())
        best = max(self.storage.get_best_score(), self.game.score)
        self.storage.set_best_score(best)

    def _on_keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_key_down)
        self._keyboard = None

    def _on_key_down(self, keyboard, keycode, text, modifiers):
        """Handle keyboard input."""
        key = keycode[1]

        direction_map = {
            "up": "up", "down": "down", "left": "left", "right": "right",
            "w": "up", "s": "down", "a": "left", "d": "right",
            "k": "up", "j": "down", "h": "left", "l": "right",
        }

        if key in direction_map:
            self.root.dispatch_move(direction_map[key])
        elif key == "r":
            self.root.dispatch_action("restart")
        elif key == "escape":
            self.stop()

        return True


if __name__ == "__main__":
    Game2048App().run()
