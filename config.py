from enum import Enum

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