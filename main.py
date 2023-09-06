from game import GameState
from battle import BattleState
from config import Character
from agent import AcidSlimeSmall
from card import CardGen

def main():
    game_state = GameState(Character.IRON_CLAD, 0)
    game_state.deck.append(CardGen.CLEAVE())
    game_state.deck.append(CardGen.IMPERVIOUS())
    battle_state = BattleState(game_state, AcidSlimeSmall(game_state), AcidSlimeSmall(game_state))
    battle_state.run()

if __name__ == '__main__':
    main()