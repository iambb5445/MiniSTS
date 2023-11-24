from tqdm import tqdm
import pandas as pd
import time
import argparse
from typing import Callable
from joblib import delayed, Parallel
import sys
import os.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from game import GameState
from battle import BattleState
from config import Character, Verbose
from agent import AcidSlimeSmall, SpikeSlimeSmall, JawWorm, Goblin, HobGoblin, Leech, Enemy
from card import CardGen, Card, CardRepo
from ggpa.ggpa import GGPA
from ggpa.random_bot import RandomBot
from ggpa.backtrack import BacktrackBot
from ggpa.chatgpt_bot import ChatGPTBot
from ggpa.prompt2 import PromptOption

def name_to_bot(name: str, limit_share: float) -> GGPA:
    if name == 'r':
        return RandomBot()
    if len(name) > 3 and name[0:3] == 'bts':
        depth = int(name[3:])
        return BacktrackBot(depth, True)
    if len(name) > 2 and name[0:2] == 'bt':
        depth = int(name[2:])
        return BacktrackBot(depth, False)
    if len(name) > 3 and name[:3] == 'gpt':
        _, model, prompt = name.split('-')
        model_dict: dict[str, ChatGPTBot.ModelName] = {
            't3.5': ChatGPTBot.ModelName.GPT_Turbo_35,
            '4': ChatGPTBot.ModelName.GPT_4,
            't4': ChatGPTBot.ModelName.GPT_Turbo_4,
            'it3.5': ChatGPTBot.ModelName.Instruct_GPT_Turbo_35,
            'idav': ChatGPTBot.ModelName.Instruct_Davinci,
        }
        prompt_dict: dict[str, PromptOption] = {
            'none': PromptOption.NONE,
            'dag': PromptOption.DAG,
            'cot': PromptOption.CoT,
            'cotr': PromptOption.CoT_rev,
        }
        return ChatGPTBot(model_dict[model], prompt_dict[prompt], False, limit_share)
    raise Exception("Bot name not recognized")

def get_enemies(enemies: str, game_state: GameState) -> list[Enemy]:
    ret: list[Enemy] = []
    for char in enemies:
        if char == 'g':
            ret.append(Goblin(game_state))
        elif char == 'h':
            ret.append(HobGoblin(game_state))
        elif char == 'l':
            ret.append(Leech(game_state))
        else:
            raise Exception(f"Enemies not recognized for {char} in {enemies}")
    return ret

def simulate_one(index: int, bot: GGPA, new_cards: list[Card]|None, deck: list[Card], enemies: str, path: str, verbose: Verbose):
    game_state = GameState(Character.IRON_CLAD, bot, 0)
    game_state.set_deck(*deck)
    if new_cards is not None:
        game_state.add_to_deck(*new_cards)
    battle_state = BattleState(game_state, *get_enemies(enemies, game_state),
                               verbose=verbose, log_filename=os.path.join(path, f'{index}_{"control" if new_cards is None else "-".join([card.name for card in new_cards])}'))
    battle_state.run()
    if isinstance(bot, ChatGPTBot):
        bot.dump_history(os.path.join(path, f'{index}_{bot.name}_history'))
    return [bot.name, game_state.player.health, game_state.get_end_results() != -1]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('test_count', type=int)
    parser.add_argument('thread_count', type=int)
    parser.add_argument('gen_count', type=int)
    parser.add_argument('enemies', type=str)
    parser.add_argument('bot', type=str)
    parser.add_argument('--name', type=str, default="")
    parser.add_argument('--dir', type=str, default="")
    parser.add_argument('--log', action=argparse.BooleanOptionalAction)
    args = parser.parse_args()

    test_count = args.test_count
    thread_count = args.thread_count
    gen_count = args.gen_count
    enemies = args.enemies
    custom_name = args.name
    custom_dir = args.dir
    verbose = Verbose.LOG if args.log else Verbose.NO_LOG
    bot: GGPA = name_to_bot(args.bot, 1/thread_count)
    bot_name = bot.name
    cards: list[Callable[[], Card]|None] = [CardRepo.get_random() for _ in range(gen_count)]
    cards.append(None)
    dir_name = f'{int(time.time())}_card_gen_{custom_name}_enemies_{enemies}_{test_count}_{bot_name}'
    if custom_dir != "":
        dir_name = os.path.join(custom_dir, dir_name)
    path = os.path.join('evaluation_results', dir_name)
    os.makedirs(path)
    print(f'simulating {test_count} times each for {gen_count} cards - {thread_count} threads')
    print(f'results can be found at {path}')
    results_dataset = Parallel(n_jobs=thread_count)(delayed(simulate_one)(i, bot,
                        None if cards[i//test_count] is None else [cards[i//test_count]()],
                        CardRepo.anonymize_deck(CardRepo.get_basics()), enemies, path, verbose
                        ) for i in tqdm(range(test_count * len(cards))))
    assert isinstance(results_dataset, list), "Parallel jobs have not resulted in an output of type list"
    df = pd.DataFrame(
        results_dataset,
        columns=["BotName", "PlayerHealth", "Win"]
    )
    df.to_csv(os.path.join(path, f"results.csv"), index=False)

if __name__ == '__main__':
    main()