"""Save/Load game state to a local JSON file.

Works on desktop (Windows/Mac/Linux) and Android.
"""

import json
import os
from typing import Optional


def _get_app_dir() -> str:
    """Get the application data directory, cross-platform."""
    try:
        # Android: use the app's private files directory
        from android.storage import app_storage_path
        return app_storage_path()
    except ImportError:
        pass

    # Desktop: use a directory next to the script or in user home
    # Try Kivy's user_data_dir first
    try:
        from kivy.app import App
        app = App.get_running_app()
        if app and app.user_data_dir:
            return app.user_data_dir
    except Exception:
        pass

    # Fallback: same directory as the game
    return os.path.dirname(os.path.abspath(__file__))


def get_save_path() -> str:
    """Get the path to the save file."""
    app_dir = _get_app_dir()
    return os.path.join(app_dir, "2048_save.json")


class StorageManager:
    """Handles persistence of game state and high score."""

    def __init__(self):
        self.save_path = get_save_path()

    def get_best_score(self) -> int:
        """Retrieve the best score from storage."""
        data = self._load()
        return data.get("best_score", 0) if data else 0

    def set_best_score(self, score: int):
        """Update the best score if higher."""
        data = self._load() or {}
        data["best_score"] = max(data.get("best_score", 0), score)
        self._save(data)

    def get_game_state(self) -> Optional[dict]:
        """Retrieve saved game state."""
        data = self._load()
        if data and "game_state" in data:
            return data["game_state"]
        return None

    def set_game_state(self, state: dict):
        """Save the current game state."""
        data = self._load() or {}
        data["game_state"] = state
        self._save(data)

    def clear_game_state(self):
        """Remove saved game (but keep best score)."""
        data = self._load()
        if data:
            data.pop("game_state", None)
            self._save(data)

    def _load(self) -> Optional[dict]:
        """Load the JSON file."""
        if not os.path.exists(self.save_path):
            return None
        try:
            with open(self.save_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None

    def _save(self, data: dict):
        """Save data to the JSON file."""
        try:
            with open(self.save_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except IOError:
            pass  # Silently fail on save errors
