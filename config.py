from enum import Enum

class StatusEffect(Enum):
    VULNERABLE = 1

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

MAX_HEALTH = {
    Character.IRON_CLAD: 80,
    Character.SILENT: 70,
    Character.DEFECT: 75,
    Character.WATCHER: 72,
}