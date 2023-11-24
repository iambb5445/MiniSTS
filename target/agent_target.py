from __future__ import annotations
import random
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from agent import Agent
    from battle import BattleState
from enum import Enum

class AgentSet(Enum):
        ENEMY = 1
        ALL = 2

def get_agent_set_name(agent_set: AgentSet):
    if agent_set == AgentSet.ENEMY:
        return "enemies"
    elif agent_set == AgentSet.ALL:
        return "living"
    else:
        raise Exception("AgentSet {} not recognized.".format(agent_set))

def get_agent_set_data(agent_set: AgentSet, battle_state: BattleState) -> list[Agent]:
    if agent_set == AgentSet.ENEMY:
        agent_list: list[Agent] = [enemy for enemy in battle_state.enemies]
        return agent_list
    elif agent_set == AgentSet.ALL:
        agent_list: list[Agent] = [battle_state.player]
        agent_list += [enemy for enemy in battle_state.enemies]
        return agent_list
    else:
        raise Exception("AgentSet {} not recognized.".format(agent_set))

class AgentTarget:
    def get(self, performer: Agent, battle_state: BattleState) -> list[Agent]:
        raise NotImplementedError("The \"get\" method is not implemented for this AgentTarget.")

    def __repr__(self) -> str:
        return self.__class__.__name__

class SelfAgentTarget(AgentTarget):
    def get(self, performer: Agent, battle_state: BattleState) -> list[Agent]:
        return [performer]
    
    def __repr__(self) -> str:
        return "self"

class PlayerAgentTarget(AgentTarget):
    def get(self, performer: Agent, battle_state: BattleState) -> list[Agent]:
        return [battle_state.player]
    
    def __repr__(self) -> str:
        return "player"

class ChooseAgentTarget(AgentTarget):
    def __init__(self, among: AgentSet, count: int = 1):
        self.among = among
        self.count = count
    
    def get(self, performer: Agent, battle_state: BattleState) -> list[Agent]:
        agent_list: list[Agent] = get_agent_set_data(self.among, battle_state)
        name: str = get_agent_set_name(self.among)
        agent = battle_state.get_player_agent_target(name, agent_list)
        return [agent]
    
    def __repr__(self) -> str:
        return f"your choice between {get_agent_set_name(self.among)}"
        
class AllAgentsTarget(AgentTarget):
    def __init__(self, among: AgentSet):
        self.among = among
    
    def get(self, performer: Agent, battle_state: BattleState) -> list[Agent]:
        agent_list = get_agent_set_data(self.among, battle_state)
        return agent_list
    
    def __repr__(self) -> str:
        return f"all {get_agent_set_name(self.among)}"

class RandomAgentTarget(AgentTarget):
    def __init__(self, among: AgentSet):
        self.among = among
    
    def get(self, performer: Agent, battle_state: BattleState) -> list[Agent]:
        agent_list: list[Agent] = get_agent_set_data(self.among, battle_state)
        agent = random.choice(agent_list)
        return [agent]
    
    def __repr__(self) -> str:
        return f"random target between {get_agent_set_name(self.among)}"