from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from card import Card
from agent import Player
from config import Character
from card import CardRepo

class GameState:
    def __init__(self, character: Character, ascention: int):
        self.player = Player(character)
        self.ascention = ascention
        self.deck: list[Card] = CardRepo.get_starter(character)
        # TODO
        self.draw_count = 5
        self.max_mana = 3