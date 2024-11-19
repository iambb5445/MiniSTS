from game import GameState
from battle import BattleState
from config import Character, Verbose
from agent import AcidSlimeSmall, SpikeSlimeSmall, JawWorm
from card import CardGen, CardRepo
import time
from ggpa.human_input import HumanInput
from ggpa.chatgpt_bot import ChatGPTBot
from ggpa.prompt2 import PromptOption
from ggpa.backtrack import BacktrackBot
from ggpa.backtrack_parallel import BacktrackParallelBot

def main():
    agent = HumanInput(True)
    # agent = BacktrackBot(4, False)
    # agent = ChatGPTBot(ChatGPTBot.ModelName.GPT_Turbo_35, PromptOption.CoT, 0, False, 1)
    game_state = GameState(Character.IRON_CLAD, agent, 0)
    game_state.set_deck(*CardRepo.get_scenario_0()[1])
    # game_state.set_deck(CardGen.Strike(), CardGen.Defend(), CardGen.Defend())
    # game_state.add_to_deck(CardGen.Strike(), CardGen.Defend(), CardGen.Defend())
    battle_state = BattleState(game_state, JawWorm(game_state), verbose=Verbose.LOG)
    start = time.time()
    battle_state.run()
    end = time.time()
    print(f"run ended in {end-start} seconds")
    # to save all the requests and responses for the ChatGPTBot agent, use:
    # agent.dump_history("bot_history")

if __name__ == '__main__':
    main()