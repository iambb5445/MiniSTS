from __future__ import annotations
from utility import UserInput
from ggpa.ggpa import GGPA
from action.action import EndPlayerTurn, PlayCard
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game import GameState
    from battle import BattleState
    from agent import Agent
    from card import Card
    from agent import Agent
    from card import Card

class HumanInput(GGPA):
    def choose_card(self, game_state: GameState, battle_state: BattleState) -> EndPlayerTurn|PlayCard:
        while True:
            card_index = UserInput.ask_for_number(
                "Enter card number, or -1 for ending your turn: ",
                lambda val: val >= -1 and val < len(battle_state.get_hand())
            )
            if card_index < 0:
                return EndPlayerTurn()
            elif battle_state.is_playable(battle_state.hand[card_index]):
                return PlayCard(card_index)
            else:
                print("Card is not playable.")
    
    def choose_agent_target(self, battle_state: BattleState, list_name: str, agent_list: list[Agent]) -> Agent:
        index = UserInput.ask_for_number(
            "Enter index among {} indices in (0-{}]: ".format(list_name, len(agent_list)),
            lambda val: val >= 0 and val < len(agent_list)
        )
        return agent_list[index]
    
    def choose_card_target(self, battle_state: BattleState, list_name: str, card_list: list[Card]) -> Card:
        index = UserInput.ask_for_number(
            "Enter index among {} indices in (0-{}]: ".format(list_name, len(card_list)),
            lambda val: val >= 0 and val < len(card_list)
        )
        return card_list[index]