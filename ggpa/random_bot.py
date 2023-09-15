from __future__ import annotations
import random
from ggpa.ggpa import GGPA
from action.action import EndAgentTurn, PlayCard
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game import GameState
    from battle import BattleState
    from agent import Agent
    from card import Card
    from agent import Agent
    from card import Card

class RandomBot(GGPA):
    def __init__(self):
        super().__init__("RandomBot")

    def choose_card(self, game_state: GameState, battle_state: BattleState) -> EndAgentTurn|PlayCard:
        options = self.get_choose_card_options(game_state, battle_state)
        return random.choice(options)
    
    def choose_agent_target(self, battle_state: BattleState, list_name: str, agent_list: list[Agent]) -> Agent:
        return random.choice(agent_list)
    
    def choose_card_target(self, battle_state: BattleState, list_name: str, card_list: list[Card]) -> Card:
        return random.choice(card_list)
    