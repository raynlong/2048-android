"""2048 Game Constants and Configuration."""

# Grid
GRID_SIZE = 4
START_TILES = 2
WIN_VALUE = 2048
TILE_2_PROB = 0.9  # 90% chance of spawning a 2, 10% chance of 4

# Window
WINDOW_WIDTH = 500
WINDOW_HEIGHT = 650
BOARD_SIZE = 500
GRID_PADDING = 15
TILE_SIZE = 107
TILE_ROUNDED = 6

# Colors (matching the original 2048 design)
BG_COLOR = (250, 248, 239)
BOARD_COLOR = (187, 173, 160)
TEXT_DARK = (119, 110, 101)
TEXT_LIGHT = (249, 246, 242)
SCORE_BG = (187, 173, 160)
GOLD_COLOR = (237, 194, 46)

# Tile colors by value
TILE_COLORS = {
    0: (205, 193, 180, 0),       # empty
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
}

# Super tile (beyond 2048)
SUPER_TILE_BG = (60, 58, 50)
SUPER_TILE_TEXT = (249, 246, 242)

# Direction vectors (matching original JS: 0=Up, 1=Right, 2=Down, 3=Left)
DIRECTIONS = {
    "up": {"x": 0, "y": -1},
    "right": {"x": 1, "y": 0},
    "down": {"x": 0, "y": 1},
    "left": {"x": -1, "y": 0},
}

# Storage keys
SAVE_FILE = "2048_save.json"
BEST_SCORE_KEY = "best_score"
GAME_STATE_KEY = "game_state"

# Animation
SLIDE_SPEED = 8       # pixels per frame for slide animation
ANIM_FRAMES = 15      # frames for appear/pop animations
FPS = 60

# Layout — board bottom margin for one-hand use (in dp)
BOARD_BOTTOM_MARGIN = 48
