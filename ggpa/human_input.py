from __future__ import annotations
from utility import UserInput
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

class HumanInput(GGPA):
    def __init__(self, should_describe_options: bool):
        super().__init__("HumanInput")
        self.should_describe_options = should_describe_options
    
    def choose_card(self, game_state: GameState, battle_state: BattleState) -> EndAgentTurn|PlayCard:
        while True:
            card_list = battle_state.get_hand()
            ask = "Enter card number in {}, or -1 for ending your turn:\n".format(" ".join(["{}:{}".format(i, card_list[i].name) for i in range(len(card_list))]))
            if self.should_describe_options:
                ask += "".join([f"{i}: {repr(card)}\n" for i, card in enumerate(card_list)])
            card_index = UserInput.ask_for_number(ask, lambda val: val >= -1 and val < len(card_list))
            if card_index < 0:
                return EndAgentTurn()
            elif battle_state.hand[card_index].is_playable(game_state, battle_state):
                return PlayCard(card_index)
            else:
                print("Card is not playable.")
    
    def choose_agent_target(self, battle_state: BattleState, list_name: str, agent_list: list[Agent]) -> Agent:
        ask = "Enter index among {} indices in {}:\n".format(list_name, " ".join(["{}:{}".format(i, agent_list[i].name) for i in range(len(agent_list))]))
        if self.should_describe_options:
            ask += "".join([f"{i}: {agent}\n" for i, agent in enumerate(agent_list)])
        index = UserInput.ask_for_number(ask, lambda val: val >= 0 and val < len(agent_list))
        return agent_list[index]
    
    def choose_card_target(self, battle_state: BattleState, list_name: str, card_list: list[Card]) -> Card:
        ask = "Enter index among {} indices in {}:\n".format(list_name, " ".join(["{}:{}".format(i, card_list[i].get_name()) for i in range(len(card_list))]))
        if self.should_describe_options:
            ask += "".join([f"{i}: {card}\n" for i, card in enumerate(card_list)])
        index = UserInput.ask_for_number(ask, lambda val: val >= 0 and val < len(card_list))
        return card_list[index]