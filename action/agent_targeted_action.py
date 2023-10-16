from __future__ import annotations
from value import Value
from config import StatusEffect
from utility import Event
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

class DealAttackDamage(AgentTargeted):
    event: Event[int, tuple[Agent, GameState, BattleState, Agent]] = Event()
    def __init__(self, val: Value):
        super().__init__(val)
        self.val = val
    
    def play(self, by: Agent, game_state: GameState, battle_state: BattleState, target: Agent) -> None:
        self.event.broadcast_before((by, game_state, battle_state, target))
        amount = self.val.get()
        amount = self.event.broadcast_apply(amount, (by, game_state, battle_state, target))
        target.get_damaged(round(amount))
        self.event.broadcast_after((by, game_state, battle_state, target))

def strength_apply(amount: int, additional_info: tuple[Agent, GameState, BattleState, Agent]):
    by, _, _, _ = additional_info
    amount += by.status_effects.get(StatusEffect.STRENGTH, 0)
    return amount

def vulnerable_apply(amount: int, additional_info: tuple[Agent, GameState, BattleState, Agent]):
    _, _, _, target = additional_info
    if target.status_effects.get(StatusEffect.VULNERABLE, 0) > 0:
        amount = int(amount * 1.5)
    return amount

def weak_apply(amount: int, additional_info: tuple[Agent, GameState, BattleState, Agent]):
    by, _, _, _ = additional_info
    if by.status_effects.get(StatusEffect.WEAK, 0) > 0:
        amount = int(amount * 0.75)
    return amount

# TODO apply
DealAttackDamage.event.subscribe_values(strength_apply)
DealAttackDamage.event.subscribe_values(vulnerable_apply)
DealAttackDamage.event.subscribe_values(weak_apply)

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
