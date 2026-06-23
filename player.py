import random
from cards import STARTER_DECK


class Player:
    def __init__(self):
        self.max_hp = 80
        self.hp = 80
        self.block = 0
        self.strength = 0
        self.vulnerable = 0
        self.max_energy = 3
        self.energy = 3
        self.gold = 0
        self.floor = 0

        self.deck = [cls() for cls in STARTER_DECK]
        self.draw_pile = []
        self.hand = []
        self.discard_pile = []

    def start_battle(self):
        self.block = 0
        self.strength = 0
        self.vulnerable = 0
        self.energy = self.max_energy
        self.draw_pile = self.deck[:]
        random.shuffle(self.draw_pile)
        self.hand = []
        self.discard_pile = []
        self.draw_cards(5)

    def start_turn(self):
        self.block = 0
        self.vulnerable = max(0, self.vulnerable - 1)
        self.energy = self.max_energy
        self.discard_pile.extend(self.hand)
        self.hand = []
        self.draw_cards(5)

    def draw_cards(self, count):
        for _ in range(count):
            if not self.draw_pile:
                if not self.discard_pile:
                    break
                self.draw_pile = self.discard_pile[:]
                random.shuffle(self.draw_pile)
                self.discard_pile = []
            if self.draw_pile:
                self.hand.append(self.draw_pile.pop())

    def take_damage(self, amount):
        if self.vulnerable > 0:
            amount = int(amount * 1.5)
        dmg = max(0, amount - self.block)
        self.block = max(0, self.block - amount)
        self.hp -= dmg
        self.hp = max(0, self.hp)

    def play_card(self, card_index, target=None):
        if card_index >= len(self.hand):
            return False
        card = self.hand[card_index]
        if self.energy < card.cost:
            return False
        self.energy -= card.cost
        card.use(self, target)
        self.hand.pop(card_index)
        self.discard_pile.append(card)
        return True

    def end_turn(self):
        self.discard_pile.extend(self.hand)
        self.hand = []

    def is_alive(self):
        return self.hp > 0

    def add_card_to_deck(self, card):
        self.deck.append(card)

    def heal(self, amount):
        self.hp = min(self.max_hp, self.hp + amount)
