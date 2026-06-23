import pygame
from battle import Battle
from player import Player
from cards import SOLO_STARTER, random_reward, try_fuse
from ui import draw_text, draw_bar, draw_card, draw_enemy_right, draw_player_panel
from constants import *

CARD_KEYS   = [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5]
CARD_LABELS = ["1", "2", "3", "4", "5"]


class GameApp:
    MENU   = "menu"
    BATTLE = "battle"
    REWARD = "reward"
    FORGE  = "forge"
    OVER   = "over"
    WIN    = "win"

    def __init__(self, screen):
        self.screen  = screen
        self.state   = self.MENU
        self.player: Player | None = None
        self.battle: Battle | None = None
        self.reward_cards = []
        self.forge_sel = [None, None]   # (card_idx, card_idx) in deck
        self.floor = 0
        self.selected_enemy = 0

    # ── game flow ───────────────────────────────────────────────
    def _new_game(self):
        self.floor  = 0
        self.player = Player(SOLO_STARTER)
        self._next_battle()

    def _next_battle(self):
        self.floor += 1
        self.battle = Battle(self.player, self.floor)
        self.selected_enemy = 0
        self.state  = self.BATTLE

    def _open_reward(self):
        self.reward_cards = random_reward(3)
        self.state = self.REWARD

    def _open_forge(self):
        self.forge_sel = [None, None]
        self.state = self.FORGE

    # ── update ──────────────────────────────────────────────────
    def update(self, dt):
        if self.state == self.BATTLE and self.battle:
            self.battle.update(dt)
            if self.battle.over:
                if self.battle.victory:
                    self.player.gold += self.battle.gold_reward()
                    self.player.heal(8)
                    if self.floor >= 10:
                        self.state = self.WIN
                    else:
                        self._open_reward()
                else:
                    self.state = self.OVER

    # ── events ──────────────────────────────────────────────────
    def handle_event(self, event):
        if self.state == self.MENU:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self._new_game()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.Rect(W//2-110, 360, 220, 52).collidepoint(event.pos):
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
                if pygame.Rect(W//2-100, 430, 200, 50).collidepoint(event.pos):
                    self.state = self.MENU

    def _battle_event(self, event):
        b = self.battle
        if not b or b.over:
            return
        if event.type == pygame.KEYDOWN:
            for i, k in enumerate(CARD_KEYS):
                if event.key == k:
                    b.play_card(i, self.selected_enemy)
                    return
            # Q/E 로 적 선택
            alive = [e for e in b.enemies if e.is_alive()]
            if event.key == pygame.K_q:
                self.selected_enemy = max(0, self.selected_enemy - 1)
            if event.key == pygame.K_e:
                self.selected_enemy = min(len(alive)-1, self.selected_enemy + 1)

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            # 카드 클릭
            for i, card in enumerate(self.player.hand):
                cx, cy = self._card_pos(i, len(self.player.hand))
                if pygame.Rect(cx, cy, 105, 145).collidepoint(mx, my):
                    b.play_card(i, self.selected_enemy)
                    return
            # 적 클릭으로 타겟 선택
            alive = [e for e in b.enemies if e.is_alive()]
            for i, e in enumerate(alive):
                ex, ey = self._enemy_pos(i, len(alive))
                if pygame.Rect(ex-10, ey-30, 110, 180).collidepoint(mx, my):
                    self.selected_enemy = i
                    return

    def _reward_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            for i, card in enumerate(self.reward_cards):
                cx = 160 + i * 300
                if pygame.Rect(cx, 220, 200, 200).collidepoint(mx, my):
                    self.player.add_card(card)
                    self._open_forge()
                    return
            if pygame.Rect(W//2-80, 460, 160, 42).collidepoint(mx, my):
                self._open_forge()

    def _forge_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            for ci, card in enumerate(self.player.deck):
                cx, cy = self._forge_pos(ci)
                if pygame.Rect(cx, cy, 105, 145).collidepoint(mx, my):
                    self._forge_select(ci)
                    return
            if pygame.Rect(W//2-90, H-70, 180, 44).collidepoint(mx, my):
                self._next_battle()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.forge_sel = [None, None]
            if event.key == pygame.K_RETURN:
                self._next_battle()

    def _forge_select(self, ci):
        a, b = self.forge_sel
        if a is None:
            self.forge_sel[0] = ci
        elif b is None:
            self.forge_sel[1] = ci
            self._try_fuse()
        else:
            self.forge_sel = [ci, None]

    def _try_fuse(self):
        i0, i1 = self.forge_sel
        if i0 == i1:
            self.forge_sel = [None, None]
            return
        card_a = self.player.deck[i0]
        card_b = self.player.deck[i1]
        result = try_fuse(card_a, card_b)
        if result:
            for idx in sorted([i0, i1], reverse=True):
                self.player.deck.pop(idx)
            self.player.deck.append(result)
        self.forge_sel = [None, None]

    # ── layout helpers ──────────────────────────────────────────
    def _card_pos(self, i, total):
        card_w = 112
        start_x = 20
        cx = start_x + i * card_w
        cy = H - 160
        return cx, cy

    def _enemy_pos(self, i, total):
        # 적은 오른쪽 절반에 배치
        base_x = W // 2 + 80
        spacing = 200
        total_w = (total - 1) * spacing
        ex = base_x + i * spacing - total_w // 2
        ey = H // 2 - 80
        return ex, ey

    def _forge_pos(self, ci):
        cols = 8
        col = ci % cols
        row = ci // cols
        x = 40 + col * 115
        y = 120 + row * 160
        return x, y

    # ── draw ────────────────────────────────────────────────────
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

    def _draw_menu(self):
        draw_text(self.screen, "FORGE & GUARD", W//2, 140, GOLD, 52, bold=True, center=True)
        draw_text(self.screen, "실시간 덱빌딩 RPG", W//2, 215, WHITE, 22, center=True)
        hints = [
            "숫자키 1~5 또는 마우스 클릭으로 카드 사용",
            "Q / E 로 적 선택  |  마우스로 적 클릭해도 됩니다",
            "적 머리 위 주황 바가 채워지면 공격!  방어 카드를 제때 내세요",
        ]
        for i, h in enumerate(hints):
            draw_text(self.screen, h, W//2, 285 + i*28, GRAY, 15, center=True)
        bx, by = W//2-110, 390
        pygame.draw.rect(self.screen, GREEN, (bx, by, 220, 52), border_radius=10)
        draw_text(self.screen, "게임 시작  [Enter]", W//2, by+14, BLACK, 18, bold=True, center=True)

    def _draw_battle(self):
        b = self.battle
        if not b:
            return

        # 중앙 구분선
        pygame.draw.line(self.screen, (50, 50, 70), (W//2, 0), (W//2, H-170), 1)

        # 헤더
        draw_text(self.screen, f"던전  {self.floor} / 10", W//2, 8, YELLOW, 17, bold=True, center=True)
        draw_text(self.screen, "1~5: 카드 사용  |  Q·E: 적 선택  |  마우스 클릭 가능",
                  W//2, 28, GRAY, 12, center=True)

        # 플레이어 패널 (왼쪽)
        p = self.player
        draw_player_panel(self.screen, p, 12, 55, 220, 210)

        # 적 (오른쪽)
        alive = [e for e in b.enemies if e.is_alive()]
        for i, e in enumerate(alive):
            ex, ey = self._enemy_pos(i, len(alive))
            selected = (i == self.selected_enemy)
            draw_enemy_right(self.screen, e, ex, ey, selected=selected)

        # 카드 핸드 (하단 왼쪽)
        for i, card in enumerate(p.hand):
            cx, cy = self._card_pos(i, len(p.hand))
            draw_card(self.screen, card, cx, cy,
                      affordable=p.energy >= card.cost,
                      hotkey=CARD_LABELS[i] if i < len(CARD_LABELS) else "")

        # 드로우/버리기 파일 수
        draw_text(self.screen, f"덱:{len(p.draw_pile)}  버림:{len(p.discard_pile)}",
                  20, H-168, GRAY, 12)
        draw_text(self.screen, f"골드: {p.gold}", 20, H-184, GOLD, 13)

    def _draw_reward(self):
        draw_text(self.screen, "전투 승리!", W//2, 80, GOLD, 36, bold=True, center=True)
        draw_text(self.screen, "카드를 하나 골라 덱에 추가하세요", W//2, 135, WHITE, 18, center=True)
        for i, card in enumerate(self.reward_cards):
            draw_card(self.screen, card, 160+i*300, 220, w=200, h=200)
        pygame.draw.rect(self.screen, GRAY, (W//2-80, 460, 160, 42), border_radius=8)
        draw_text(self.screen, "넘어가기 →", W//2, 472, WHITE, 16, center=True)

    def _draw_forge(self):
        draw_text(self.screen, "카드 대장간", W//2, 12, PINK, 28, bold=True, center=True)
        draw_text(self.screen, "카드 두 장을 클릭하면 합성 시도!  레시피가 맞으면 새 카드 획득",
                  W//2, 46, GRAY, 13, center=True)
        draw_text(self.screen, "합성 예: 일격+점화=화염일격  방어+방어=철벽  강타+회오리=오메가일격",
                  W//2, 64, GRAY, 12, center=True)
        draw_text(self.screen, f"내 덱  ({len(self.player.deck)}장)", 40, 90, TEAL, 14, bold=True)
        for ci, card in enumerate(self.player.deck):
            cx, cy = self._forge_pos(ci)
            sel = (self.forge_sel[0] == ci or self.forge_sel[1] == ci)
            draw_card(self.screen, card, cx, cy, selected=sel, affordable=True)
        cont = pygame.Rect(W//2-90, H-70, 180, 44)
        pygame.draw.rect(self.screen, GREEN, cont, border_radius=8)
        draw_text(self.screen, "다음 전투  [Enter]", W//2, H-58, BLACK, 15, bold=True, center=True)

    def _draw_over(self):
        draw_text(self.screen, "쓰러졌습니다", W//2, 200, RED, 48, bold=True, center=True)
        draw_text(self.screen, f"{self.floor}층에서 도전 종료", W//2, 278, WHITE, 22, center=True)
        pygame.draw.rect(self.screen, RED, (W//2-100, 430, 200, 50), border_radius=10)
        draw_text(self.screen, "다시 시작  [R]", W//2, 443, WHITE, 18, center=True)

    def _draw_win(self):
        draw_text(self.screen, "던전 정복!", W//2, 180, GOLD, 52, bold=True, center=True)
        draw_text(self.screen, "10층을 모두 클리어했습니다!", W//2, 265, GREEN, 22, center=True)
        draw_text(self.screen, f"획득 골드: {self.player.gold}", W//2, 320, GOLD, 20, center=True)
        pygame.draw.rect(self.screen, GREEN, (W//2-100, 430, 200, 50), border_radius=10)
        draw_text(self.screen, "처음부터  [R]", W//2, 443, BLACK, 18, bold=True, center=True)
