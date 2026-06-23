import pygame
from battle import Battle
from player import Player
from cards import P1_STARTER, P2_STARTER, random_reward, try_fuse
from ui import (draw_text, draw_bar, draw_card, draw_enemy, draw_player_panel,
                font)
from constants import *


# ── Key bindings ─────────────────────────────────────────────
P1_KEYS    = [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5]
P2_KEYS    = [pygame.K_7, pygame.K_8, pygame.K_9, pygame.K_0, pygame.K_MINUS]
P1_LABELS  = ["1", "2", "3", "4", "5"]
P2_LABELS  = ["7", "8", "9", "0", "-"]
CANCEL_KEY = pygame.K_ESCAPE


class GameApp:
    MENU    = "menu"
    BATTLE  = "battle"
    REWARD  = "reward"
    FORGE   = "forge"      # inter-battle card crafting
    OVER    = "over"
    WIN     = "win"

    def __init__(self, screen):
        self.screen = screen
        self.state  = self.MENU
        self.players: list[Player] = []
        self.battle: Battle | None = None
        self.reward_cards = []
        self.forge_selection = [None, None]  # (player_idx, card_idx)
        self.floor = 0

    # ── state machine ────────────────────────────────────────
    def _new_game(self):
        self.floor = 0
        self.players = [
            Player(P1_STARTER, name="전사"),
            Player(P2_STARTER, name="수호자"),
        ]
        self._next_battle()

    def _next_battle(self):
        self.floor += 1
        self.battle = Battle(self.players, self.floor)
        self.state  = self.BATTLE

    def _open_reward(self):
        self.reward_cards = random_reward(3)
        self.state = self.REWARD

    def _open_forge(self):
        self.forge_selection = [None, None]
        self.state = self.FORGE

    # ── update ───────────────────────────────────────────────
    def update(self, dt):
        if self.state == self.BATTLE and self.battle:
            self.battle.update(dt)
            if self.battle.over:
                if self.battle.victory:
                    gold = self.battle.gold_reward()
                    for p in self.players:
                        p.gold += gold
                        p.heal(10)
                    if self.floor >= 10:
                        self.state = self.WIN
                    else:
                        self._open_reward()
                else:
                    self.state = self.OVER

    # ── events ───────────────────────────────────────────────
    def handle_event(self, event):
        if self.state == self.MENU:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self._new_game()
            if event.type == pygame.MOUSEBUTTONDOWN:
                bx, by = W // 2 - 110, 340
                if pygame.Rect(bx, by, 220, 52).collidepoint(event.pos):
                    self._new_game()

        elif self.state == self.BATTLE:
            self._battle_event(event)

        elif self.state == self.REWARD:
            self._reward_event(event)

        elif self.state == self.FORGE:
            self._forge_event(event)

        elif self.state in (self.OVER, self.WIN):
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.state = self.MENU
            if event.type == pygame.MOUSEBUTTONDOWN:
                bx, by = W // 2 - 100, 430
                if pygame.Rect(bx, by, 200, 50).collidepoint(event.pos):
                    self.state = self.MENU

    def _battle_event(self, event):
        b = self.battle
        if not b or b.over:
            return

        if event.type == pygame.KEYDOWN:
            for i, k in enumerate(P1_KEYS):
                if event.key == k:
                    b.play_card(0, i, 0)
                    return
            for i, k in enumerate(P2_KEYS):
                if event.key == k:
                    b.play_card(1, i, 0)
                    return

    def _reward_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            # Card reward buttons
            for i, card in enumerate(self.reward_cards):
                cx = 160 + i * 290
                cy = 240
                if pygame.Rect(cx, cy, 200, 180).collidepoint(mx, my):
                    # Give to P1 (attacker gets new attack/power, P2 gets guard/support)
                    if card.card_type in ("attack", "power"):
                        self.players[0].add_card(card)
                    else:
                        self.players[1].add_card(card)
                    self._open_forge()
                    return
            # Skip
            skip_r = pygame.Rect(W // 2 - 80, 460, 160, 42)
            if skip_r.collidepoint(mx, my):
                self._open_forge()

    def _forge_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            # Try fuse button area cards
            for pi, player in enumerate(self.players):
                for ci, card in enumerate(player.deck):
                    cx, cy = self._forge_card_pos(pi, ci)
                    if pygame.Rect(cx, cy, 105, 145).collidepoint(mx, my):
                        self._forge_select(pi, ci)
                        return
            # Continue button
            cont_r = pygame.Rect(W // 2 - 90, H - 70, 180, 44)
            if cont_r.collidepoint(mx, my):
                self._next_battle()

        if event.type == pygame.KEYDOWN:
            if event.key == CANCEL_KEY:
                self.forge_selection = [None, None]
            if event.key == pygame.K_RETURN:
                self._next_battle()

    def _forge_select(self, pi, ci):
        a, b = self.forge_selection
        if a is None:
            self.forge_selection[0] = (pi, ci)
        elif b is None:
            self.forge_selection[1] = (pi, ci)
            self._try_forge_fuse()
        else:
            self.forge_selection = [(pi, ci), None]

    def _try_forge_fuse(self):
        (pi0, ci0), (pi1, ci1) = self.forge_selection
        card_a = self.players[pi0].deck[ci0]
        card_b = self.players[pi1].deck[ci1]
        result = try_fuse(card_a, card_b)
        if result:
            # remove both from decks (descending index to avoid shift)
            pairs = sorted([(pi0, ci0), (pi1, ci1)], key=lambda x: (x[0], x[1]), reverse=True)
            for pi, ci in pairs:
                self.players[pi].deck.pop(ci)
            self.players[pi0].deck.append(result)
        self.forge_selection = [None, None]

    def _forge_card_pos(self, player_idx, card_idx):
        cols = 8
        col = card_idx % cols
        row = card_idx // cols
        base_x = 20 + player_idx * (W // 2)
        x = base_x + col * 112
        y = 140 + row * 158
        return x, y

    # ── draw ─────────────────────────────────────────────────
    def draw(self):
        self.screen.fill(BG)
        if self.state == self.MENU:
            self._draw_menu()
        elif self.state == self.BATTLE:
            self._draw_battle()
        elif self.state == self.REWARD:
            self._draw_reward()
        elif self.state == self.FORGE:
            self._draw_forge()
        elif self.state == self.OVER:
            self._draw_over()
        elif self.state == self.WIN:
            self._draw_win()

    # ── draw helpers ─────────────────────────────────────────
    def _draw_menu(self):
        draw_text(self.screen, "FORGE & GUARD", W // 2, 160, GOLD, 48, bold=True, center=True)
        draw_text(self.screen, "실시간 협동 덱빌딩 RPG", W // 2, 230, WHITE, 22, center=True)

        lines = [
            "P1 (Warrior)  :  1 2 3 4 5  카드 사용",
            "P2 (Guardian) :  7 8 9 0 -  카드 사용",
            "F  :  카드 합성 모드  |  ESC : 취소",
            "적이 공격할 때 가드 카드를 제때 내세요!",
        ]
        for i, l in enumerate(lines):
            draw_text(self.screen, l, W // 2, 290 + i * 26, GRAY, 15, center=True)

        bx, by = W // 2 - 110, 400
        pygame.draw.rect(self.screen, GREEN, (bx, by, 220, 52), border_radius=10)
        draw_text(self.screen, "게임 시작  [Enter]", W // 2, by + 14, BLACK, 18, bold=True, center=True)

    def _draw_battle(self):
        b = self.battle
        if not b:
            return

        # Header
        draw_text(self.screen, f"Floor {self.floor} / 10", W // 2, 8, YELLOW, 16, bold=True, center=True)
        draw_text(self.screen, "P1: 1-5  |  P2: 7-0  |  전투 후 대장간에서 카드 합성",
                  W // 2, 26, GRAY, 13, center=True)

        # Player panels
        draw_player_panel(self.screen, self.players[0], 8, 50, 200, 190,
                          "P1 전사", "1 2 3 4 5 = 카드 사용")
        draw_player_panel(self.screen, self.players[1], W - 208, 50, 200, 190,
                          "P2 수호자", "7 8 9 0 - = 카드 사용")

        # Enemies
        alive = [e for e in b.enemies if e.is_alive()]
        ex_start = W // 2 - len(alive) * 110 // 2
        for i, e in enumerate(alive):
            ex = ex_start + i * 220
            draw_enemy(self.screen, e, ex, 80)

        # Cards — P1 (bottom left)
        p1 = self.players[0]
        for i, card in enumerate(p1.hand):
            cx = 8 + i * 112
            cy = H - 155
            draw_card(self.screen, card, cx, cy,
                      affordable=p1.energy >= card.cost,
                      hotkey=P1_LABELS[i] if i < len(P1_LABELS) else "")

        # Cards — P2 (bottom right)
        p2 = self.players[1]
        for i, card in enumerate(p2.hand):
            cx = W - 8 - (len(p2.hand) - i) * 112
            cy = H - 155
            draw_card(self.screen, card, cx, cy,
                      affordable=p2.energy >= card.cost,
                      hotkey=P2_LABELS[i] if i < len(P2_LABELS) else "")

        # Gold
        draw_text(self.screen, f"🪙 {self.players[0].gold}", 8, H - 170, GOLD, 14)

    def _draw_reward(self):
        draw_text(self.screen, "전투 승리! 카드를 선택하세요", W // 2, 80, GOLD, 30, bold=True, center=True)
        draw_text(self.screen, "공격/파워 카드 → P1(전사)  |  방어/서포트 → P2(수호자)",
                  W // 2, 128, GRAY, 14, center=True)

        for i, card in enumerate(self.reward_cards):
            cx = 150 + i * 300
            cy = 190
            draw_card(self.screen, card, cx, cy, w=200, h=180)

        skip_r = pygame.Rect(W // 2 - 80, 420, 160, 42)
        pygame.draw.rect(self.screen, GRAY, skip_r, border_radius=8)
        draw_text(self.screen, "Skip →", W // 2, 432, WHITE, 16, center=True)

    def _draw_forge(self):
        draw_text(self.screen, "⚗ 카드 대장간", W // 2, 14, PINK, 26, bold=True, center=True)
        draw_text(self.screen, "두 카드를 클릭하면 합성 시도! (레시피가 있으면 새 카드 획득)",
                  W // 2, 48, GRAY, 13, center=True)
        draw_text(self.screen, "레시피 예시: 일격+점화=화염일격  방어+방어=철벽  강타+회오리=오메가일격",
                  W // 2, 66, GRAY, 12, center=True)

        # Show both decks
        for pi, player in enumerate(self.players):
            label_col = TEAL if pi == 0 else PINK
            label = f"P{pi+1} {player.name} 덱"
            bx = 20 + pi * (W // 2)
            draw_text(self.screen, label, bx, 100, label_col, 14, bold=True)
            for ci, card in enumerate(player.deck):
                cx, cy = self._forge_card_pos(pi, ci)
                sel = self.forge_selection[0] == (pi, ci) or self.forge_selection[1] == (pi, ci)
                draw_card(self.screen, card, cx, cy, selected=sel, affordable=True)

        # Continue button
        cont_r = pygame.Rect(W // 2 - 90, H - 70, 180, 44)
        pygame.draw.rect(self.screen, GREEN, cont_r, border_radius=8)
        draw_text(self.screen, "다음 전투 →  [Enter]", W // 2, H - 58, BLACK, 15, bold=True, center=True)

    def _draw_over(self):
        draw_text(self.screen, "GAME OVER", W // 2, 200, RED, 48, bold=True, center=True)
        draw_text(self.screen, f"Floor {self.floor}에서 쓰러졌습니다", W // 2, 280, WHITE, 22, center=True)
        bx, by = W // 2 - 100, 430
        pygame.draw.rect(self.screen, RED, (bx, by, 200, 50), border_radius=10)
        draw_text(self.screen, "다시 시작 [R]", W // 2, by + 13, WHITE, 18, center=True)

    def _draw_win(self):
        draw_text(self.screen, "VICTORY!", W // 2, 180, GOLD, 52, bold=True, center=True)
        draw_text(self.screen, "던전을 정복했습니다! 두 영웅의 승리!", W // 2, 265, GREEN, 22, center=True)
        draw_text(self.screen, f"획득 골드: {self.players[0].gold}", W // 2, 320, GOLD, 20, center=True)
        bx, by = W // 2 - 100, 430
        pygame.draw.rect(self.screen, GREEN, (bx, by, 200, 50), border_radius=10)
        draw_text(self.screen, "처음부터 [R]", W // 2, by + 13, BLACK, 18, bold=True, center=True)
