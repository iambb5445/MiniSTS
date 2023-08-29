from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from card import Card
    from creature import Creature

from enum import Enum

class CreatureSet(Enum):
        ENEMY = 1
        ALL = 2

class CreatureTarget:
    def get(self) -> Creature:
        raise NotImplementedError("The \"get\" method is not implemented for this CreateTarget.")

class SelfCreature(CreatureTarget):
    pass

class PlayerCreature(CreatureTarget):
    pass

class ChooseCreature(CreatureTarget):
    def __init__(self, among: CreatureSet, count: int = 1):
        self.among = among
        self.count = count

class RandomCreature(CreatureTarget):
    def __init__(self, among: CreatureSet, count: int = 1):
        self.among = among
        self.count = count

class AllCreature(CreatureTarget):
    def __init__(self, among: CreatureSet):
        self.among = among

class CardPile(Enum):
    HAND = 1
    DISCARD = 2

class CardTarget:
    def get(self) -> Card:
        raise NotImplementedError("The \"get\" method is not implemented for this CreateTarget.")

class SelfCard(CardTarget):
    pass

class ChooseCard(CardTarget):
    def __init__(self, among: CardPile, count: int = 1):
        self.among = among
        self.count = count

class AllCard(CardTarget):
    def __init__(self, among: CardPile):
        self.among = among