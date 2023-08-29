from __future__ import annotations
from config import Character, MAX_HEALTH
from value import RandomUniformRange, ConstValue
from utility import RoundRobin, RoundRobinRandomStart, ItemSet
from action import Action, DealDamage
from target import PlayerCreature
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from battle import BattleState
    from game import GameState

class Creature:
    def __init__(self, max_health: int):
        self.max_health = max_health
        self.health = max_health

    def get_action(self, game_state: 'GameState', battle_state: BattleState) -> Action:
        raise NotImplementedError("The \"get_action\" method is not implemented for this Creature.")

class Player(Creature):
    def __init__(self, character: Character):
        self.character = character
        super().__init__(MAX_HEALTH[self.character])

class Enemy(Creature):
    def __init__(self, max_health: int):
        super().__init__(max_health)

class AcidSlimeSmall(Enemy):
    def __init__(self, game_state: GameState):
        max_health_gen = RandomUniformRange(8, 12) if game_state.ascention < 7 else RandomUniformRange(9, 13)
        super().__init__(max_health_gen.get())
        self.action_set: ItemSet[Action] = \
            RoundRobinRandomStart(DealDamage(ConstValue(3 if game_state.ascention < 2 else 4), PlayerCreature())) \
            if game_state.ascention < 17 else \
            RoundRobin(0, DealDamage(ConstValue(3 if game_state.ascention < 2 else 4), PlayerCreature()))
    
    def get_action(self, game_state: GameState, battle_state: BattleState) -> Action:
        return self.action_set.get()