from config import Character, MAX_HEALTH
from value import RandomUniformRange
from game import GameState
from battle import BattleState

class Creature:
    def __init__(self, max_health: int):
        self.max_health = max_health
        self.health = max_health

    def get_action(self, game_state: GameState, battle_state: BattleState):
        pass

class Player(Creature):
    def __init__(self, character: Character):
        super().__init__(MAX_HEALTH[self.character])
        self.character = character

class Enemy(Creature):
    def __init__(self, max_health: int):
        super().__init__(max_health)

class AcidSlimeSmall(Enemy):
    def __init__(self, game_state: GameState):
        max_health_gen = RandomUniformRange(8, 12) if game_state.ascention < 7 else RandomUniformRange(9, 13)
        super().__init__(max_health_gen.get())
    
    def get_action(self, game_state: GameState, battle_state: BattleState):
        pass