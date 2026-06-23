import random
from constants import ENEMY_WARN_SEC


class Enemy:
    def __init__(self, name, hp, strength=0):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.strength = strength
        self.burn = 0
        self.alive = True

        self.intent = None
        self.intent_value = 0
        self.warn_timer = 0.0
        self.warn_total = ENEMY_WARN_SEC

        self._decide()

    def is_alive(self):
        return self.hp > 0 and self.alive

    def take_damage(self, amount):
        self.hp = max(0, self.hp - amount)
        if self.hp == 0:
            self.alive = False

    def update(self, dt, players):
        if not self.is_alive():
            return
        self.warn_timer += dt
        if self.warn_timer >= self.warn_total:
            self._execute(players)
            self._decide()
            self.warn_timer = 0.0

    def _decide(self):
        pass

    def _execute(self, players):
        if self.burn > 0:
            self.take_damage(self.burn)
            self.burn = max(0, self.burn - 1)

    def warn_frac(self):
        return min(1.0, self.warn_timer / self.warn_total)

    def intent_label(self):
        if self.intent == "attack":
            return f"⚔  {self.intent_value} 데미지 예고"
        if self.intent == "buff":
            return "↑  강화 중..."
        if self.intent == "heal":
            return f"♥  {self.intent_value} 회복 예고"
        return "?"


# ── 일반 적 ──────────────────────────────────────────────────
class Slime(Enemy):
    def __init__(self, floor=1):
        hp = random.randint(30, 45) + floor * 4
        self.floor = floor
        super().__init__("슬라임", hp)
    def _decide(self):
        self.intent = "attack"
        self.intent_value = random.randint(8, 14) + self.floor
        # 층수 높을수록 조금 빨라짐, 하지만 최소 3.5초
        self.warn_total = max(3.5, ENEMY_WARN_SEC - self.floor * 0.1)
    def _execute(self, players):
        super()._execute(players)
        if self.is_alive():
            p = next((p for p in players if p.alive), None)
            if p:
                p.take_damage(self.intent_value + self.strength)


