import pygame
from constants import *
from constants import TYPE_KR


def font(size, bold=False):
    # 한국어 지원 폰트 순서대로 시도
    for name in ["malgun gothic", "맑은 고딕", "nanum gothic", "gulim", "dotum", "arial"]:
        f = pygame.font.SysFont(name, size, bold=bold)
        if f is not None:
            return f
    return pygame.font.SysFont(None, size, bold=bold)


def draw_text(surf, text, x, y, color=WHITE, size=16, bold=False, center=False):
    f = font(size, bold)
    for i, line in enumerate(str(text).split("\n")):
        img = f.render(line, True, color)
        bx = x - img.get_width() // 2 if center else x
        surf.blit(img, (bx, y + i * (size + 3)))


def draw_bar(surf, x, y, w, h, frac, fg, bg=DARK_GRAY, border=GRAY):
    pygame.draw.rect(surf, bg, (x, y, w, h))
    pygame.draw.rect(surf, fg, (x, y, int(w * max(0, min(1, frac))), h))
    pygame.draw.rect(surf, border, (x, y, w, h), 2)


def draw_card(surf, card, x, y, w=105, h=145,
              selected=False, fuse_sel=False, affordable=True, hotkey=""):
    alpha_surf = pygame.Surface((w, h), pygame.SRCALPHA)
    body_col = (55, 50, 75) if affordable else (35, 35, 50)
    pygame.draw.rect(alpha_surf, (*body_col, 220), (0, 0, w, h), border_radius=9)
    surf.blit(alpha_surf, (x, y))

    border_col = YELLOW if selected else (PINK if fuse_sel else TYPE_COLOR.get(card.card_type, WHITE))
    bw = 3 if (selected or fuse_sel) else 2
    pygame.draw.rect(surf, border_col, (x, y, w, h), bw, border_radius=9)

    # cost bubble
    bc = BLUE if affordable else GRAY
    pygame.draw.circle(surf, bc, (x + 16, y + 16), 13)
    draw_text(surf, str(card.cost), x + 16, y + 8, WHITE, 14, bold=True, center=True)

    # name
    nc = RARITY_COLOR.get(card.rarity, WHITE)
    draw_text(surf, card.name, x + w // 2, y + 32, nc, 12, bold=True, center=True)

    pygame.draw.line(surf, GRAY, (x + 6, y + 50), (x + w - 6, y + 50), 1)

    tc = TYPE_COLOR.get(card.card_type, WHITE)
    draw_text(surf, TYPE_KR.get(card.card_type, card.card_type), x + w // 2, y + 54, tc, 10, center=True)

    draw_text(surf, card.description, x + w // 2, y + 70, WHITE, 11, center=True)

    if hotkey:
        draw_text(surf, hotkey, x + 4, y + h - 18, GRAY, 11)


def draw_enemy(surf, enemy, x, y, w=90, h=110):
    if not enemy.is_alive():
        return
    col = (150, 55, 55)
    pygame.draw.ellipse(surf, col, (x, y + 20, w, h - 20))
    pygame.draw.ellipse(surf, WHITE, (x, y + 20, w, h - 20), 2)

    # name
    draw_text(surf, enemy.name, x + w // 2, y, WHITE, 13, bold=True, center=True)

    # hp bar
    draw_bar(surf, x, y + 14, w, 14, enemy.hp / enemy.max_hp, RED)
    draw_text(surf, f"{enemy.hp}/{enemy.max_hp}", x + w // 2, y + 15, WHITE, 11, center=True)

    # burn
    if enemy.burn > 0:
        draw_text(surf, f"🔥{enemy.burn}", x + w + 4, y + 14, ORANGE, 13)

    # warn bar (countdown to action)
    warn_col = ORANGE if enemy.warn_frac() > 0.75 else YELLOW
    draw_bar(surf, x, y + h + 4, w, 10, enemy.warn_frac(), warn_col, bg=(30, 30, 40))

    # intent
    draw_text(surf, enemy.intent_label(), x + w // 2, y + h + 18, ORANGE, 12, center=True)


def draw_player_panel(surf, player, px, py, pw, ph, label, controls_hint):
    # panel bg
    panel = pygame.Surface((pw, ph), pygame.SRCALPHA)
    pygame.draw.rect(panel, (25, 22, 45, 200), (0, 0, pw, ph), border_radius=10)
    surf.blit(panel, (px, py))
    pygame.draw.rect(surf, TEAL if "P1" in label else PINK, (px, py, pw, ph), 2, border_radius=10)

    draw_text(surf, label, px + 8, py + 6, TEAL if "P1" in label else PINK, 14, bold=True)

    # hp bar
    draw_bar(surf, px + 8, py + 26, pw - 16, 16, player.hp / player.max_hp, GREEN)
    draw_text(surf, f"HP {player.hp}/{player.max_hp}", px + pw // 2, py + 27, WHITE, 11, center=True)

    # energy bar
    draw_bar(surf, px + 8, py + 46, pw - 16, 10, player.energy_frac(), BLUE)
    draw_text(surf, f"⚡ {player.energy}/{player.max_energy}", px + 8, py + 48, WHITE, 10)

    # shield / strength
    draw_text(surf, f"🛡 {player.shield}  💪 {player.strength}", px + 8, py + 62, WHITE, 12)

    # controls hint
    draw_text(surf, controls_hint, px + 8, py + ph - 20, GRAY, 10)
