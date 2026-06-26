"""Grid data structure - exact replica of original JS grid.js.

The grid is a 2D list: cells[x][y], where each cell is either None or a Tile.
"""

import random
from typing import Optional, Callable

from .tile import Tile
from .constants import GRID_SIZE


class Grid:
    """4x4 grid managing tile placement."""

    def __init__(self, size: int = GRID_SIZE, previous_state: Optional[dict] = None):
        self.size = size
        self.cells = self._from_state(previous_state) if previous_state else self._empty()

    def _empty(self) -> list:
        """Create an empty grid (all None)."""
        return [[None for _ in range(self.size)] for _ in range(self.size)]

    def _from_state(self, state: dict) -> list:
        """Restore grid from serialized state."""
        cells = self._empty()
        for cell_data in state.get("cells", []):
            if cell_data:
                pos = cell_data["position"]
                tile = Tile(pos["x"], pos["y"], cell_data["value"])
                tile.is_new = False
                cells[pos["x"]][pos["y"]] = tile
        return cells

    def random_available_cell(self) -> Optional[dict]:
        """Return a random empty cell position as {'x': int, 'y': int}, or None if full."""
        available = self.available_cells()
        if available:
            return random.choice(available)
        return None

    def available_cells(self) -> list:
        """Return list of {'x': int, 'y': int} for all empty cells."""
        result = []
        self.each_cell(lambda x, y, tile: result.append({"x": x, "y": y}) if tile is None else None)
        return result

    def cells_available(self) -> bool:
        """Check if any cell is empty."""
        return any(
            self.cells[x][y] is None
            for x in range(self.size)
            for y in range(self.size)
        )

    def cell_available(self, x: int, y: int) -> bool:
        """Check if a specific cell is empty."""
        return self.within_bounds(x, y) and self.cells[x][y] is None

    def cell_content(self, x: int, y: int) -> Optional[Tile]:
        """Get tile at position, or None if empty/out-of-bounds."""
        if self.within_bounds(x, y):
            return self.cells[x][y]
        return None

    def cell_occupied(self, x: int, y: int) -> bool:
        """Check if a cell has a tile."""
        return self.within_bounds(x, y) and self.cells[x][y] is not None

    def insert_tile(self, tile: Tile):
        """Place a tile on the grid."""
        self.cells[tile.x][tile.y] = tile

    def remove_tile(self, tile: Tile):
        """Remove a tile from the grid."""
        if self.within_bounds(tile.x, tile.y):
            self.cells[tile.x][tile.y] = None

    def within_bounds(self, x: int, y: int) -> bool:
        """Check if coordinates are within the grid."""
        return 0 <= x < self.size and 0 <= y < self.size

    def each_cell(self, callback: Callable[[int, int, Optional[Tile]], None]):
        """Iterate over every cell, calling callback(x, y, tile)."""
        for x in range(self.size):
            for y in range(self.size):
                callback(x, y, self.cells[x][y])

    def serialize(self) -> dict:
        """Convert to JSON-serializable structure."""
        cells = []
        for x in range(self.size):
            row = []
            for y in range(self.size):
                tile = self.cells[x][y]
                row.append(tile.serialize() if tile else None)
            cells.extend(row)
        return {"size": self.size, "cells": cells}
