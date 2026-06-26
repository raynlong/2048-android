"""Game Manager - core game logic, exact replica of original JS game_manager.js.

Controls the game loop: initialization, tile movement, merging, scoring,
win/loss detection, and state serialization.
"""

import random
from typing import Optional

from .grid import Grid
from .tile import Tile
from .constants import (
    GRID_SIZE, START_TILES, WIN_VALUE, TILE_2_PROB, DIRECTIONS,
)


class GameManager:
    """Main game controller."""

    def __init__(self, previous_state: Optional[dict] = None):
        self.size = GRID_SIZE
        self.start_tiles = START_TILES
        self.score = 0
        self.over = False
        self.won = False
        self.keep_playing = False
        self.moved_this_turn = False

        if previous_state:
            self._load_state(previous_state)
        else:
            self.grid = Grid(self.size)
            self._add_start_tiles()

    # ── Initialization ──────────────────────────────────────────────

    def _add_start_tiles(self):
        """Add initial random tiles at game start."""
        for _ in range(self.start_tiles):
            self._add_random_tile()

    def _add_random_tile(self):
        """Add a tile with random value (90% chance of 2, 10% chance of 4)
        at a random empty position."""
        cell = self.grid.random_available_cell()
        if cell:
            value = 2 if random.random() < TILE_2_PROB else 4
            tile = Tile(cell["x"], cell["y"], value)
            self.grid.insert_tile(tile)
            tile.is_new = True

    # ── Movement (the core algorithm) ───────────────────────────────

    def move(self, direction: str):
        """Execute a move in the given direction.

        Args:
            direction: One of 'up', 'right', 'down', 'left'
        """
        if self._is_game_terminated():
            return

        # Save positions for animation
        self._prepare_tiles()

        vector = DIRECTIONS[direction]
        moved = False
        self.grid, moved = self._process_move(self.grid, vector)

        if moved:
            self.moved_this_turn = True
            self._add_random_tile()

            if not self._moves_available():
                self.over = True

    def _process_move(self, grid: Grid, vector: dict):
        """Process all tiles sliding and merging in one direction.

        Returns (grid, moved_flag).
        """
        traversals = self._build_traversals(vector)
        moved = False

        # Clear merged_from on all tiles before processing
        grid.each_cell(lambda x, y, tile: self._clear_merged(tile))

        # Process each cell in the correct traversal order
        for x in traversals["x"]:
            for y in traversals["y"]:
                tile = grid.cell_content(x, y)
                if tile is None:
                    continue

                farthest, next_pos = self._find_farthest_position(grid, x, y, vector)
                next_tile = grid.cell_content(next_pos["x"], next_pos["y"])

                # Check if we can merge with the next tile
                if (next_tile is not None
                        and next_tile.value == tile.value
                        and next_tile.merged_from is None):
                    # Merge!
                    merged_value = tile.value * 2
                    merged = Tile(next_pos["x"], next_pos["y"], merged_value)
                    merged.merged_from = (tile, next_tile)
                    merged.is_new = False

                    grid.insert_tile(merged)
                    grid.remove_tile(tile)

                    # Update tile position for rendering
                    tile.update_position(next_pos["x"], next_pos["y"])

                    # Scoring
                    self.score += merged_value
                    if merged_value >= WIN_VALUE and not self.won:
                        self.won = True

                    moved = True

                else:
                    # Just move the tile to the farthest empty position
                    if farthest["x"] != x or farthest["y"] != y:
                        grid.remove_tile(tile)
                        tile.update_position(farthest["x"], farthest["y"])
                        grid.insert_tile(tile)
                        moved = True

        return grid, moved

    def _build_traversals(self, vector: dict) -> dict:
        """Build traversal order lists. Must traverse from the farthest
        tile in the movement direction toward the nearest, so tiles
        don't block each other."""
        traversals = {
            "x": list(range(self.size)),
            "y": list(range(self.size)),
        }

        # Reverse traversal if we're moving right/down
        if vector["x"] == 1:
            traversals["x"] = traversals["x"][::-1]
        if vector["y"] == 1:
            traversals["y"] = traversals["y"][::-1]

        return traversals

    def _find_farthest_position(self, grid: Grid, x: int, y: int, vector: dict) -> tuple:
        """Find the farthest empty position a tile can slide to.

        Returns (farthest: {x,y}, next: {x,y}) where:
        - farthest: the furthest empty cell in the direction
        - next: the cell just beyond farthest (may contain a tile or be out of bounds)
        """
        previous = {"x": x, "y": y}

        while True:
            next_x = previous["x"] + vector["x"]
            next_y = previous["y"] + vector["y"]
            next_cell = {"x": next_x, "y": next_y}

            if not grid.within_bounds(next_x, next_y) or not grid.cell_available(next_x, next_y):
                break

            previous = next_cell

        next_x = previous["x"] + vector["x"]
        next_y = previous["y"] + vector["y"]

        return previous, {"x": next_x, "y": next_y}

    @staticmethod
    def _clear_merged(tile: Optional[Tile]):
        """Reset merged_from flag on a tile."""
        if tile:
            tile.merged_from = None

    def _prepare_tiles(self):
        """Save positions and clear merge state before a move."""
        self.grid.each_cell(lambda x, y, tile: self._save_pos(tile))

    @staticmethod
    def _save_pos(tile: Optional[Tile]):
        if tile:
            tile.save_position()
            tile.merged_from = None

    # ── Game State Queries ──────────────────────────────────────────

    def _is_game_terminated(self) -> bool:
        """Check if the game has ended (either lost or won+not keeping playing)."""
        return self.over or (self.won and not self.keep_playing)

    def _moves_available(self) -> bool:
        """Check if any moves are still possible."""
        return self.grid.cells_available() or self._tile_matches_available()

    def _tile_matches_available(self) -> bool:
        """Check if any two adjacent tiles have the same value."""
        for x in range(self.size):
            for y in range(self.size):
                tile = self.grid.cell_content(x, y)
                if tile is None:
                    continue
                for d in DIRECTIONS.values():
                    neighbor = self.grid.cell_content(x + d["x"], y + d["y"])
                    if neighbor and neighbor.value == tile.value:
                        return True
        return False

    # ── Player Actions ──────────────────────────────────────────────

    def restart(self):
        """Reset the game to initial state."""
        self.score = 0
        self.over = False
        self.won = False
        self.keep_playing = False
        self.moved_this_turn = False
        self.grid = Grid(self.size)
        self._add_start_tiles()

    def keep_playing_action(self):
        """Continue playing after reaching 2048."""
        self.keep_playing = True

    # ── Serialization ───────────────────────────────────────────────

    def serialize(self) -> dict:
        """Export full game state to JSON-serializable dict."""
        return {
            "grid": self.grid.serialize(),
            "score": self.score,
            "over": self.over,
            "won": self.won,
            "keep_playing": self.keep_playing,
        }

    def _load_state(self, state: dict):
        """Restore game from serialized state."""
        self.score = state.get("score", 0)
        self.over = state.get("over", False)
        self.won = state.get("won", False)
        self.keep_playing = state.get("keep_playing", False)
        self.moved_this_turn = False
        self.grid = Grid(self.size, state.get("grid"))
