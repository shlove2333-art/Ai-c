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
        super().__init__("일격", 1, "8 데미지", "attack", "common")
    def use(self, owner, battle, target_idx=0):
        battle.damage_enemy(target_idx, 8 + owner.strength)

class HeavySlash(CardDef):
    def __init__(self):
        super().__init__("강타", 2, "18 데미지", "attack", "uncommon")
    def use(self, owner, battle, target_idx=0):
        battle.damage_enemy(target_idx, 18 + owner.strength * 2)

class Whirlwind(CardDef):
    def __init__(self):
        super().__init__("회오리", 2, "전체에\n5 데미지", "attack", "uncommon")
    def use(self, owner, battle, target_idx=0):
        for i in range(len(battle.enemies)):
            battle.damage_enemy(i, 5 + owner.strength)

class Ignite(CardDef):
    def __init__(self):
        super().__init__("점화", 1, "5 데미지\n화상 2", "attack", "common")
    def use(self, owner, battle, target_idx=0):
        battle.damage_enemy(target_idx, 5 + owner.strength)
        battle.enemies[target_idx].burn += 2

class Execute(CardDef):
    def __init__(self):
        super().__init__("처형", 3, "40 데미지\n(체력 30% 이하)", "attack", "rare")
    def use(self, owner, battle, target_idx=0):
        e = battle.enemies[target_idx]
        dmg = 40 if e.hp / e.max_hp < 0.30 else 12
        battle.damage_enemy(target_idx, dmg + owner.strength)

# ── Guard cards ───────────────────────────────────────────────
class Guard(CardDef):
    def __init__(self):
        super().__init__("방어", 1, "방어막 10", "guard", "common")
    def use(self, owner, battle, target_idx=0):
        owner.shield += 10

class IronWall(CardDef):
    def __init__(self):
        super().__init__("철벽", 2, "방어막 22", "guard", "common")
    def use(self, owner, battle, target_idx=0):
        owner.shield += 22

class Parry(CardDef):
    def __init__(self):
        super().__init__("흘려내기", 1, "방어막 8\n카드 1장 드로우", "guard", "uncommon")
    def use(self, owner, battle, target_idx=0):
        owner.shield += 8
        owner.draw_one()

class CounterStance(CardDef):
    def __init__(self):
        super().__init__("반격", 2, "방어막 12\n+6 반격 데미지", "guard", "uncommon")
    def use(self, owner, battle, target_idx=0):
        owner.shield += 12
        battle.damage_enemy(target_idx, 6)

class FortressWall(CardDef):
    def __init__(self):
        super().__init__("요새", 3, "방어막 40", "guard", "rare")
    def use(self, owner, battle, target_idx=0):
        owner.shield += 40

# ── Support cards ─────────────────────────────────────────────
class Heal(CardDef):
    def __init__(self):
        super().__init__("치유", 2, "두 플레이어\nHP 15 회복", "support", "common")
    def use(self, owner, battle, target_idx=0):
        for p in battle.players:
            p.heal(15)

class BattleCry(CardDef):
    def __init__(self):
        super().__init__("함성", 1, "두 플레이어\n힘 +2", "support", "uncommon")
    def use(self, owner, battle, target_idx=0):
        for p in battle.players:
            p.strength += 2

class DrawTwo(CardDef):
    def __init__(self):
        super().__init__("집중", 1, "두 플레이어\n카드 2장 드로우", "support", "common")
    def use(self, owner, battle, target_idx=0):
        for p in battle.players:
            p.draw_one()
            p.draw_one()

class EnergySurge(CardDef):
    def __init__(self):
        super().__init__("에너지 폭발", 0, "에너지 3 획득", "support", "uncommon")
    def use(self, owner, battle, target_idx=0):
        owner.energy = min(owner.energy + 3, owner.max_energy)

# ── Power cards ───────────────────────────────────────────────
class Inflame(CardDef):
    def __init__(self):
        super().__init__("분노", 1, "힘 +3\n(영구)", "power", "uncommon")
    def use(self, owner, battle, target_idx=0):
        owner.strength += 3

class BerserkerRage(CardDef):
    def __init__(self):
        super().__init__("광전사", 2, "힘 +6\nHP -8", "power", "rare")
    def use(self, owner, battle, target_idx=0):
        owner.strength += 6
        owner.take_damage(8)


# ── Fused cards (crafting results) ───────────────────────────
class BlazingSlash(CardDef):
    def __init__(self):
        super().__init__("화염 일격", 2, "22 데미지\n화상 3", "attack", "fused")
    def use(self, owner, battle, target_idx=0):
        battle.damage_enemy(target_idx, 22 + owner.strength * 2)
        battle.enemies[target_idx].burn += 3

class GuardedStrike(CardDef):
    def __init__(self):
        super().__init__("수비 공격", 2, "방어막 10\n+10 데미지", "attack", "fused")
    def use(self, owner, battle, target_idx=0):
        owner.shield += 10
        battle.damage_enemy(target_idx, 10 + owner.strength)

class SoulBarrier(CardDef):
    def __init__(self):
        super().__init__("영혼 장벽", 2, "방어막 30\nHP 10 회복", "guard", "fused")
    def use(self, owner, battle, target_idx=0):
        owner.shield += 30
        owner.heal(10)

class WarCry(CardDef):
    def __init__(self):
        super().__init__("전투 함성", 2, "힘 +4 (둘다)\n카드 2장 드로우", "support", "fused")
    def use(self, owner, battle, target_idx=0):
        for p in battle.players:
            p.strength += 4
            p.draw_one()
            p.draw_one()

class OmegaStrike(CardDef):
    def __init__(self):
        super().__init__("오메가 일격", 4, "전체에\n50 데미지", "attack", "fused")
    def use(self, owner, battle, target_idx=0):
        for i in range(len(battle.enemies)):
            battle.damage_enemy(i, 50 + owner.strength * 3)


# ── Crafting recipes ──────────────────────────────────────────
# key: frozenset of two card class names → result class
RECIPES: dict[frozenset, type] = {
    frozenset(["일격",    "점화"]):       BlazingSlash,
    frozenset(["일격",    "방어"]):       GuardedStrike,
    frozenset(["철벽",    "치유"]):       SoulBarrier,
    frozenset(["함성",    "집중"]):       WarCry,
    frozenset(["강타",    "회오리"]):     OmegaStrike,
    frozenset(["일격",    "일격"]):       HeavySlash,
    frozenset(["방어",    "방어"]):       IronWall,
    frozenset(["흘려내기","반격"]):       FortressWall,
    frozenset(["분노",    "광전사"]):     OmegaStrike,
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
