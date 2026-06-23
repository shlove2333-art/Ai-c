import random
from constants import MAX_ENERGY, MAX_HAND, ENERGY_REGEN_SEC, DRAW_INTERVAL


class Player:
    def __init__(self, starter_classes):
        self.max_hp = 80
        self.hp = 80
        self.strength = 0
        self.max_energy = MAX_ENERGY
        self.energy = MAX_ENERGY
        self.shield = 0

        self.deck = [cls() for cls in starter_classes]
        self.draw_pile: list = []
        self.hand: list = []
        self.discard_pile: list = []

        self._energy_timer = 0.0
        self._draw_timer = 0.0
        self._draw_total = DRAW_INTERVAL
        self.alive = True
        self.gold = 0

    def start_battle(self):
        self.shield = 0
        self.energy = self.max_energy
        self.draw_pile = self.deck[:]
        random.shuffle(self.draw_pile)
        self.hand = []
        self.discard_pile = []
        self._energy_timer = 0.0
        self._draw_timer = 0.0
        for _ in range(4):
            self.draw_one()

    def update(self, dt: float):
        if self.energy < self.max_energy:
            self._energy_timer += dt
            while self._energy_timer >= ENERGY_REGEN_SEC and self.energy < self.max_energy:
                self.energy += 1
                self._energy_timer -= ENERGY_REGEN_SEC

        if len(self.hand) < MAX_HAND:
            self._draw_timer += dt
            if self._draw_timer >= self._draw_total:
                self._draw_timer = 0.0
                self.draw_one()

    def draw_one(self):
        if len(self.hand) >= MAX_HAND:
            return
        if not self.draw_pile:
            if not self.discard_pile:
                return
            self.draw_pile = self.discard_pile[:]
            random.shuffle(self.draw_pile)
            self.discard_pile = []
        if self.draw_pile:
            self.hand.append(self.draw_pile.pop())

    def can_play(self, idx: int) -> bool:
        return 0 <= idx < len(self.hand) and self.energy >= self.hand[idx].cost

    def play_card(self, idx: int, battle, target_idx=0) -> bool:
        if not self.can_play(idx):
            return False
        card = self.hand.pop(idx)
        self.energy -= card.cost
        card.use(self, battle, target_idx)
        self.discard_pile.append(card)
        return True

    def take_damage(self, amount: int):
        absorbed = min(self.shield, amount)
        self.shield -= absorbed
        net = amount - absorbed
        self.hp = max(0, self.hp - net)
        if self.hp == 0:
            self.alive = False

    def heal(self, amount: int):
        self.hp = min(self.max_hp, self.hp + amount)

    def add_card(self, card):
        self.deck.append(card)

    def energy_frac(self) -> float:
        if self.energy >= self.max_energy:
            return 1.0
        return (self.energy + self._energy_timer / ENERGY_REGEN_SEC) / self.max_energy
