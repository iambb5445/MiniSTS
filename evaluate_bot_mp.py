from tqdm import tqdm
import pandas as pd
import time
import argparse
from joblib import delayed, Parallel
from game import GameState
from battle import BattleState
from config import Character, Verbose
from agent import AcidSlimeSmall, SpikeSlimeSmall, JawWorm
from card import CardGen
from ggpa.ggpa import GGPA
from ggpa.random_bot import RandomBot
from ggpa.backtrack import BacktrackBot
from ggpa.chatgpt_bot import ChatGPTBot

def name_to_bot(name: str) -> GGPA:
    if name == 'r':
        return RandomBot()
    if len(name) > 2 and name[0:2] == 'bt':
        depth = int(name[2:])
        return BacktrackBot(depth, True)
    if name == 'gpt-t3.5':
        return ChatGPTBot(ChatGPTBot.ModelName.GPT_Turbo_35)
    if name == 'gpt-4':
        return ChatGPTBot(ChatGPTBot.ModelName.GPT_4)
    if name == 'gpt-it3.5':
        return ChatGPTBot(ChatGPTBot.ModelName.Instruct_GPT_Turbo_35)
    if name == 'gpt-idav':
        return ChatGPTBot(ChatGPTBot.ModelName.Instruct_Davinci)
    raise Exception("Bot name not recognized")

def simulate_one(bot: GGPA):
    game_state = GameState(Character.IRON_CLAD, bot, 0)
    game_state.add_to_deck(CardGen.Cleave(), CardGen.Impervious(), CardGen.Anger(), CardGen.Armaments())
    battle_state = BattleState(game_state, AcidSlimeSmall(game_state), SpikeSlimeSmall(game_state), JawWorm(game_state), verbose=Verbose.NO_LOG)
    battle_state.run()
    return [bot.name, game_state.player.health, game_state.get_end_results() != -1]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('test_count', type=int)
    parser.add_argument('bots', nargs='+')
    args = parser.parse_args()

    test_count = args.test_count
    bots: list[GGPA] = [name_to_bot(name) for name in args.bots]  
    results_dataset = Parallel(n_jobs=8)(delayed(simulate_one)(bot) for bot in bots for _ in tqdm(range(test_count)))
    assert isinstance(results_dataset, list), "Parallel jobs have not resulted in an output of type list"
    df = pd.DataFrame(
        results_dataset,
        columns=["BotName", "PlayerHealth", "Win"]
    )
    bot_names = '_'.join([bot.name for bot in bots])
    df.to_csv(f"evaluation_results\\mp_evaluation_on_{test_count}_tests_{bot_names}_{int(time.time())}.csv", index=False)

if __name__ == '__main__':
    main()