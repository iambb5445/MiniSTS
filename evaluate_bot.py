from tqdm import tqdm
import pandas as pd
import time
from game import GameState
from battle import BattleState
from config import Character, Verbose
from agent import AcidSlimeSmall, SpikeSlimeSmall, JawWorm
from card import CardGen
from ggpa.ggpa import GGPA
from ggpa.random_bot import RandomBot
from ggpa.backtrack import BacktrackBot

def main():
    test_count = 100
    results_dataset: list[tuple[str, GameState]] = []
    bots: list[GGPA] = [RandomBot(), BacktrackBot(3)]
    for bot in bots:
        for _ in tqdm(range(test_count)):
            game_state = GameState(Character.IRON_CLAD, bot, 0)
            game_state.add_to_deck(CardGen.Cleave(), CardGen.Impervious(), CardGen.Anger(), CardGen.Armaments())
            battle_state = BattleState(game_state, AcidSlimeSmall(game_state), SpikeSlimeSmall(game_state), JawWorm(game_state), verbose=Verbose.NO_LOG)
            battle_state.run()
            results_dataset.append((bot.name, game_state))
    df = pd.DataFrame(
        [[name, game_state.player.health, game_state.get_end_results() != -1] for name, game_state in results_dataset],
        columns=["BotName", "PlayerHealth", "Win"]
    )
    df.to_csv(f"evaluation_results\\evaluation_on_{test_count}_tests_{int(time.time())}.csv", index=False)

if __name__ == '__main__':
    main()