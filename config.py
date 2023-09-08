from typing import Callable
from enum import Enum

MAX_BLOCK = 999
MAX_MANA = 999

class StatusEffect(Enum):
    VULNERABLE = "Vulnerable"
    WEAK = "Weak"
    ENTANGLE = "Entangle"

def add_stack(val1: int, val2: int) -> int:
    return val1 + val2
def no_stack(val1: int, val2: int) -> int:
    return val1
STACK_BEHAVIOR: dict[StatusEffect, Callable[[int, int], int]] = {
    StatusEffect.VULNERABLE: add_stack,
    StatusEffect.WEAK: add_stack,
    StatusEffect.ENTANGLE: no_stack,
}
def decrease(val: int) -> int:
    return (val-1) if val > 0 else 0
def remove(val: int) -> int:
    return 0
END_TURN_BEHAVIOR: dict[StatusEffect, Callable[[int], int]] = {
    StatusEffect.VULNERABLE: decrease,
    StatusEffect.WEAK: decrease,
    StatusEffect.ENTANGLE: remove,
}

class Character(Enum):
    IRON_CLAD = 1
    SILENT = 2
    DEFECT = 3
    WATCHER = 4

class CardType(Enum):
    ATTACK = 1
    SKILL = 2
    POWER = 3

class Rarity(Enum):
    STARTER = 1
    COMMON = 2
    UNCOMMON = 3
    RARE = 4

MAX_HEALTH: dict[Character, int] = {
    Character.IRON_CLAD: 80,
    Character.SILENT: 70,
    Character.DEFECT: 75,
    Character.WATCHER: 72,
}

CHARACTER_NAME: dict[Character, str] = {
    Character.IRON_CLAD: "IronClad",
    Character.SILENT: "Silent",
    Character.DEFECT: "Defect",
    Character.WATCHER: "Watcher",
}

class Verbose(Enum):
    NO_LOG = 0
    LOG = 1