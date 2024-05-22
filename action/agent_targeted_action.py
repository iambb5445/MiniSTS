from __future__ import annotations
from value import Value, ConstValue
from status_effecs import StatusEffectDefinition, strength_apply, vigor_apply, vulnerable_apply, weak_apply, vigor_after
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
    def __init__(self, val: Value, times: Value = ConstValue(1)):
        super().__init__(val)
        self.val = val
        self.times = times
    
    def play(self, by: Agent, game_state: GameState, battle_state: BattleState, target: Agent) -> None:
        self.event.broadcast_before((by, game_state, battle_state, target))
        amount = self.val.get()
        amount = self.event.broadcast_apply(amount, (by, game_state, battle_state, target))
        times = self.times.get()
        for _ in range(times):
            target.get_damaged(round(amount))
        self.event.broadcast_after((by, game_state, battle_state, target))
    
    def __repr__(self) -> str:
        if self.times.peek() != 1:
            return f"Deal {self.val.peek()} attack damage {self.times.peek()} times"
        else:
            return f"Deal {self.val.peek()} attack damage"
        

class DealDamage(AgentTargeted):
    def __init__(self, val: Value, times: Value = ConstValue(1)):
        super().__init__(val)
        self.val = val
        self.times = times
    
    def play(self, by: Agent, game_state: GameState, battle_state: BattleState, target: Agent) -> None:
        amount = self.val.get()
        times = self.times.get()
        for _ in range(times):
            target.get_damaged(round(amount))
    
    def __repr__(self) -> str:
        if self.times.peek() != 1:
            return f"Deal {self.val.peek()} damage {self.times.peek()} times"
        else:
            return f"Deal {self.val.peek()} damage"
        

class Heal(AgentTargeted):
    def __init__(self, val: Value):
        super().__init__(val)
        self.val = val
    
    def play(self, by: Agent, game_state: GameState, battle_state: BattleState, target: Agent) -> None:
        target.get_healed(self.val.get())
    
    def __repr__(self) -> str:
        return f"Apply {self.val.peek()} heal"

class AddBlock(AgentTargeted):
    def __init__(self, val: Value):
        super().__init__(val)
        self.val = val
    
    def play(self, by: Agent, game_state: GameState, battle_state: BattleState, target: Agent) -> None:
        target.gain_block(self.val.get())
    
    def __repr__(self) -> str:
        return f"Add {self.val.peek()} block"

class ApplyStatus(AgentTargeted):
    def __init__(self, val: Value, status_effect: StatusEffectDefinition):
        super().__init__(val)
        self.val = val
        self.status_effect = status_effect
    
    def play(self, by: Agent, game_state: GameState, battle_state: BattleState, target: Agent) -> None:
        target.status_effect_state.apply_status(self.status_effect, self.val.get())

    def __repr__(self) -> str:
        return f"Apply {self.val.peek()} {str(self.status_effect)}"
        # return self.__class__.__name__ + "({}-{})".format('-'.join([value.__repr__() for value in self.values]), self.status_effect)

# TODO order
DealAttackDamage.event.subscribe_values(strength_apply)
DealAttackDamage.event.subscribe_values(vigor_apply)
DealAttackDamage.event.subscribe_after(vigor_after)
DealAttackDamage.event.subscribe_values(vulnerable_apply)
DealAttackDamage.event.subscribe_values(weak_apply)