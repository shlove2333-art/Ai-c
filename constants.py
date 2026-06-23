W, H = 1200, 720

# Colors
BG        = (15, 12, 28)
WHITE     = (255, 255, 255)
BLACK     = (0, 0, 0)
RED       = (220, 55, 55)
GREEN     = (55, 200, 90)
BLUE      = (55, 120, 220)
YELLOW    = (240, 200, 55)
GRAY      = (100, 100, 120)
DARK_GRAY = (35, 35, 50)
ORANGE    = (240, 130, 35)
PURPLE    = (160, 55, 220)
GOLD      = (255, 210, 0)
TEAL      = (55, 200, 180)
PINK      = (220, 80, 160)

TYPE_COLOR = {
    "attack":  RED,
    "guard":   BLUE,
    "support": GREEN,
    "power":   PURPLE,
}

RARITY_COLOR = {
    "common":   WHITE,
    "uncommon": TEAL,
    "rare":     GOLD,
    "fused":    PINK,
}

# Timing
ENEMY_WARN_SEC   = 2.2   # seconds enemy shows intent before acting
ENERGY_REGEN_SEC = 1.0   # seconds per 1 energy regen
MAX_ENERGY       = 6
DRAW_INTERVAL    = 3.0   # auto-draw interval seconds
MAX_HAND         = 5
