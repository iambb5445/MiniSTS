from game import GameState
from battle import BattleState
from config import Character
from agent import AcidSlimeSmall

def main():
    game_state = GameState(Character.IRON_CLAD, 0)
    battle_state = BattleState(game_state, AcidSlimeSmall(game_state))
    battle_state.run()

if __name__ == '__main__':
    main()