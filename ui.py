import pygame
from constants import *
from constants import TYPE_KR


def font(size, bold=False):
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
        surf.blit(img, (bx, y + i * (size + 4)))


def draw_bar(surf, x, y, w, h, frac, fg, bg=DARK_GRAY, border=GRAY):
    pygame.draw.rect(surf, bg, (x, y, w, h))
    pygame.draw.rect(surf, fg, (x, y, int(w * max(0.0, min(1.0, frac))), h))
    pygame.draw.rect(surf, border, (x, y, w, h), 2)


def draw_card(surf, card, x, y, w=105, h=145, selected=False, affordable=True, hotkey=""):
    body = (55, 50, 75) if affordable else (30, 30, 48)
    pygame.draw.rect(surf, body, (x, y, w, h), border_radius=9)
    border = YELLOW if selected else TYPE_COLOR.get(card.card_type, WHITE)
    bw = 3 if selected else 2
    pygame.draw.rect(surf, border, (x, y, w, h), bw, border_radius=9)

    # 코스트
    bc = BLUE if affordable else GRAY
    pygame.draw.circle(surf, bc, (x + 16, y + 16), 13)
    draw_text(surf, str(card.cost), x + 16, y + 8, WHITE, 14, bold=True, center=True)

    # 카드 이름
    nc = RARITY_COLOR.get(card.rarity, WHITE)
    draw_text(surf, card.name, x + w//2, y + 32, nc, 12, bold=True, center=True)

    pygame.draw.line(surf, GRAY, (x+6, y+50), (x+w-6, y+50), 1)

    # 타입
    tc = TYPE_COLOR.get(card.card_type, WHITE)
    draw_text(surf, TYPE_KR.get(card.card_type, card.card_type), x+w//2, y+54, tc, 10, center=True)

    # 설명
    draw_text(surf, card.description, x+w//2, y+70, WHITE, 11, center=True)

    if hotkey:
        draw_text(surf, hotkey, x+4, y+h-18, GRAY, 11)


def draw_player_panel(surf, player, px, py, pw, ph):
    # 배경
    panel = pygame.Surface((pw, ph), pygame.SRCALPHA)
    pygame.draw.rect(panel, (25, 22, 45, 210), (0, 0, pw, ph), border_radius=10)
    surf.blit(panel, (px, py))
    pygame.draw.rect(surf, TEAL, (px, py, pw, ph), 2, border_radius=10)

    draw_text(surf, "영웅", px+10, py+7, TEAL, 15, bold=True)

    # HP 바
    draw_bar(surf, px+8, py+30, pw-16, 18, player.hp/player.max_hp, GREEN)
    draw_text(surf, f"HP  {player.hp} / {player.max_hp}", px+pw//2, py+31, WHITE, 11, center=True)

    # 에너지 바
    draw_bar(surf, px+8, py+54, pw-16, 12, player.energy_frac(), BLUE)
    draw_text(surf, f"에너지  {player.energy} / {player.max_energy}", px+pw//2, py+55, WHITE, 10, center=True)

    # 방어막 / 힘
    draw_text(surf, f"방어막   {player.shield}", px+10, py+74, BLUE, 13)
    draw_text(surf, f"힘         {player.strength}", px+10, py+94, RED, 13)
    draw_text(surf, f"골드       {player.gold}", px+10, py+114, GOLD, 13)

    # 드로우 정보
    draw_text(surf, f"덱 {len(player.draw_pile)}장  /  버림 {len(player.discard_pile)}장",
              px+10, py+138, GRAY, 11)

    # 에너지 재생 힌트
    draw_text(surf, "에너지는 자동 충전됩니다", px+10, py+ph-22, GRAY, 10)


def draw_enemy_right(surf, enemy, x, y, selected=False):
    if not enemy.is_alive():
        return

    w, h = 100, 120

    # 선택 표시
    if selected:
        pygame.draw.rect(surf, YELLOW, (x-14, y-34, w+28, h+70), 2, border_radius=12)

    # 몸통
    pygame.draw.ellipse(surf, (160, 50, 50), (x, y+20, w, h-20))
    pygame.draw.ellipse(surf, WHITE, (x, y+20, w, h-20), 2)

    # 이름
    draw_text(surf, enemy.name, x+w//2, y-22, WHITE, 14, bold=True, center=True)

    # HP 바
    draw_bar(surf, x, y-6, w, 16, enemy.hp/enemy.max_hp, RED)
    draw_text(surf, f"{enemy.hp}/{enemy.max_hp}", x+w//2, y-5, WHITE, 11, center=True)

    # 화상
    if enemy.burn > 0:
        draw_text(surf, f"화상 {enemy.burn}", x+w+6, y+20, ORANGE, 12)

    # 행동 카운트다운 바 (주황 = 곧 공격)
    warn_col = RED if enemy.warn_frac() > 0.80 else (ORANGE if enemy.warn_frac() > 0.5 else YELLOW)
    draw_bar(surf, x, y+h+6, w, 12, enemy.warn_frac(), warn_col, bg=(30, 30, 40))

    # 예고 텍스트
    draw_text(surf, enemy.intent_label(), x+w//2, y+h+22, ORANGE, 13, center=True)
