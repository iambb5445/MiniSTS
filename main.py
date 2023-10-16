from game import GameState
from battle import BattleState
from config import Character, Verbose
from agent import AcidSlimeSmall, SpikeSlimeSmall, JawWorm
from card import CardGen
from ggpa.human_input import HumanInput

def main():
    game_state = GameState(Character.IRON_CLAD, HumanInput(False), 0)
    game_state.add_to_deck(CardGen.Cleave(), CardGen.Impervious(), CardGen.Anger(), CardGen.Armaments())
    battle_state = BattleState(game_state, AcidSlimeSmall(game_state), SpikeSlimeSmall(game_state), JawWorm(game_state), verbose=Verbose.LOG)
    battle_state.run()

if __name__ == '__main__':
    main()