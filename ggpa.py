from __future__ import annotations
import random
from agent import Agent
from battle import BattleState
from card import Card
from game import GameState
from utility import UserInput
from action.action import NoAction, PlayCard, Action
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
    
class HumanInput(GGPA):
    def choose_card(self, game_state: GameState, battle_state: BattleState) -> Action:
        while True:
            card_index = UserInput.ask_for_number(
                "Enter card number, or -1 for ending your turn: ",
                lambda val: val >= -1 and val < len(battle_state.get_hand())
            )
            if card_index < 0:
                battle_state.end_player_turn()
                return NoAction()
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
    
class MCTSBot(GGPA):
    pass