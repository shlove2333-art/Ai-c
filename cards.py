import random
from dataclasses import dataclass


@dataclass
class CardDef:
    name: str
    cost: int
    description: str
    card_type: str   # attack / guard / support / power
    rarity: str      # common / uncommon / rare / fused

    def use(self, owner, battle, target_idx=0):
        pass


# ── Attack cards ──────────────────────────────────────────────
class Strike(CardDef):
    def __init__(self):
        super().__init__("Strike", 1, "Deal 8 dmg", "attack", "common")
    def use(self, owner, battle, target_idx=0):
        battle.damage_enemy(target_idx, 8 + owner.strength)

class HeavySlash(CardDef):
    def __init__(self):
        super().__init__("Heavy Slash", 2, "Deal 18 dmg", "attack", "uncommon")
    def use(self, owner, battle, target_idx=0):
        battle.damage_enemy(target_idx, 18 + owner.strength * 2)

class Whirlwind(CardDef):
    def __init__(self):
        super().__init__("Whirlwind", 2, "5 dmg × all\nenemies", "attack", "uncommon")
    def use(self, owner, battle, target_idx=0):
        for i in range(len(battle.enemies)):
            battle.damage_enemy(i, 5 + owner.strength)

class Ignite(CardDef):
    def __init__(self):
        super().__init__("Ignite", 1, "Deal 5 dmg\n+2 Burn", "attack", "common")
    def use(self, owner, battle, target_idx=0):
        battle.damage_enemy(target_idx, 5 + owner.strength)
        battle.enemies[target_idx].burn += 2

class Execute(CardDef):
    def __init__(self):
        super().__init__("Execute", 3, "Deal 40 dmg\n(below 30% hp)", "attack", "rare")
    def use(self, owner, battle, target_idx=0):
        e = battle.enemies[target_idx]
        dmg = 40 if e.hp / e.max_hp < 0.30 else 12
        battle.damage_enemy(target_idx, dmg + owner.strength)

# ── Guard cards ───────────────────────────────────────────────
class Guard(CardDef):
    def __init__(self):
        super().__init__("Guard", 1, "Block 10 dmg\nthis hit", "guard", "common")
    def use(self, owner, battle, target_idx=0):
        owner.shield += 10

class IronWall(CardDef):
    def __init__(self):
        super().__init__("Iron Wall", 2, "Block 22 dmg\nthis hit", "guard", "common")
    def use(self, owner, battle, target_idx=0):
        owner.shield += 22

class Parry(CardDef):
    def __init__(self):
        super().__init__("Parry", 1, "Block 8 dmg\n+Draw 1", "guard", "uncommon")
    def use(self, owner, battle, target_idx=0):
        owner.shield += 8
        owner.draw_one()

class CounterStance(CardDef):
    def __init__(self):
        super().__init__("Counter", 2, "Block 12 dmg\n+6 dmg back", "guard", "uncommon")
    def use(self, owner, battle, target_idx=0):
        owner.shield += 12
        battle.damage_enemy(target_idx, 6)

class FortressWall(CardDef):
    def __init__(self):
        super().__init__("Fortress", 3, "Block 40 dmg\nnext hit", "guard", "rare")
    def use(self, owner, battle, target_idx=0):
        owner.shield += 40

# ── Support cards ─────────────────────────────────────────────
class Heal(CardDef):
    def __init__(self):
        super().__init__("Heal", 2, "Restore 15 HP\n(both players)", "support", "common")
    def use(self, owner, battle, target_idx=0):
        for p in battle.players:
            p.heal(15)

class BattleCry(CardDef):
    def __init__(self):
        super().__init__("Battle Cry", 1, "Both +2 Str\nthis battle", "support", "uncommon")
    def use(self, owner, battle, target_idx=0):
        for p in battle.players:
            p.strength += 2

class DrawTwo(CardDef):
    def __init__(self):
        super().__init__("Draw Two", 1, "Both players\ndraw 2 cards", "support", "common")
    def use(self, owner, battle, target_idx=0):
        for p in battle.players:
            p.draw_one()
            p.draw_one()

