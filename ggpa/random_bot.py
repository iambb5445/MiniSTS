from __future__ import annotations
import random
from agent import Agent
from battle import BattleState
from card import Card
from game import GameState
from action.action import NoAction, PlayCard, Action
from ggpa.ggpa import GGPA
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game import GameState
    from battle import BattleState
    from agent import Agent
    from card import Card

class RandomBot(GGPA):
    def choose_card(self, game_state: GameState, battle_state: BattleState) -> Action:
        options: list[Action] = [PlayCard(i) for i in range(len(battle_state.hand)) if battle_state.is_playable(battle_state.hand[i])]
        options.append(NoAction())
        choice = random.choice(options)
        if choice == options[-1]:
            battle_state.end_player_turn()
        return choice
    
    def choose_agent_target(self, battle_state: BattleState, list_name: str, agent_list: list[Agent]) -> Agent:
        return random.choice(agent_list)
    
    def choose_card_target(self, battle_state: BattleState, list_name: str, card_list: list[Card]) -> Card:
        return random.choice(card_list)
    