class Goblin(Enemy):
    def __init__(self, floor=1):
        hp = random.randint(25, 40) + floor * 3
        self.floor = floor
        super().__init__("고블린", hp, strength=1 + floor // 3)
    def _decide(self):
        if random.random() < 0.75:
            self.intent = "attack"
            self.intent_value = random.randint(10, 16) + self.floor
            self.warn_total = max(3.2, ENEMY_WARN_SEC - self.floor * 0.12)
        else:
            self.intent = "heal"
            self.intent_value = 12 + self.floor * 2
            self.warn_total = 4.0
    def _execute(self, players):
        super()._execute(players)
        if not self.is_alive():
            return
        if self.intent == "attack":
            p = next((p for p in players if p.alive), None)
            if p:
                p.take_damage(self.intent_value + self.strength)
        else:
            self.hp = min(self.max_hp, self.hp + self.intent_value)


class Cultist(Enemy):
    def __init__(self, floor=1):
        hp = random.randint(60, 85) + floor * 5
        self.floor = floor
        self._turn = 0
        super().__init__("광신도", hp)
    def _decide(self):
        if self._turn == 0:
            self.intent = "buff"
            self.intent_value = 4
            self.warn_total = 4.5
        else:
            self.intent = "attack"
            self.intent_value = 12 + self.strength + self.floor
            self.warn_total = max(3.0, ENEMY_WARN_SEC - self.floor * 0.1)
    def _execute(self, players):
        super()._execute(players)
        if not self.is_alive():
            return
        if self.intent == "buff":
            self.strength += 4
        else:
            p = next((p for p in players if p.alive), None)
            if p:
                p.take_damage(self.intent_value)
        self._turn += 1


class OrcWarrior(Enemy):
    def __init__(self, floor=1):
        hp = random.randint(80, 110) + floor * 6
        self.floor = floor
        super().__init__("오크 전사", hp, strength=3 + floor // 2)
    def _decide(self):
        self.intent = "attack"
        self.intent_value = random.randint(18, 26) + self.floor
        self.warn_total = max(3.8, ENEMY_WARN_SEC - self.floor * 0.08)
    def _execute(self, players):
        super()._execute(players)
        if self.is_alive():
            p = next((p for p in players if p.alive), None)
            if p:
                p.take_damage(self.intent_value + self.strength)


class Troll(Enemy):
    def __init__(self, floor=1):
        hp = random.randint(100, 130) + floor * 7
        self.floor = floor
        self._phase = 0
        super().__init__("트롤", hp, strength=2 + floor // 3)
    def _decide(self):
        if self._phase % 3 == 2:
            self.intent = "heal"
            self.intent_value = 20 + self.floor * 2
            self.warn_total = 5.0
        else:
            self.intent = "attack"
            self.intent_value = random.randint(20, 30) + self.floor
            self.warn_total = max(3.5, ENEMY_WARN_SEC - self.floor * 0.1)
    def _execute(self, players):
        super()._execute(players)
        if not self.is_alive():
            return
        if self.intent == "heal":
            self.hp = min(self.max_hp, self.hp + self.intent_value)
        else:
            p = next((p for p in players if p.alive), None)
            if p:
                p.take_damage(self.intent_value + self.strength)
        self._phase += 1


# ── 보스 ─────────────────────────────────────────────────────
class SlimeBoss(Enemy):
    def __init__(self, floor=5):
        hp = 220 + floor * 10
        self.floor = floor
        self._phase = 0
        super().__init__("슬라임 왕", hp, strength=4)
    def _decide(self):
        pattern = ["attack", "attack", "buff", "attack", "attack"]
        self.intent = pattern[self._phase % len(pattern)]
        if self.intent == "attack":
            self.intent_value = 22 + self.strength + self.floor
            self.warn_total = max(3.2, ENEMY_WARN_SEC - self.floor * 0.08)
        else:
            self.warn_total = 4.0
    def _execute(self, players):
        super()._execute(players)
        if not self.is_alive():
            return
        if self.intent == "attack":
            p = next((p for p in players if p.alive), None)
            if p:
                p.take_damage(self.intent_value)
        else:
            self.strength += 4
        self._phase += 1


class DragonLord(Enemy):
    def __init__(self, floor=10):
        hp = 380 + floor * 12
        self.floor = floor
        self._phase = 0
        super().__init__("드래곤 군주", hp, strength=6)
    def _decide(self):
        pattern = ["attack", "attack", "buff", "attack", "heal"]
        self.intent = pattern[self._phase % len(pattern)]
        if self.intent == "attack":
            self.intent_value = 28 + self.strength + self.floor
            self.warn_total = max(3.0, ENEMY_WARN_SEC - self.floor * 0.07)
        elif self.intent == "heal":
            self.intent_value = 50
            self.warn_total = 5.0
        else:
            self.warn_total = 4.0
    def _execute(self, players):
        super()._execute(players)
        if not self.is_alive():
            return
        if self.intent == "attack":
            p = next((p for p in players if p.alive), None)
            if p:
                p.take_damage(self.intent_value)
        elif self.intent == "heal":
            self.hp = min(self.max_hp, self.hp + self.intent_value)
        else:
            self.strength += 5
        self._phase += 1


NORMAL_POOL = [Slime, Goblin, Cultist, OrcWarrior, Troll]
BOSS_POOL   = [SlimeBoss, DragonLord]


def make_enemy_group(floor: int):
    if floor % 5 == 0:
        boss_cls = SlimeBoss if floor == 5 else DragonLord
        return [boss_cls(floor)]
    count = 1 if floor <= 2 else (2 if floor <= 6 else random.randint(1, 2))
    pool = NORMAL_POOL[:max(2, floor // 2)]  # 층수 높을수록 강한 적 등장
    return [random.choice(pool)(floor) for _ in range(count)]
