from __future__ import annotations
from value import Value
from config import StatusEffect
from typing import TYPE_CHECKING
from action.action import Action
if TYPE_CHECKING:
    from battle import BattleState
    from game import GameState
    from agent import Agent
    from target.agent_target import AgentTarget

class AgentTargetedAction(Action):
    def __init__(self, targeted: AgentTargeted, target: AgentTarget):
        super().__init__(*targeted.values)
        self.targeted = targeted
        self.target = target
    
    def play(self, by: Agent, game_state: GameState, battle_state: BattleState) -> None:
        self.targeted.play_many(by, game_state, battle_state, self.target.get(by, battle_state))
    
    def __repr__(self) -> str:
        return self.targeted.__repr__() + " to " + self.target.__repr__()

class AgentTargeted:
    def __init__(self, *values: Value) -> None:
        self.values = values

    def To(self, target: AgentTarget):
        return AgentTargetedAction(self, target)

    def And(self, other: AgentTargeted) -> AgentTargeted:
        return AndAgentTargeted(self, other)
    
    def play_many(self, by: Agent, game_state: GameState, battle_state: BattleState, targets: list[Agent]) -> None:
        for target in targets:
            self.play(by, game_state, battle_state, target)

    def play(self, by: Agent, game_state: GameState, battle_state: BattleState, target: Agent) -> None:
        raise NotImplementedError("The \"play\" method is not implemented for {}.".format(self.__class__.__name__))
    
    def __repr__(self) -> str:
        return self.__class__.__name__ + "({})".format('-'.join([value.__repr__() for value in self.values]))

class AndAgentTargeted(AgentTargeted):
    def __init__(self, *targeted_set: AgentTargeted):
        super().__init__(*[value for targeted in targeted_set for value in targeted.values])
        self.targeted_set = targeted_set
    
    def play(self, by: Agent, game_state: GameState, battle_state: BattleState, target: Agent):
        for targeted in self.targeted_set:
            targeted.play(by, game_state, battle_state, target)
    
    def __repr__(self) -> str:
        return ' and '.join([targeted.__repr__() for targeted in self.targeted_set])

class DealDamage(AgentTargeted):
    def __init__(self, val: Value):
        super().__init__(val)
        self.val = val
    
    def play(self, by: Agent, game_state: GameState, battle_state: BattleState, target: Agent) -> None:
        target.get_damaged(self.val.get())

class AddBlock(AgentTargeted):
    def __init__(self, val: Value):
        super().__init__(val)
        self.val = val
    
    def play(self, by: Agent, game_state: GameState, battle_state: BattleState, target: Agent) -> None:
        target.gain_block(self.val.get())

class ApplyStatus(AgentTargeted):
    def __init__(self, val: Value, status_effect: StatusEffect):
        super().__init__(val)
        self.val = val
        self.status_effect = status_effect
    
    def play(self, by: Agent, game_state: GameState, battle_state: BattleState, target: Agent) -> None:
        target.apply_status(self.status_effect, self.val.get())

    def __repr__(self) -> str:
        return self.__class__.__name__ + "({}-{})".format('-'.join([value.__repr__() for value in self.values]), self.status_effect)
