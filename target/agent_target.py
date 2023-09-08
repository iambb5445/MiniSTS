from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
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
        raise Exception("AgentSet {} not recognized.".format(agent_set))

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