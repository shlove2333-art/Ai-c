import random
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Card:
    name: str
    cost: int
    description: str
    card_type: str  # "attack", "skill", "power"
    rarity: str     # "common", "uncommon", "rare"

    def use(self, user, target=None):
        pass

    def __repr__(self):
        return f"{self.name}({self.cost})"


class Strike(Card):
    def __init__(self):
        super().__init__("Strike", 1, "Deal 6 damage.", "attack", "common")

    def use(self, user, target=None):
        if target:
            target.take_damage(6 + user.strength)


class Bash(Card):
    def __init__(self):
        super().__init__("Bash", 2, "Deal 8 dmg.\nApply 2 Vulnerable.", "attack", "common")

    def use(self, user, target=None):
        if target:
            target.take_damage(8 + user.strength)
            target.vulnerable += 2


class Defend(Card):
    def __init__(self):
        super().__init__("Defend", 1, "Gain 5 Block.", "skill", "common")

    def use(self, user, target=None):
        user.block += 5


class IronWave(Card):
    def __init__(self):
        super().__init__("Iron Wave", 1, "Gain 5 Block.\nDeal 5 damage.", "attack", "uncommon")

    def use(self, user, target=None):
        user.block += 5
        if target:
            target.take_damage(5 + user.strength)


class Whirlwind(Card):
    def __init__(self):
        super().__init__("Whirlwind", 1, "Deal 5 dmg 3 times.", "attack", "uncommon")

    def use(self, user, target=None):
        if target:
            for _ in range(3):
                target.take_damage(5 + user.strength)


class Inflame(Card):
    def __init__(self):
        super().__init__("Inflame", 1, "Gain 2 Strength.", "power", "uncommon")

    def use(self, user, target=None):
        user.strength += 2


class Shrug(Card):
    def __init__(self):
        super().__init__("Shrug It Off", 1, "Gain 8 Block.\nDraw 1 card.", "skill", "uncommon")

    def use(self, user, target=None):
        user.block += 8
        user.draw_cards(1)


class PerfectedStrike(Card):
    def __init__(self):
        super().__init__("Perfected Strike", 2, "Deal 6+2 dmg\nper Strike.", "attack", "common")

    def use(self, user, target=None):
        if target:
            strike_count = sum(1 for c in user.deck if "Strike" in c.name)
            target.take_damage(6 + strike_count * 2 + user.strength)


class Armaments(Card):
    def __init__(self):
        super().__init__("Armaments", 1, "Gain 5 Block.\nUpgrade a card.", "skill", "common")

    def use(self, user, target=None):
        user.block += 5


class HeavyBlade(Card):
    def __init__(self):
        super().__init__("Heavy Blade", 2, "Deal 14 damage.\nStr x3.", "attack", "rare")

    def use(self, user, target=None):
        if target:
            target.take_damage(14 + user.strength * 3)


class Limit_Break(Card):
    def __init__(self):
        super().__init__("Limit Break", 1, "Double your\nStrength.", "power", "rare")

    def use(self, user, target=None):
        user.strength *= 2


ALL_CARDS = [
    Strike, Bash, Defend, IronWave, Whirlwind,
    Inflame, Shrug, PerfectedStrike, Armaments, HeavyBlade, Limit_Break
]

STARTER_DECK = [
    Strike, Strike, Strike, Strike, Strike,
    Defend, Defend, Defend, Defend, Bash
]


def get_random_reward_cards(count=3):
    uncommon_rare = [c for c in ALL_CARDS if c().rarity in ("uncommon", "rare")]
    chosen = random.sample(uncommon_rare, min(count, len(uncommon_rare)))
    return [c() for c in chosen]
