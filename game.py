from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from card import Card
from creature import Player
from config import Character

class GameState:
    def __init__(self, character: Character, ascention: int):
        self.player = Player(character)
        self.ascention = ascention
        self.deck: list[Card] = []