from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from card import Card
    from agent import Agent
    from battle import BattleState

from enum import Enum

class AgentSet(Enum):
        ENEMY = 1
        ALL = 2

def get_agent_set_data(agent_set: AgentSet, battle_state: BattleState) -> tuple[str, list[Agent]]:
    if agent_set == AgentSet.ENEMY:
        agent_list: list[Agent] = [enemy for enemy in battle_state.enemies]
        return "enemies", agent_list
    elif agent_set == AgentSet.ALL:
        agent_list: list[Agent] = [battle_state.player]
        agent_list += [enemy for enemy in battle_state.enemies]
        return "all agents", agent_list
    else:
        raise Exception("AgentSet {} not recognized.".format(AgentSet))

class AgentTarget:
    def get(self, performer: Agent, battle_state: BattleState) -> list[Agent]:
        raise NotImplementedError("The \"get\" method is not implemented for this AgentTarget.")

    def __repr__(self) -> str:
        return self.__class__.__name__

class SelfAgentTarget(AgentTarget):
    def get(self, performer: Agent, battle_state: BattleState) -> list[Agent]:
        return [performer]

class PlayerAgentTarget(AgentTarget):
    def get(self, performer: Agent, battle_state: BattleState) -> list[Agent]:
        return [battle_state.player]

class ChooseAgentTarget(AgentTarget):
    def __init__(self, among: AgentSet, count: int = 1):
        self.among = among
        self.count = count
    
    def get(self, performer: Agent, battle_state: BattleState) -> list[Agent]:
        name, agent_list = get_agent_set_data(self.among, battle_state)
        agent = battle_state.player.bot.choose_agent_target(battle_state, name, agent_list)
        return [agent]
        
class AllAgentsTarget(AgentTarget):
    def __init__(self, among: AgentSet):
        self.among = among
    
    def get(self, performer: Agent, battle_state: BattleState) -> list[Agent]:
        _, agent_list = get_agent_set_data(self.among, battle_state)
        return agent_list

'''
class RandomAgentTarget(AgentTarget):
    def __init__(self, among: AgentSet, count: int = 1):
        self.among = among
        self.count = count
'''
        
class CardPile(Enum):
    HAND = 1
    DISCARD = 2
    DRAW = 3
    EXHAUST = 4

def get_card_pile_data(card_pile: CardPile, battle_state: BattleState) -> tuple[str, list[Card]]:
    if card_pile == CardPile.HAND:
        card_list: list[Card] = [card for card in battle_state.hand]
        return "hand", card_list
    elif card_pile == CardPile.DISCARD:
        card_list: list[Card] = [card for card in battle_state.discard_pile]
        return "discard", card_list
    elif card_pile == CardPile.DRAW:
        card_list: list[Card] = [card for card in battle_state.draw_pile]
        return "draw", card_list
    elif card_pile == CardPile.EXHAUST:
        card_list: list[Card] = [card for card in battle_state.exhause_pile]
        return "exhaust", card_list
    else:
        raise Exception("AgentSet {} not recognized.".format(AgentSet))

class CardTarget:
    def get(self, by: Card, battle_state: BattleState) -> list[Card]:
        raise NotImplementedError("The \"get\" method is not implemented for this CreateTarget.")

    def __repr__(self) -> str:
        return self.__class__.__name__
    
class SelfCardTarget(CardTarget):
    def get(self, by: Card, battle_state: BattleState) -> list[Card]:
        return [by]

class ChooseCardTarget(CardTarget):
    def __init__(self, among: CardPile, count: int = 1):
        self.among = among
        self.count = count
    
    def get(self, by: Card, battle_state: BattleState) -> list[Card]:
        name, card_list = get_card_pile_data(self.among, battle_state)
        card = battle_state.player.bot.choose_card_target(battle_state, name, card_list)
        return [card]
    
'''
class SelfCardTarget(CardTarget):
    pass

class AllCardsTarget(CardTarget):
    def __init__(self, among: CardPile):
        self.among = among
'''