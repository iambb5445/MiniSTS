from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from creature import Enemy
    from game import GameState

import random

class BattleState:
    def __init__(self, game_state: GameState, *enemies: Enemy):
        self.turn = 0
        self.player = game_state.player
        self.enemies = [enemy for enemy in enemies]
        self.game_state = game_state
        self._start()

    def _start(self):
        self.draw_pile = [card for card in self.game_state.deck]
        random.shuffle(self.draw_pile)
        draw_count = 5 # TODO
        draw_count = max(draw_count, len(self.draw_pile))
        self.hand, self.draw_pile = self.draw_pile[:draw_count], self.draw_pile[draw_count:]
    
    def get_hand(self):
        return self.hand

    def discard(self, card_index: int):
        assert card_index < len(self.hand) and card_index > 0, "Card index {} out of range for hand {}".format(card_index, self.hand)
    
    def take_turn(self):
        print(self.player.get_action(self.game_state, self))
        for enemy in self.enemies:
            print(enemy.get_action(self.game_state, self))