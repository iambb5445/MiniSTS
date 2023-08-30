from game import GameState
from battle import BattleState
from config import Character
from creature import AcidSlimeSmall

def main():
    game_state = GameState(Character.IRON_CLAD, 0)
    battle_state = BattleState(game_state, AcidSlimeSmall(game_state))
    print(battle_state)
    battle_state.take_turn()

if __name__ == '__main__':
    main()