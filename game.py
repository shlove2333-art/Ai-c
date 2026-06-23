import pygame
from battle import BattleState
from cards import get_random_reward_cards
from ui import (
    BG, WHITE, BLACK, RED, GREEN, BLUE, YELLOW, GRAY, DARK_GRAY, ORANGE, GOLD,
    draw_text, draw_hp_bar, draw_card, draw_enemy, draw_player_status
)

W, H = 1100, 700


class Game:
    STATE_MENU = "menu"
    STATE_BATTLE = "battle"
    STATE_REWARD = "reward"
    STATE_SHOP = "shop"
    STATE_GAME_OVER = "game_over"
    STATE_VICTORY = "victory"

    def __init__(self, screen, player):
        self.screen = screen
        self.player = player
        self.state = self.STATE_MENU
        self.battle = None
        self.reward_cards = []
        self.selected_card_idx = None
        self.target_enemy_idx = 0
        self.font_big = pygame.font.SysFont("Arial", 36, bold=True)
        self.font_med = pygame.font.SysFont("Arial", 22)
        self.font_sm = pygame.font.SysFont("Arial", 16)
        self.font_xs = pygame.font.SysFont("Arial", 13)

    def start_battle(self):
        self.player.floor += 1
        self.battle = BattleState(self.player, self.player.floor)
        self.state = self.STATE_BATTLE
        self.selected_card_idx = None
        self.target_enemy_idx = 0

    def handle_event(self, event):
        if self.state == self.STATE_MENU:
            self._menu_event(event)
        elif self.state == self.STATE_BATTLE:
            self._battle_event(event)
        elif self.state == self.STATE_REWARD:
            self._reward_event(event)
        elif self.state == self.STATE_GAME_OVER:
            self._gameover_event(event)
        elif self.state == self.STATE_VICTORY:
            self._victory_event(event)

    def _menu_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            self.start_battle()
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            btn = pygame.Rect(W // 2 - 100, 340, 200, 50)
            if btn.collidepoint(mx, my):
                self.start_battle()

    def _battle_event(self, event):
        b = self.battle
        if b.turn != BattleState.PLAYER_TURN:
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos

            # End turn button
            end_btn = pygame.Rect(W - 170, H - 90, 150, 44)
            if end_btn.collidepoint(mx, my):
                self.selected_card_idx = None
                b.end_player_turn()
                self._check_battle_end()
                return

            # Click on card in hand
            hand = b.player.hand
            card_y = H - 165
            total_w = len(hand) * 120
            start_x = (W - total_w) // 2
            for i, card in enumerate(hand):
                cx = start_x + i * 120
                rect = pygame.Rect(cx, card_y, 110, 150)
                if rect.collidepoint(mx, my):
                    if self.selected_card_idx == i:
                        self.selected_card_idx = None
                    else:
                        self.selected_card_idx = i
                    return

            # Click on enemy (when card selected)
            if self.selected_card_idx is not None:
                enemies = b.get_alive_enemies()
                for i, e in enumerate(enemies):
                    ex = 300 + i * 200
                    ey = 150
                    rect = pygame.Rect(ex - 10, ey - 30, 100, 160)
                    if rect.collidepoint(mx, my):
                        b.play_card(self.selected_card_idx, i)
                        self.selected_card_idx = None
                        self._check_battle_end()
                        return
                # Clicked elsewhere — try to play skill/power on self
                card = hand[self.selected_card_idx] if self.selected_card_idx < len(hand) else None
                if card and card.card_type in ("skill", "power"):
                    b.play_card(self.selected_card_idx, 0)
                    self.selected_card_idx = None
                    self._check_battle_end()

        if event.type == pygame.KEYDOWN:
            hand = b.player.hand
            if pygame.K_1 <= event.key <= pygame.K_9:
                idx = event.key - pygame.K_1
                if idx < len(hand):
                    if self.selected_card_idx == idx:
                        self.selected_card_idx = None
                    else:
                        self.selected_card_idx = idx
            if event.key == pygame.K_e:
                self.selected_card_idx = None
                b.end_player_turn()
                self._check_battle_end()
            if event.key == pygame.K_ESCAPE:
                self.selected_card_idx = None

    def _check_battle_end(self):
        b = self.battle
        if b.turn == BattleState.VICTORY:
            gold = b.gold_reward()
            self.player.gold += gold
            self.player.heal(self.player.max_hp // 10)
            self.reward_cards = get_random_reward_cards(3)
            self.state = self.STATE_REWARD
        elif b.turn == BattleState.DEFEAT:
            self.state = self.STATE_GAME_OVER

    def _reward_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            # Card choices
            for i, card in enumerate(self.reward_cards):
                cx = 150 + i * 260
                cy = 250
                rect = pygame.Rect(cx, cy, 200, 200)
                if rect.collidepoint(mx, my):
                    self.player.add_card_to_deck(card)
                    self.reward_cards = []
                    if self.player.floor >= 10:
                        self.state = self.STATE_VICTORY
                    else:
                        self.start_battle()
                    return
            # Skip button
            skip_btn = pygame.Rect(W // 2 - 80, 490, 160, 44)
            if skip_btn.collidepoint(mx, my):
                self.reward_cards = []
                if self.player.floor >= 10:
                    self.state = self.STATE_VICTORY
                else:
                    self.start_battle()

    def _gameover_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            from player import Player
            self.player.__dict__.update(Player().__dict__)
            self.player.floor = 0
            self.state = self.STATE_MENU

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            btn = pygame.Rect(W // 2 - 100, 420, 200, 50)
            if btn.collidepoint(mx, my):
                from player import Player
                self.player.__dict__.update(Player().__dict__)
                self.player.floor = 0
                self.state = self.STATE_MENU

    def _victory_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            from player import Player
            self.player.__dict__.update(Player().__dict__)
            self.player.floor = 0
            self.state = self.STATE_MENU

    def draw(self):
        self.screen.fill(BG)
        if self.state == self.STATE_MENU:
            self._draw_menu()
        elif self.state == self.STATE_BATTLE:
            self._draw_battle()
        elif self.state == self.STATE_REWARD:
            self._draw_reward()
        elif self.state == self.STATE_GAME_OVER:
            self._draw_gameover()
        elif self.state == self.STATE_VICTORY:
            self._draw_victory()

    def _draw_menu(self):
        title = self.font_big.render("CARD DUNGEON", True, GOLD)
        self.screen.blit(title, (W // 2 - title.get_width() // 2, 200))

        sub = self.font_med.render("덱빌딩 RPG — 던전을 탐험하라", True, WHITE)
        self.screen.blit(sub, (W // 2 - sub.get_width() // 2, 270))

        btn = pygame.Rect(W // 2 - 100, 340, 200, 50)
        pygame.draw.rect(self.screen, GREEN, btn, border_radius=8)
        pygame.draw.rect(self.screen, WHITE, btn, 2, border_radius=8)
        t = self.font_med.render("게임 시작", True, BLACK)
        self.screen.blit(t, (btn.centerx - t.get_width() // 2, btn.centery - t.get_height() // 2))

        hint = self.font_xs.render("Enter 또는 클릭으로 시작", True, GRAY)
        self.screen.blit(hint, (W // 2 - hint.get_width() // 2, 410))

    def _draw_battle(self):
        b = self.battle
        if b is None:
            return

        # Title bar
        title = self.font_sm.render(
            f"Floor {self.player.floor}  |  Turn {b.turn_number}  |  {'YOUR TURN' if b.turn == BattleState.PLAYER_TURN else 'ENEMY TURN'}",
            True, YELLOW
        )
        self.screen.blit(title, (W // 2 - title.get_width() // 2, 12))

        # Player status panel
        draw_player_status(self.screen, self.player, 20, 100)

        # Enemies
        enemies = b.enemies
        for i, e in enumerate(enemies):
            ex = 320 + i * 220
            ey = 160
            if self.target_enemy_idx == i and self.selected_card_idx is not None:
                pygame.draw.circle(self.screen, YELLOW, (ex + 40, ey + 50), 55, 3)
            draw_enemy(self.screen, e, ex, ey)

        # Hand cards
        hand = b.player.hand
        card_y = H - 168
        total_w = len(hand) * 120
        start_x = max(10, (W - total_w) // 2)

        for i, card in enumerate(hand):
            cx = start_x + i * 120
            selected = (self.selected_card_idx == i)
            cy = card_y - (20 if selected else 0)
            affordable = b.player.energy >= card.cost
            draw_card(self.screen, card, cx, cy, selected=selected, affordable=affordable)
            # Hotkey hint
            key_txt = self.font_xs.render(str(i + 1), True, GRAY)
            self.screen.blit(key_txt, (cx + 5, cy + 134))

        # End turn button
        end_btn = pygame.Rect(W - 170, H - 90, 150, 44)
        btn_color = GREEN if b.turn == BattleState.PLAYER_TURN else GRAY
        pygame.draw.rect(self.screen, btn_color, end_btn, border_radius=8)
        pygame.draw.rect(self.screen, WHITE, end_btn, 2, border_radius=8)
        et = self.font_sm.render("End Turn  [E]", True, BLACK)
        self.screen.blit(et, (end_btn.centerx - et.get_width() // 2, end_btn.centery - et.get_height() // 2))

        # Hint
        if self.selected_card_idx is not None and self.selected_card_idx < len(hand):
            card = hand[self.selected_card_idx]
            if card.card_type == "attack":
                hint = self.font_xs.render("적을 클릭하여 카드 사용", True, ORANGE)
            else:
                hint = self.font_xs.render("빈 공간 클릭 또는 카드 재클릭", True, ORANGE)
            self.screen.blit(hint, (W // 2 - hint.get_width() // 2, H - 180))

    def _draw_reward(self):
        title = self.font_big.render("전투 승리!", True, GOLD)
        self.screen.blit(title, (W // 2 - title.get_width() // 2, 120))

        sub = self.font_med.render("카드를 하나 선택하세요 (또는 Skip)", True, WHITE)
        self.screen.blit(sub, (W // 2 - sub.get_width() // 2, 185))

        for i, card in enumerate(self.reward_cards):
            cx = 130 + i * 280
            cy = 240
            draw_card(self.screen, card, cx, cy, w=200, h=200)

        skip_btn = pygame.Rect(W // 2 - 80, 490, 160, 44)
        pygame.draw.rect(self.screen, GRAY, skip_btn, border_radius=8)
        pygame.draw.rect(self.screen, WHITE, skip_btn, 2, border_radius=8)
        t = self.font_sm.render("Skip →", True, WHITE)
        self.screen.blit(t, (skip_btn.centerx - t.get_width() // 2, skip_btn.centery - t.get_height() // 2))

        gold_txt = self.font_sm.render(f"골드: {self.player.gold}", True, GOLD)
        self.screen.blit(gold_txt, (20, 20))

        floor_txt = self.font_sm.render(f"Floor {self.player.floor} / 10", True, WHITE)
        self.screen.blit(floor_txt, (W - 150, 20))

    def _draw_gameover(self):
        title = self.font_big.render("GAME OVER", True, RED)
        self.screen.blit(title, (W // 2 - title.get_width() // 2, 220))

        info = self.font_med.render(f"Floor {self.player.floor}에서 쓰러졌습니다", True, WHITE)
        self.screen.blit(info, (W // 2 - info.get_width() // 2, 300))

        btn = pygame.Rect(W // 2 - 100, 420, 200, 50)
        pygame.draw.rect(self.screen, RED, btn, border_radius=8)
        pygame.draw.rect(self.screen, WHITE, btn, 2, border_radius=8)
        t = self.font_med.render("다시 시작 [R]", True, WHITE)
        self.screen.blit(t, (btn.centerx - t.get_width() // 2, btn.centery - t.get_height() // 2))

    def _draw_victory(self):
        title = self.font_big.render("VICTORY!", True, GOLD)
        self.screen.blit(title, (W // 2 - title.get_width() // 2, 200))

        sub = self.font_med.render("던전을 정복했습니다! 축하합니다!", True, GREEN)
        self.screen.blit(sub, (W // 2 - sub.get_width() // 2, 280))

        gold = self.font_med.render(f"획득 골드: {self.player.gold}", True, GOLD)
        self.screen.blit(gold, (W // 2 - gold.get_width() // 2, 340))

        hint = self.font_sm.render("[R] 처음부터 다시", True, GRAY)
        self.screen.blit(hint, (W // 2 - hint.get_width() // 2, 420))