class EnergySurge(CardDef):
    def __init__(self):
        super().__init__("Energy Surge", 0, "Gain 3 energy", "support", "uncommon")
    def use(self, owner, battle, target_idx=0):
        owner.energy = min(owner.energy + 3, owner.max_energy)

# ── Power cards ───────────────────────────────────────────────
class Inflame(CardDef):
    def __init__(self):
        super().__init__("Inflame", 1, "+3 Strength\npermanent", "power", "uncommon")
    def use(self, owner, battle, target_idx=0):
        owner.strength += 3

class BerserkerRage(CardDef):
    def __init__(self):
        super().__init__("Berserker", 2, "+6 Str, lose\n8 HP", "power", "rare")
    def use(self, owner, battle, target_idx=0):
        owner.strength += 6
        owner.take_damage(8)


# ── Fused cards (crafting results) ───────────────────────────
class BlazingSlash(CardDef):
    def __init__(self):
        super().__init__("Blazing Slash", 2, "22 dmg\n+3 Burn", "attack", "fused")
    def use(self, owner, battle, target_idx=0):
        battle.damage_enemy(target_idx, 22 + owner.strength * 2)
        battle.enemies[target_idx].burn += 3

class GuardedStrike(CardDef):
    def __init__(self):
        super().__init__("Guarded Strike", 2, "Block 10\n+Deal 10", "attack", "fused")
    def use(self, owner, battle, target_idx=0):
        owner.shield += 10
        battle.damage_enemy(target_idx, 10 + owner.strength)

class SoulBarrier(CardDef):
    def __init__(self):
        super().__init__("Soul Barrier", 2, "Block 30\nheal 10", "guard", "fused")
    def use(self, owner, battle, target_idx=0):
        owner.shield += 30
        owner.heal(10)

class WarCry(CardDef):
    def __init__(self):
        super().__init__("War Cry", 2, "+4 Str both\n+draw 2", "support", "fused")
    def use(self, owner, battle, target_idx=0):
        for p in battle.players:
            p.strength += 4
            p.draw_one()
            p.draw_one()

class OmegaStrike(CardDef):
    def __init__(self):
        super().__init__("Omega Strike", 4, "50 dmg all\nenemies", "attack", "fused")
    def use(self, owner, battle, target_idx=0):
        for i in range(len(battle.enemies)):
            battle.damage_enemy(i, 50 + owner.strength * 3)


# ── Crafting recipes ──────────────────────────────────────────
# key: frozenset of two card class names → result class
RECIPES: dict[frozenset, type] = {
    frozenset(["Strike",    "Ignite"]):     BlazingSlash,
    frozenset(["Strike",    "Guard"]):      GuardedStrike,
    frozenset(["IronWall",  "Heal"]):       SoulBarrier,
    frozenset(["BattleCry", "DrawTwo"]):    WarCry,
    frozenset(["HeavySlash","Whirlwind"]):  OmegaStrike,
    frozenset(["Strike",    "Strike"]):     HeavySlash,
    frozenset(["Guard",     "Guard"]):      IronWall,
    frozenset(["Parry",     "CounterStance"]): FortressWall,
    frozenset(["Inflame",   "BerserkerRage"]): OmegaStrike,
}

def try_fuse(card_a: CardDef, card_b: CardDef):
    key = frozenset([type(card_a).__name__, type(card_b).__name__])
    result_cls = RECIPES.get(key)
    if result_cls:
        return result_cls()
    return None


# ── Card pools ────────────────────────────────────────────────
ATTACK_POOL  = [Strike, HeavySlash, Whirlwind, Ignite, Execute]
GUARD_POOL   = [Guard, IronWall, Parry, CounterStance, FortressWall]
SUPPORT_POOL = [Heal, BattleCry, DrawTwo, EnergySurge]
POWER_POOL   = [Inflame, BerserkerRage]

ALL_POOL = ATTACK_POOL + GUARD_POOL + SUPPORT_POOL + POWER_POOL

P1_STARTER = [Strike, Strike, Strike, Guard, DrawTwo]
P2_STARTER = [Guard, Guard, IronWall, Heal, Parry]

def random_reward(count=3):
    uncommon_rare = [c for c in ALL_POOL if c().rarity in ("uncommon", "rare")]
    return [c() for c in random.sample(uncommon_rare, min(count, len(uncommon_rare)))]
