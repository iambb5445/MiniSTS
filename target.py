from __future__ import annotations
from utility import UserInput
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
    def get(self, performer: Agent, battle_state: BattleState) -> Agent:
        raise NotImplementedError("The \"get\" method is not implemented for this AgentTarget.")

    def __repr__(self) -> str:
        return self.__class__.__name__

class SelfAgentTarget(AgentTarget):
    def get(self, performer: Agent, battle_state: BattleState) -> Agent:
        return performer

class PlayerAgentTarget(AgentTarget):
    def get(self, performer: Agent, battle_state: BattleState) -> Agent:
        return battle_state.player

class ChooseAgentTarget(AgentTarget):
    def __init__(self, among: AgentSet, count: int = 1):
        self.among = among
        self.count = count
    
    def get(self, performer: Agent, battle_state: BattleState) -> Agent:
        name, agent_list = get_agent_set_data(self.among, battle_state)
        index = UserInput.ask_for_number(
            "enter index among {} indices in (0-{}]: ".format(name, len(agent_list)),
            lambda val: val >= 0 or val < len(agent_list)
        )
        return agent_list[index]
        
'''
class RandomAgentTarget(AgentTarget):
    def __init__(self, among: AgentSet, count: int = 1):
        self.among = among
        self.count = count

class AllAgentsTarget(AgentTarget):
    def __init__(self, among: AgentSet):
        self.among = among
'''
        
class CardPile(Enum):
    HAND = 1
    DISCARD = 2

class CardTarget:
    def get(self, battle_state: BattleState) -> Card:
        raise NotImplementedError("The \"get\" method is not implemented for this CreateTarget.")
'''
class SelfCardTarget(CardTarget):
    pass

class ChooseCardTarget(CardTarget):
    def __init__(self, among: CardPile, count: int = 1):
        self.among = among
        self.count = count

class AllCardsTarget(CardTarget):
    def __init__(self, among: CardPile):
        self.among = among
'''