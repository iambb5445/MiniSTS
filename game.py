from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from card import Card
    from ggpa.ggpa import GGPA
from agent import Player
from config import Character
from card import CardRepo

class GameState:
    def __init__(self, character: Character, bot: GGPA, ascention: int):
        self.player = Player(character, bot)
        self.ascention = ascention
        self.deck: list[Card] = CardRepo.get_starter(character)
        self.draw_count = 5
        self.max_mana = 3

    def add_to_deck(self, *cards: Card):
        for card in cards:
            self.deck.append(card)

    def set_deck(self, *cards: Card):
        self.deck = [card for card in cards]

    def get_end_results(self):
        if self.player.is_dead():
            return -1
        return 1 # TODO is this a good idea? is this actually win?