import random


class Enemy:
    def __init__(self, name, hp, strength=0):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.block = 0
        self.strength = strength
        self.vulnerable = 0
        self.intent = None
        self.intent_value = 0

    def take_damage(self, amount):
        if self.vulnerable > 0:
            amount = int(amount * 1.5)
        dmg = max(0, amount - self.block)
        self.block = max(0, self.block - amount)
        self.hp -= dmg
        self.hp = max(0, self.hp)

    def is_alive(self):
        return self.hp > 0

    def decide_intent(self):
        pass

    def execute_intent(self, player):
        pass

    def start_turn(self):
        self.block = 0
        self.vulnerable = max(0, self.vulnerable - 1)
        self.decide_intent()

    def get_intent_text(self):
        if self.intent == "attack":
            return f"Attack {self.intent_value}"
        elif self.intent == "defend":
            return f"Defend {self.intent_value}"
        elif self.intent == "buff":
            return "Buff"
        return "???"


class Slime(Enemy):
    def __init__(self):
        super().__init__("Slime", random.randint(14, 18))
        self.decide_intent()

    def decide_intent(self):
        self.intent = "attack"
        self.intent_value = random.randint(5, 8)

    def execute_intent(self, player):
        if self.intent == "attack":
            player.take_damage(self.intent_value + self.strength)


class Cultist(Enemy):
    def __init__(self):
        super().__init__("Cultist", random.randint(48, 54))
        self.turn = 0
        self.decide_intent()

    def decide_intent(self):
        if self.turn == 0:
            self.intent = "buff"
        else:
            self.intent = "attack"
            self.intent_value = 6 + self.strength

    def execute_intent(self, player):
        if self.intent == "buff":
            self.strength += 3
        elif self.intent == "attack":
            player.take_damage(self.intent_value)
        self.turn += 1
        self.decide_intent()


class Goblin(Enemy):
    def __init__(self):
        super().__init__("Goblin", random.randint(10, 15), strength=1)
        self.decide_intent()

    def decide_intent(self):
        r = random.random()
        if r < 0.6:
            self.intent = "attack"
            self.intent_value = random.randint(4, 7)
        else:
            self.intent = "defend"
            self.intent_value = random.randint(4, 6)

    def execute_intent(self, player):
        if self.intent == "attack":
            player.take_damage(self.intent_value + self.strength)
        elif self.intent == "defend":
            self.block += self.intent_value


class JawWorm(Enemy):
    def __init__(self):
        super().__init__("Jaw Worm", random.randint(40, 44))
        self.decide_intent()

    def decide_intent(self):
        r = random.random()
        if r < 0.45:
            self.intent = "attack"
            self.intent_value = random.randint(11, 14)
        elif r < 0.75:
            self.intent = "defend"
            self.intent_value = random.randint(6, 9)
        else:
            self.intent = "attack"
            self.intent_value = 7

    def execute_intent(self, player):
        if self.intent == "attack":
            player.take_damage(self.intent_value + self.strength)
        elif self.intent == "defend":
            self.block += self.intent_value


class Louse(Enemy):
    def __init__(self):
        super().__init__("Louse", random.randint(10, 15))
        self.decide_intent()

    def decide_intent(self):
        self.intent = "attack"
        self.intent_value = random.randint(5, 7)

    def execute_intent(self, player):
        player.take_damage(self.intent_value)
        if random.random() < 0.25:
            player.vulnerable += 1


# Boss enemies
class SlimeBoss(Enemy):
    def __init__(self):
        super().__init__("Slime Boss", 140)
        self.pattern = ["defend", "attack", "attack", "buff"]
        self.idx = 0
        self.decide_intent()

    def decide_intent(self):
        action = self.pattern[self.idx % len(self.pattern)]
        self.intent = action
        if action == "attack":
            self.intent_value = 16
        elif action == "defend":
            self.intent_value = 12
        elif action == "buff":
            self.intent_value = 0

    def execute_intent(self, player):
        if self.intent == "attack":
            player.take_damage(self.intent_value + self.strength)
        elif self.intent == "defend":
            self.block += self.intent_value
        elif self.intent == "buff":
            self.strength += 2
        self.idx += 1
        self.decide_intent()


class HexaGhost(Enemy):
    def __init__(self):
        super().__init__("Hexa Ghost", 250, strength=2)
        self.decide_intent()

    def decide_intent(self):
        self.intent = "attack"
        self.intent_value = random.randint(6, 10)

    def execute_intent(self, player):
        hits = random.randint(2, 4)
        for _ in range(hits):
            player.take_damage(self.intent_value + self.strength)
        self.decide_intent()


NORMAL_ENEMIES = [Slime, Cultist, Goblin, JawWorm, Louse]
BOSS_ENEMIES = [SlimeBoss, HexaGhost]


def get_random_enemy(floor):
    if floor % 5 == 0:
        return random.choice(BOSS_ENEMIES)()
    count = random.randint(1, 2)
    if count == 1:
        return random.choice(NORMAL_ENEMIES)()
    e1 = random.choice(NORMAL_ENEMIES)()
    return e1  # single enemy for simplicity


def get_enemy_group(floor):
    if floor > 0 and floor % 5 == 0:
        return [random.choice(BOSS_ENEMIES)()]
    count = random.randint(1, 3)
    return [random.choice(NORMAL_ENEMIES)() for _ in range(count)]
