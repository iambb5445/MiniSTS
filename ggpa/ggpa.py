from __future__ import annotations
from typing import TYPE_CHECKING
from action.action import EndPlayerTurn, PlayCard
if TYPE_CHECKING:
    from game import GameState
    from battle import BattleState
    from agent import Agent
    from card import Card
    from agent import Agent
    from card import Card

class GGPA:
    def __init__(self):
        pass

    @staticmethod
    def get_play_card_options(game_state: GameState, battle_state: BattleState) -> list[PlayCard]:
        return [PlayCard(i) for i in range(len(battle_state.hand)) if battle_state.is_playable(battle_state.hand[i])]

    def choose_card(self, game_state: GameState, battle_state: BattleState) -> PlayCard|EndPlayerTurn:
        raise NotImplementedError("The \"choose_card\" method is not implemented for {}.".format(self.__class__.__name__))
    
    def choose_agent_target(self, battle_state: BattleState, list_name: str, agent_list: list[Agent]) -> Agent:
        raise NotImplementedError("The \"choose_agent_target\" method is not implemented for {}.".format(self.__class__.__name__))
    
    def choose_card_target(self, battle_state: BattleState, list_name: str, card_list: list[Card]) -> Card:
        raise NotImplementedError("The \"choose_card_target\" method is not implemented for {}.".format(self.__class__.__name__))