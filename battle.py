from enemy import make_enemy_group


class Battle:
    def __init__(self, players, floor):
        self.players = players
        self.enemies = make_enemy_group(floor)
        self.floor = floor
        self.over = False
        self.victory = False

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
        if self.over:
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

    # ── rewards ──────────────────────────────────────────────
    def gold_reward(self):
        return sum(e.max_hp // 4 for e in self.enemies)
