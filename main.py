from game import GameState
from battle import BattleState
from config import Character, Verbose
from agent import AcidSlimeSmall, SpikeSlimeSmall, JawWorm
from card import CardGen, CardRepo
import time
from ggpa.human_input import HumanInput
from ggpa.chatgpt_bot import ChatGPTBot
from ggpa.backtrack import BacktrackBot
from ggpa.backtrack_parallel import BacktrackParallelBot

def main():
    # agent = HumanInput(True)
    #agent = BacktrackParallelBot(6)
    agent = BacktrackBot(4, False)
    game_state = GameState(Character.IRON_CLAD, agent, 0)
    game_state.set_deck(*CardRepo.get_scenario_3()[1])
    battle_state = BattleState(game_state, AcidSlimeSmall(game_state), SpikeSlimeSmall(game_state), JawWorm(game_state), verbose=Verbose.LOG)
    start = time.time()
    battle_state.run()
    end = time.time()
    print(end-start)
    #agent.dump_history("bot_history")

if __name__ == '__main__':
    main()