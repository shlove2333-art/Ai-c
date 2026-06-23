import pygame

# Colors
BG = (20, 20, 35)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 60, 60)
GREEN = (60, 200, 100)
BLUE = (60, 120, 220)
YELLOW = (240, 200, 60)
GRAY = (100, 100, 120)
DARK_GRAY = (40, 40, 55)
ORANGE = (240, 140, 40)
PURPLE = (160, 60, 220)
GOLD = (255, 215, 0)

RARITY_COLOR = {
    "common": WHITE,
    "uncommon": BLUE,
    "rare": GOLD,
}

TYPE_COLOR = {
    "attack": RED,
    "skill": GREEN,
    "power": PURPLE,
}


def draw_text(surface, text, x, y, color=WHITE, font=None, center=False):
    if font is None:
        font = pygame.font.SysFont("Arial", 16)
    for i, line in enumerate(text.split("\n")):
        img = font.render(line, True, color)
        rx = x - img.get_width() // 2 if center else x
        surface.blit(img, (rx, y + i * 20))


def draw_hp_bar(surface, x, y, w, h, current, maximum, color=RED):
    pygame.draw.rect(surface, DARK_GRAY, (x, y, w, h))
    if maximum > 0:
        fill = int(w * current / maximum)
        pygame.draw.rect(surface, color, (x, y, fill, h))
    pygame.draw.rect(surface, GRAY, (x, y, w, h), 2)
    font = pygame.font.SysFont("Arial", 13)
    txt = font.render(f"{current}/{maximum}", True, WHITE)
    surface.blit(txt, (x + w // 2 - txt.get_width() // 2, y + 1))


def draw_card(surface, card, x, y, w=110, h=150, selected=False, affordable=True):
    color = (50, 50, 70) if affordable else (35, 35, 50)
    border = YELLOW if selected else TYPE_COLOR.get(card.card_type, WHITE)
    border_w = 3 if selected else 2

    pygame.draw.rect(surface, color, (x, y, w, h), border_radius=8)
    pygame.draw.rect(surface, border, (x, y, w, h), border_w, border_radius=8)

    # Cost circle
    cost_color = BLUE if affordable else GRAY
    pygame.draw.circle(surface, cost_color, (x + 18, y + 18), 14)
    font_cost = pygame.font.SysFont("Arial", 16, bold=True)
    cost_txt = font_cost.render(str(card.cost), True, WHITE)
    surface.blit(cost_txt, (x + 18 - cost_txt.get_width() // 2, y + 18 - cost_txt.get_height() // 2))

    # Card name
    font_name = pygame.font.SysFont("Arial", 13, bold=True)
    name_color = RARITY_COLOR.get(card.rarity, WHITE)
    name_txt = font_name.render(card.name, True, name_color)
    surface.blit(name_txt, (x + w // 2 - name_txt.get_width() // 2, y + 36))

    # Divider
    pygame.draw.line(surface, GRAY, (x + 8, y + 56), (x + w - 8, y + 56), 1)

    # Type badge
    font_type = pygame.font.SysFont("Arial", 11)
    type_color = TYPE_COLOR.get(card.card_type, WHITE)
    type_txt = font_type.render(card.card_type.upper(), True, type_color)
    surface.blit(type_txt, (x + w // 2 - type_txt.get_width() // 2, y + 60))

    # Description
    font_desc = pygame.font.SysFont("Arial", 12)
    for i, line in enumerate(card.description.split("\n")):
        d = font_desc.render(line, True, WHITE)
        surface.blit(d, (x + w // 2 - d.get_width() // 2, y + 80 + i * 18))


def draw_enemy(surface, enemy, x, y):
    # Body
    color = (160, 60, 60) if enemy.is_alive() else GRAY
    pygame.draw.ellipse(surface, color, (x, y, 80, 100))
    pygame.draw.ellipse(surface, WHITE, (x, y, 80, 100), 2)

    font = pygame.font.SysFont("Arial", 14, bold=True)
    name = font.render(enemy.name, True, WHITE)
    surface.blit(name, (x + 40 - name.get_width() // 2, y - 22))

    draw_hp_bar(surface, x - 5, y - 6, 90, 16, enemy.hp, enemy.max_hp, RED)

    # Block
    if enemy.block > 0:
        font_b = pygame.font.SysFont("Arial", 13)
        blk = font_b.render(f"🛡 {enemy.block}", True, BLUE)
        surface.blit(blk, (x + 40 - blk.get_width() // 2, y + 105))

    # Intent
    font_i = pygame.font.SysFont("Arial", 13)
    intent = font_i.render(enemy.get_intent_text(), True, ORANGE)
    surface.blit(intent, (x + 40 - intent.get_width() // 2, y + 118))


def draw_player_status(surface, player, x, y):
    font = pygame.font.SysFont("Arial", 16, bold=True)
    title = font.render("Hero", True, GREEN)
    surface.blit(title, (x, y))

    draw_hp_bar(surface, x, y + 24, 160, 18, player.hp, player.max_hp, GREEN)

    font2 = pygame.font.SysFont("Arial", 14)
    stats = [
        f"Block: {player.block}",
        f"Strength: {player.strength}",
        f"Energy: {player.energy}/{player.max_energy}",
        f"Gold: {player.gold}",
        f"Floor: {player.floor}",
    ]
    for i, s in enumerate(stats):
        t = font2.render(s, True, WHITE)
        surface.blit(t, (x, y + 48 + i * 20))

    # Deck info
    font3 = pygame.font.SysFont("Arial", 13)
    deck_txt = font3.render(
        f"Draw:{len(player.draw_pile)} Disc:{len(player.discard_pile)}",
        True, GRAY
    )
    surface.blit(deck_txt, (x, y + 156))
