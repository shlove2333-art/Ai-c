from enemy import make_enemy_group


class Battle:
    def __init__(self, player, floor):
        self.player = player
        self.enemies = make_enemy_group(floor)
        self.floor = floor
        self.over = False
        self.victory = False

        player.start_battle()

    def update(self, dt):
        if self.over:
            return

        self.player.update(dt)

        for e in self.enemies:
            if e.is_alive():
                e.update(dt, [self.player])

        if all(not e.is_alive() for e in self.enemies):
            self.over = True
            self.victory = True
        elif not self.player.alive:
            self.over = True
            self.victory = False

    def play_card(self, card_idx: int, enemy_idx: int = 0) -> bool:
        if self.over:
            return False
        alive = [e for e in self.enemies if e.is_alive()]
        if not alive:
            return False
        target = alive[min(enemy_idx, len(alive) - 1)]
        real_idx = self.enemies.index(target)
        return self.player.play_card(card_idx, self, real_idx)

    def damage_enemy(self, idx: int, amount: int):
        if 0 <= idx < len(self.enemies):
            self.enemies[idx].take_damage(amount)

    def gold_reward(self):
        return sum(e.max_hp // 4 for e in self.enemies)
