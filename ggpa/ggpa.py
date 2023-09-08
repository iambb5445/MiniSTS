from __future__ import annotations
from agent import Agent
from battle import BattleState
from card import Card
from game import GameState
from action.action import Action
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game import GameState
    from battle import BattleState
    from agent import Agent
    from card import Card

class GGPA:
    def __init__(self):
        pass

    def choose_card(self, game_state: GameState, battle_state: BattleState) -> Action:
        raise NotImplementedError("The \"choose_card\" method is not implemented for {}.".format(self.__class__.__name__))
    
    def choose_agent_target(self, battle_state: BattleState, list_name: str, agent_list: list[Agent]) -> Agent:
        raise NotImplementedError("The \"choose_agent_target\" method is not implemented for {}.".format(self.__class__.__name__))
    
    def choose_card_target(self, battle_state: BattleState, list_name: str, card_list: list[Card]) -> Card:
        raise NotImplementedError("The \"choose_card_target\" method is not implemented for {}.".format(self.__class__.__name__))