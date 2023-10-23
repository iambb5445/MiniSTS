from enum import Enum

MAX_BLOCK = 999
MAX_MANA = 999
MAX_STATUS = 999

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
    FILE_LOG = 2