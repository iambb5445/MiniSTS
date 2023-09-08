from game import GameState
from battle import BattleState
from config import Character, Verbose
from agent import AcidSlimeSmall
from card import CardGen
from ggpa.random_bot import RandomBot

def main():
    game_state = GameState(Character.IRON_CLAD, RandomBot(), 0)
    game_state.deck.append(CardGen.Cleave())
    game_state.deck.append(CardGen.Impervious())
    game_state.deck.append(CardGen.Anger())
    game_state.deck.append(CardGen.Armaments())
    battle_state = BattleState(game_state, AcidSlimeSmall(game_state), AcidSlimeSmall(game_state))
    battle_state.run(Verbose.LOG)
    for card in game_state.deck:
        print(card.__repr__())

if __name__ == '__main__':
    main()