from enemy import get_enemy_group


class BattleState:
    PLAYER_TURN = "player_turn"
    ENEMY_TURN = "enemy_turn"
    VICTORY = "victory"
    DEFEAT = "defeat"

    def __init__(self, player, floor):
        self.player = player
        self.enemies = get_enemy_group(floor)
        self.turn = self.PLAYER_TURN
        self.turn_number = 1
        self.log = []
        self.selected_card = None

        for e in self.enemies:
            e.start_turn()

        player.start_battle()

    def get_alive_enemies(self):
        return [e for e in self.enemies if e.is_alive()]

    def play_card(self, card_index, enemy_index=0):
        if self.turn != self.PLAYER_TURN:
            return
        enemies = self.get_alive_enemies()
        target = enemies[enemy_index] if enemies else None
        success = self.player.play_card(card_index, target)
        if success:
            self._check_enemies()

    def end_player_turn(self):
        if self.turn != self.PLAYER_TURN:
            return
        self.player.end_turn()
        self.turn = self.ENEMY_TURN
        self._run_enemy_turn()

    def _run_enemy_turn(self):
        for e in self.get_alive_enemies():
            e.execute_intent(self.player)
            if not self.player.is_alive():
                self.turn = self.DEFEAT
                return
        for e in self.get_alive_enemies():
            e.start_turn()
        self.player.start_turn()
        self.turn_number += 1
        self.turn = self.PLAYER_TURN

    def _check_enemies(self):
        if not self.get_alive_enemies():
            self.turn = self.VICTORY

    def is_over(self):
        return self.turn in (self.VICTORY, self.DEFEAT)

    def gold_reward(self):
        return sum(e.max_hp // 3 for e in self.enemies)
