from tqdm import tqdm
import pandas as pd
import time
import argparse
from joblib import delayed, Parallel
import sys
import os.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

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

def simulate_one(index: int, bot: GGPA, path: str, verbose: Verbose):
    game_state = GameState(Character.IRON_CLAD, bot, 0)
    game_state.add_to_deck(CardGen.Cleave(), CardGen.Impervious(), CardGen.Anger(), CardGen.Armaments())
    battle_state = BattleState(game_state, AcidSlimeSmall(game_state), SpikeSlimeSmall(game_state), JawWorm(game_state),
                               verbose=verbose, log_filename=os.path.join(path, f'{index}_{bot.name}'))
    battle_state.run()
    return [bot.name, game_state.player.health, game_state.get_end_results() != -1]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('test_count', type=int)
    parser.add_argument('thread_count', type=int, nargs='?', default=1)
    parser.add_argument('log_battles', type=bool, nargs='?', default=False)
    parser.add_argument('bots', nargs='+')
    args = parser.parse_args()

    test_count = args.test_count
    thread_count = args.thread_count
    verbose = Verbose.LOG if args.log_battles else Verbose.NO_LOG
    bots: list[GGPA] = [name_to_bot(name) for name in args.bots]  
    bot_names = '_'.join([bot.name for bot in bots])
    path = os.path.join('evaluation_results', f'{int(time.time())}_boteval_{test_count}_tests_{bot_names}')
    os.makedirs(path)
    print(f'simulating {test_count} times, for {bot_names} - {thread_count} threads')
    print(f'results can be found at {path}')
    results_dataset = Parallel(n_jobs=thread_count)(delayed(simulate_one)(i, bots[i%len(bots)], path, verbose) for i in tqdm(range(test_count * len(bots))))
    assert isinstance(results_dataset, list), "Parallel jobs have not resulted in an output of type list"
    df = pd.DataFrame(
        results_dataset,
        columns=["BotName", "PlayerHealth", "Win"]
    )
    df.to_csv(os.path.join(path, f"results.csv"), index=False)

if __name__ == '__main__':
    main()