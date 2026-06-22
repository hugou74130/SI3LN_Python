"""
Constants and configuration for SI3LN Game
"""
import os

# Directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) if os.path.dirname(os.path.abspath(__file__)) else '.'
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
DATA_DIR = os.path.join(BASE_DIR, "data")

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# Screen settings
DEFAULT_SCREEN_WIDTH = 1280
DEFAULT_SCREEN_HEIGHT = 720
FPS = 60

# Reference resolution used by ResolutionManager for responsive scaling.
# All UI coordinates and game logic are expressed in this space.
# S = min(W_actual / REF_WIDTH,  H_actual / REF_HEIGHT)
REF_WIDTH = 1280
REF_HEIGHT = 720

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (50, 50, 50)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
DARK_BLUE = (0, 0, 139)
LIGHT_BLUE = (173, 216, 230)
SAND_COLOR = (210, 180, 140)
BROWN = (139, 69, 19)
DARK_BROWN = (101, 67, 33)

# Boot Camp colors
STERILE_WHITE = (240, 245, 250)
HOLO_BLUE = (0, 220, 255)
HOLO_GREEN = (50, 255, 150)
HOLO_CYAN = (0, 200, 220)

# Game settings
MAX_LIVES = 5
MAX_PLAYER_BULLETS = 3
PLAYER_SPEED = 8
ENEMY_SPEED = 1
PLAYER_BULLET_SPEED = 10
ENEMY_BULLET_SPEED = 5

# Worlds configuration
WORLDS = {
    "BootCamp": {
        "name": "Boot Camp",
        "subtitle": "Orbital Training Station",
        "background": "background_bootcamp.jpg",
        "levels": 1,
        "enemies_dir": "BootCamp_world",
        "enemy_count": 10,
        "is_tutorial": True,
        "bullet_colors": {
            "player": [(0, 220, 255), (150, 240, 255)],      # Holographic blue
            "enemy": [(180, 190, 200), (200, 210, 220)]      # Drone gray (harmless)
        }
    },
    "Space": {
        "name": "Space World",
        "background": "background_space.jpg",
        "levels": 5,
        "enemies_dir": "Space_world",
        "enemy_count": 15,
        "bullet_colors": {
            "player": [(0, 150, 255), (100, 200, 255)],      # Bleu électrique
            "enemy": [(255, 50, 150), (255, 150, 200)]        # Rose/Magenta
        }
    },
    "Desert": {
        "name": "Desert World",
        "background": "background_desert.png",
        "levels": 5,
        "enemies_dir": "Desert_world",
        "enemy_count": 8,
        "bullet_colors": {
            "player": [(255, 200, 0), (255, 255, 100)],       # Jaune/Or
            "enemy": [(200, 100, 0), (255, 150, 50)]          # Orange/Marron
        }
    },
    "Forest": {
        "name": "Forest World",
        "background": "background_forest.png",
        "levels": 5,
        "enemies_dir": "Forest_world",
        "enemy_count": 9,
        "bullet_colors": {
            "player": [(50, 255, 150), (150, 255, 200)],      # Vert émeraude
            "enemy": [(150, 50, 200), (200, 100, 255)]        # Violet
        }
    },
    "Marine": {
        "name": "Marine World",
        "background": "background_marine.jpg",
        "levels": 5,
        "enemies_dir": "Marine_world",
        "enemy_count": 12,
        "bullet_colors": {
            "player": [(0, 255, 255), (150, 255, 255)],       # Cyan brillant
            "enemy": [(255, 100, 0), (255, 200, 100)]         # Orange vif
        }
    },
    "Apocalyptic": {
        "name": "Apocalyptic World",
        "background": "background_apocalyptic.jpg",
        "levels": 5,
        "enemies_dir": "Apocalyptic_world",
        "enemy_count": 9,
        "bullet_colors": {
            "player": [(255, 50, 50), (255, 150, 150)],       # Rouge sang
            "enemy": [(0, 255, 0), (150, 255, 150)]           # Vert toxique
        }
    }
}

