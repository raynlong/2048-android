"""Tile data model - exact replica of original JS tile.js."""


class Tile:
    """Represents a single tile on the 2048 board.

    Attributes:
        x, y: Current grid position
        value: Tile value (2, 4, 8, ...)
        previous_position: Position before move (for slide animation)
        merged_from: Tuple of (tile1, tile2) if this tile was created by merge
    """

    def __init__(self, x: int, y: int, value: int = 2):
        self.x = x
        self.y = y
        self.value = value
        self.previous_position = None  # (x, y) or None
        self.merged_from = None  # (Tile, Tile) or None
        self.is_new = True  # For appear animation

    def save_position(self):
        """Remember current position before a move (for slide animation)."""
        self.previous_position = (self.x, self.y)

    def update_position(self, x: int, y: int):
        """Move tile to a new grid position."""
        self.x = x
        self.y = y

    def clone(self) -> "Tile":
        """Create a copy for state snapshot."""
        t = Tile(self.x, self.y, self.value)
        t.previous_position = self.previous_position
        t.merged_from = self.merged_from
        t.is_new = self.is_new
        return t

    def serialize(self) -> dict:
        """Convert to JSON-serializable dict."""
        return {
            "position": {"x": self.x, "y": self.y},
            "value": self.value,
        }
