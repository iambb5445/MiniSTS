from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from creature import Enemy
    from game import GameState

class BattleState:
    def __init__(self, game_state: GameState, *enemies: Enemy):
        self.turn = 0
        self.player = game_state.player
        self.enemies = [enemy for enemy in enemies]
        self.game_state = game_state
    
    def take_turn(self):
        print(self.player.get_action(self.game_state, self))
        for enemy in self.enemies:
            print(enemy.get_action(self.game_state, self))