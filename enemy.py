import random
from constants import ENEMY_WARN_SEC


class Enemy:
    def __init__(self, name, hp, strength=0):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.strength = strength
        self.burn = 0         # damage per action
        self.alive = True

        self.intent = None    # "attack" / "buff" / "heal"
        self.intent_value = 0
        self.warn_timer = 0.0
        self.warn_total = ENEMY_WARN_SEC
        self._action_cd = 0.0  # cooldown between actions

        self._decide()

    # ── state ───────────────────────────────────────────────────
    def is_alive(self):
        return self.hp > 0 and self.alive

    def take_damage(self, amount):
        self.hp = max(0, self.hp - amount)
        if self.hp == 0:
            self.alive = False

    # ── real-time update ────────────────────────────────────────
    def update(self, dt, players):
        if not self.is_alive():
            return

        self.warn_timer += dt
        if self.warn_timer >= self.warn_total:
            self._execute(players)
            self._decide()
            self.warn_timer = 0.0

    # ── intent ──────────────────────────────────────────────────
    def _decide(self):
        pass  # subclass

    def _execute(self, players):
        # burn tick
        if self.burn > 0:
            self.take_damage(self.burn)
            self.burn = max(0, self.burn - 1)

    def warn_frac(self):
        return min(1.0, self.warn_timer / self.warn_total)

    def intent_label(self):
        if self.intent == "attack":
            return f"⚔ Attack {self.intent_value}"
        if self.intent == "buff":
            return "↑ Buff"
        if self.intent == "heal":
            return f"♥ Heal {self.intent_value}"
        return "?"


# ── Concrete enemies ─────────────────────────────────────────
class Slime(Enemy):
    def __init__(self):
        super().__init__("Slime", random.randint(18, 26))
    def _decide(self):
        self.intent = "attack"
        self.intent_value = random.randint(6, 10)
        self.warn_total = random.uniform(1.8, 2.6)
    def _execute(self, players):
        super()._execute(players)
        if self.is_alive():
            target = random.choice([p for p in players if p.alive])
            target.take_damage(self.intent_value + self.strength)


class Cultist(Enemy):
    def __init__(self):
        super().__init__("Cultist", random.randint(50, 60))
        self._turn = 0
    def _decide(self):
        if self._turn == 0:
            self.intent = "buff"
            self.intent_value = 3
            self.warn_total = 2.0
        else:
            self.intent = "attack"
            self.intent_value = 8 + self.strength
            self.warn_total = random.uniform(1.6, 2.2)
    def _execute(self, players):
        super()._execute(players)
        if not self.is_alive():
            return
        if self.intent == "buff":
            self.strength += 3
        else:
            alive = [p for p in players if p.alive]
            if alive:
                random.choice(alive).take_damage(self.intent_value)
        self._turn += 1


class Goblin(Enemy):
    def __init__(self):
        super().__init__("Goblin", random.randint(14, 20), strength=1)
    def _decide(self):
        if random.random() < 0.7:
            self.intent = "attack"
            self.intent_value = random.randint(5, 9)
            self.warn_total = random.uniform(1.2, 2.0)
        else:
            self.intent = "heal"
            self.intent_value = 6
            self.warn_total = 2.5
    def _execute(self, players):
        super()._execute(players)
        if not self.is_alive():
            return
        if self.intent == "attack":
            alive = [p for p in players if p.alive]
            if alive:
                random.choice(alive).take_damage(self.intent_value + self.strength)
        else:
            self.hp = min(self.max_hp, self.hp + self.intent_value)


class OrcWarrior(Enemy):
    def __init__(self):
        super().__init__("Orc", random.randint(55, 70), strength=2)
    def _decide(self):
        self.intent = "attack"
        self.intent_value = random.randint(12, 18)
        self.warn_total = random.uniform(2.0, 3.0)
    def _execute(self, players):
        super()._execute(players)
        if self.is_alive():
            alive = [p for p in players if p.alive]
            if alive:
                random.choice(alive).take_damage(self.intent_value + self.strength)


# ── Bosses ───────────────────────────────────────────────────
class SlimeBoss(Enemy):
    def __init__(self):
        super().__init__("Slime King", 180, strength=2)
        self._phase = 0
    def _decide(self):
        pattern = ["attack", "attack", "buff", "attack"]
        self.intent = pattern[self._phase % len(pattern)]
        if self.intent == "attack":
            self.intent_value = 18 + self.strength
            self.warn_total = random.uniform(1.8, 2.4)
        else:
            self.intent_value = 0
            self.warn_total = 2.2
    def _execute(self, players):
        super()._execute(players)
        if not self.is_alive():
            return
        if self.intent == "attack":
            for p in [p for p in players if p.alive]:
                p.take_damage(self.intent_value)
        else:
            self.strength += 3
        self._phase += 1


class DragonLord(Enemy):
    def __init__(self):
        super().__init__("Dragon Lord", 280, strength=4)
        self._phase = 0
    def _decide(self):
        pattern = ["attack", "attack", "buff", "attack", "heal"]
        self.intent = pattern[self._phase % len(pattern)]
        if self.intent == "attack":
            self.intent_value = 22 + self.strength
            self.warn_total = random.uniform(1.5, 2.2)
        elif self.intent == "heal":
            self.intent_value = 30
            self.warn_total = 3.0
        else:
            self.intent_value = 0
            self.warn_total = 2.0
    def _execute(self, players):
        super()._execute(players)
        if not self.is_alive():
            return
        if self.intent == "attack":
            for p in [p for p in players if p.alive]:
                p.take_damage(self.intent_value)
        elif self.intent == "heal":
            self.hp = min(self.max_hp, self.hp + self.intent_value)
        else:
            self.strength += 4
        self._phase += 1


NORMAL_POOL = [Slime, Cultist, Goblin, OrcWarrior]
BOSS_POOL   = [SlimeBoss, DragonLord]


def make_enemy_group(floor: int):
    if floor > 0 and floor % 5 == 0:
        return [random.choice(BOSS_POOL)()]
    count = 1 if floor < 3 else random.randint(1, 2)
    return [random.choice(NORMAL_POOL)() for _ in range(count)]