# Game states
STATE_MAIN_MENU = "MAIN_MENU"
STATE_LOGIN = "LOGIN"
STATE_REGISTER = "REGISTER"
STATE_PLAYER_SELECT = "PLAYER_SELECT"
STATE_LEVEL_SELECT = "LEVEL_SELECT"
STATE_GAMEPLAY = "GAMEPLAY"
STATE_TUTORIAL = "TUTORIAL"
STATE_LEVEL_WIN = "LEVEL_WIN"
STATE_GAME_OVER = "GAME_OVER"
STATE_PROFILE = "PROFILE"
STATE_HELP = "HELP"
STATE_TUTORIAL_COMPLETE = "TUTORIAL_COMPLETE"
STATE_TUTORIAL_PAUSE = "TUTORIAL_PAUSE"

# Tutorial objective types
TUTORIAL_OBJ_MOVE = "MOVE"
TUTORIAL_OBJ_SHOOT = "SHOOT"
TUTORIAL_OBJ_COLLECT = "COLLECT"
TUTORIAL_OBJ_SURVIVE = "SURVIVE"
TUTORIAL_OBJ_EXIT = "EXIT"

# Tutorial settings
TUTORIAL_SURVIVE_TIME = 30000  # 30 seconds in ms
TUTORIAL_DRONE_COUNT = 10
TUTORIAL_MOVE_DISTANCE = 200   # pixels to move for waypoint objective
TUTORIAL_NO_DEATH_PENALTY = True

# File paths
USER_DATA_FILE = os.path.join(DATA_DIR, "users.json")
SCORES_FILE = os.path.join(DATA_DIR, "scores.json")

# UI Settings
BUTTON_CORNER_RADIUS = 10
PROFILE_ICON_SIZE = 60
PROFILE_ICON_POSITION = (20, 20)  # Top right offset from screen width

# Email settings (for future password reset functionality)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# ── Characters ──────────────────────────────────────────────────────────────
# Playable characters configuration
CHARACTER_NAMES = [
    "Star Fighter",      # 0 - Default
    "Cosmic Blazer",     # 1
    "Nebula Ranger",     # 2
    "Galaxy Defender",   # 3
    "Void Walker",       # 4
    "Solar Knight",      # 5
    "Astro Sentinel",    # 6
    "Phantom Striker",   # 7 - Unlockable (Level 3+ in any world + 5000+ score)
]

CHARACTER_ABILITIES = {
    "Phantom Striker": {
        "name": "Phase Dash",
        "description": "Brief invincible dash (0.5s) with 8s cooldown",
        "dash_duration_ms": 500,    # 0.5s invincibility
        "cooldown_ms": 8000,        # 8s cooldown
        "speed_multiplier": 2.5,    # 2.5x speed during dash
    }
}

# Unlock conditions for special characters
CHARACTER_UNLOCK_CONDITIONS = {
    7: {  # Phantom Striker
        "min_level_in_any_world": 3,
        "min_single_run_score": 5000,
        "achievement_name": "Phantom Unlocked",
        "achievement_description": "Unlock the Phantom Striker character",
    }
}

# Achievement definitions
ACHIEVEMENTS = {
    "Phantom Unlocked": {
        "description": "Unlock the Phantom Striker character",
        "points": 50,
        "rarity": "RARE",
    }
}

# Player sprite files (must match CHARACTER_NAMES length)
PLAYER_SPRITE_FILES = [
    "1000055338.png", "1000055339.png", "1000055340.png",
    "1000055341.png", "1000055342.png", "1000055343.png",
    "1000055344.png", "1000055345.png", "1000055346.png"
]

# ── API Integration ─────────────────────────────────────────────────────────
# The Python game connects to the SI3LN REST API to submit scores and read
# leaderboard data.  Set SI3LN_API_URL and SI3LN_TOKEN in the environment
# (or via docker-compose) to point the game at a running API instance.
import os as _os
API_URL   = _os.environ.get("SI3LN_API_URL", "http://localhost:8000")
API_TOKEN = _os.environ.get("SI3LN_TOKEN", "")

# World-name to World-ID mapping (must match the DB World records)
WORLD_IDS = {
    "BootCamp":    0,
    "Space":       1,
    "Desert":      2,
    "Forest":      3,
    "Marine":      4,
    "Apocalyptic": 5,
}
