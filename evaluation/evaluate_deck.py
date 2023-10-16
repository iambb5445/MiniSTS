from tqdm import tqdm
import pandas as pd
import time
import argparse
import sys
import os.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from game import GameState
from battle import BattleState
from config import Character, Verbose, CardType, Rarity
from agent import AcidSlimeSmall, SpikeSlimeSmall, JawWorm
from card import CardGen, Card
from ggpa.backtrack import BacktrackBot
from value import ConstValue, UpgradableOnce
from action.agent_targeted_action import DealAttackDamage
from target.agent_target import ChooseAgentTarget, AgentSet, AllAgentsTarget

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('test_count', type=int)
    args = parser.parse_args()

    test_count = args.test_count
    results_dataset: list[tuple[str, GameState]] = []
    card_lists: list[tuple[str, list[Card]]] = [
        ("Starter", []),
        ("Cleave", [CardGen.Cleave()]),
        ("BidDamage", [Card("BigDamage", CardType.ATTACK, ConstValue(1), Character.IRON_CLAD, Rarity.STARTER, DealAttackDamage(UpgradableOnce(100, 110)).To(ChooseAgentTarget(AgentSet.ENEMY)))]),
        ("WinCard", [Card("Win", CardType.ATTACK, ConstValue(1), Character.IRON_CLAD, Rarity.STARTER, DealAttackDamage(UpgradableOnce(100, 110)).To(AllAgentsTarget(AgentSet.ENEMY)))]),
        ("WinCard_10", [Card("Win", CardType.ATTACK, ConstValue(1), Character.IRON_CLAD, Rarity.STARTER, DealAttackDamage(UpgradableOnce(100, 110)).To(AllAgentsTarget(AgentSet.ENEMY)))] * 10),
        ("NothingCard", [Card("DoesNothing", CardType.ATTACK, ConstValue(1), Character.IRON_CLAD, Rarity.STARTER, DealAttackDamage(UpgradableOnce(0, 0)).To(AllAgentsTarget(AgentSet.ENEMY)))]),
        ("NothingCard_10", [Card("DoesNothing", CardType.ATTACK, ConstValue(1), Character.IRON_CLAD, Rarity.STARTER, DealAttackDamage(UpgradableOnce(0, 0)).To(AllAgentsTarget(AgentSet.ENEMY)))] * 10),
    ]
    for name, card_list in card_lists:
        for _ in tqdm(range(test_count)):
            game_state = GameState(Character.IRON_CLAD, BacktrackBot(3, False), 0)
            game_state.add_to_deck(*card_list)
            battle_state = BattleState(game_state, AcidSlimeSmall(game_state), SpikeSlimeSmall(game_state), JawWorm(game_state), verbose=Verbose.NO_LOG)
            battle_state.run()
            results_dataset.append((name, game_state))
    df = pd.DataFrame(
        [[name, game_state.player.health, game_state.get_end_results() != -1] for name, game_state in results_dataset],
        columns=["DeckName", "PlayerHealth", "Win"]
    )
    deck_name = '_'.join([name for name, _ in card_lists])
    df.to_csv(f"evaluation_results\\evaluation_on_{test_count}_tests_{deck_name}_{int(time.time())}.csv", index=False)

if __name__ == '__main__':
    main()