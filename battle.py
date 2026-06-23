from enemy import make_enemy_group


class Battle:
    def __init__(self, players, floor):
        self.players = players
        self.enemies = make_enemy_group(floor)
        self.floor = floor
        self.over = False
        self.victory = False
        self.fuse_mode = False        # crafting UI active
        self.fuse_slot = [None, None] # (player_idx, card_idx) x2

        for p in players:
            p.start_battle()

    # ── update ───────────────────────────────────────────────
    def update(self, dt):
        if self.over:
            return

        for p in self.players:
            if p.alive:
                p.update(dt)

        for e in self.enemies:
            if e.is_alive():
                e.update(dt, self.players)

        # check win/lose
        if all(not e.is_alive() for e in self.enemies):
            self.over = True
            self.victory = True
        elif all(not p.alive for p in self.players):
            self.over = True
            self.victory = False

    # ── player actions ───────────────────────────────────────
    def play_card(self, player_idx: int, card_idx: int, enemy_idx: int = 0):
        if self.over or self.fuse_mode:
            return False
        p = self.players[player_idx]
        alive_enemies = [e for e in self.enemies if e.is_alive()]
        if not alive_enemies:
            return False
        target_idx = self.enemies.index(alive_enemies[min(enemy_idx, len(alive_enemies) - 1)])
        return p.play_card(card_idx, self, target_idx)

    def damage_enemy(self, idx: int, amount: int):
        if 0 <= idx < len(self.enemies):
            self.enemies[idx].take_damage(amount)

    # ── fuse mode ────────────────────────────────────────────
    def enter_fuse(self):
        self.fuse_mode = True
        self.fuse_slot = [None, None]

    def select_fuse(self, player_idx, card_idx):
        from cards import try_fuse
        p = self.players[player_idx]
        if card_idx >= len(p.hand):
            return
        # fill first empty slot
        if self.fuse_slot[0] is None:
            self.fuse_slot[0] = (player_idx, card_idx)
        elif self.fuse_slot[1] is None:
            self.fuse_slot[1] = (player_idx, card_idx)
            self._attempt_fuse()

    def _attempt_fuse(self):
        from cards import try_fuse
        (pi0, ci0), (pi1, ci1) = self.fuse_slot
        p0, p1 = self.players[pi0], self.players[pi1]

        # adjust index if same player and first card removed
        card_a = p0.hand[ci0]
        card_b = p1.hand[ci1]

        result = try_fuse(card_a, card_b)
        if result:
            # remove both cards (careful with same-player same-hand)
            cards_to_remove = [(pi0, ci0), (pi1, ci1)]
            # sort descending by idx to avoid index shift
            cards_to_remove.sort(key=lambda x: (x[0], x[1]), reverse=True)
            for pi, ci in cards_to_remove:
                self.players[pi].hand.pop(ci)
            # give fused card to p0
            p0.hand.append(result)
        self.fuse_mode = False
        self.fuse_slot = [None, None]

    def cancel_fuse(self):
        self.fuse_mode = False
        self.fuse_slot = [None, None]

    # ── rewards ──────────────────────────────────────────────
    def gold_reward(self):
        return sum(e.max_hp // 4 for e in self.enemies)
