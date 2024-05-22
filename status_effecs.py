from __future__ import annotations
from enum import StrEnum, Enum
from config import MAX_STATUS
from typing import Callable
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from battle import BattleState
    from game import GameState
    from agent import Agent

class StatusEffectDefinition:
    def __init__(self, name,
                 stack: Callable[[list[StatusEffectObject]], list[bool]],
                 end_turn: Callable[[StatusEffectObject], None],
                 done: Callable[[StatusEffectObject], bool],
                 repr: Callable[[StatusEffectObject], str]|None):
        self.name = name
        self.stack = stack
        self.end_turn = end_turn
        self.done = done
        if repr is not None:
            self.is_hidden = False
            self.repr = repr
        else:
            self.is_hidden = True
            self.repr = SEDef._hidden_repr
    
    @staticmethod
    def zero_done(se: StatusEffectObject) -> bool:
        return se.val == 0

    @staticmethod
    def never_done(se: StatusEffectObject) -> bool:
        return False

    @staticmethod
    def always_done(se: StatusEffectObject) -> bool:
        return True

    @staticmethod
    def add_stack(se_list: list[StatusEffectObject]) -> list[bool]:
        keep = [False for _ in se_list]
        total = min(MAX_STATUS, sum([se.val for se in se_list]))
        se_list[0].val = total
        keep[0] = True
        return keep
        
    @staticmethod
    def no_stack(se_list: list[StatusEffectObject]) -> list[bool]:
        keep = [False for _ in se_list]
        keep[0] = True
        return keep
    
    @staticmethod
    def unique_stack(se_list: list[StatusEffectObject]) -> list[bool]:
        return [True for _ in se_list]

    @staticmethod
    def decrease(se: StatusEffectObject, amount: int = 1):
        se.val -= amount
    
    @staticmethod
    def increase(se: StatusEffectObject, amount: int = 1):
        se.val += amount
    
    @staticmethod
    def get_decrease(amount: int = 1) -> Callable[[StatusEffectObject], None]:
        return lambda x: StatusEffectDefinition.decrease(x, amount)
    
    @staticmethod
    def get_increase(amount: int = 1):
        return lambda x: StatusEffectDefinition.increase(x, amount)
    
    @staticmethod
    def remove(se: StatusEffectObject):
        se.done = lambda: True
    
    @staticmethod
    def no_change(se: StatusEffectObject):
        return
    
    @staticmethod
    def key_value_repr(se: StatusEffectObject):
        return f"<{se.definition.name}>: {se.val}"
    
    @staticmethod
    def _hidden_repr(se: StatusEffectObject):
        raise Exception(f"Hidden status effect {se.definition.name} does not have a representation.")
    
    def __repr__(self):
        return self.name
SEDef = StatusEffectDefinition

class StatusEffectRepo:
    VULNERABLE = SEDef("Vulnerable", SEDef.add_stack, SEDef.get_decrease(1), SEDef.zero_done, SEDef.key_value_repr)
    WEAK = SEDef("Weak", SEDef.add_stack, SEDef.get_decrease(1), SEDef.zero_done, SEDef.key_value_repr)
    STRENGTH = SEDef("Strength", SEDef.add_stack, SEDef.no_change, SEDef.zero_done, SEDef.key_value_repr)
    VIGOR = SEDef("Vigor", SEDef.add_stack, SEDef.no_change, SEDef.zero_done, SEDef.key_value_repr)
    TOLERANCE = SEDef("Tolerance", SEDef.no_stack, SEDef.get_increase(2), SEDef.zero_done, SEDef.key_value_repr)
    BOMB = SEDef("Bomb", SEDef.unique_stack, SEDef.get_decrease(1), SEDef.zero_done, SEDef.key_value_repr)

class StatusEffectObject:
    def __init__(self, definition: StatusEffectDefinition, val: int):
        self.val = val
        self.definition = definition
    
    def done(self):
        return self.definition.done(self)
    
    def __repr__(self) -> str:
        return self.definition.repr(self)

class StatusEffectState:
    def __init__(self):
        self.status_effects: list[StatusEffectObject] = []
    
    def get(self, status: StatusEffectDefinition) -> int:
        values = self._get_obj(status)
        if len(values) > 1:
            raise Exception(f"Cannot return a single value for {status}")
        elif len(values) == 0:
            return 0
        return values[0].val

    def has(self, status: StatusEffectDefinition) -> bool:
        return len(self._get_obj(status)) > 0

    def _get_obj(self, status: StatusEffectDefinition) -> list[StatusEffectObject]:
        ret: list[StatusEffectObject] = []
        for se_obj in self.status_effects:
            if se_obj.definition.name == status.name:
                ret.append(se_obj)
        return ret
    
    def end_turn(self):
        for se in self.status_effects:
            se.definition.end_turn(se)
        self.clean()
        
    def remove_status(self, sed: StatusEffectDefinition):
        find = self._get_obj(sed)
        for se in find:
            se.done = lambda: True
        self.clean()
    
    def apply_status(self, definition: StatusEffectDefinition, amount: int):
        self.status_effects.append(StatusEffectObject(definition, amount))
        find = self._get_obj(definition)
        keep = definition.stack(find)
        for se, should_keep in zip(find, keep):
            if not should_keep:
                se.done = lambda: True
        self.clean()

    def clean_up(self):
        self.status_effects = []

    def clean(self):
        self.status_effects = [se for se in self.status_effects if not se.done()]

    def __repr__(self) -> str:
        return f'[{",".join([repr(se) for se in self.status_effects if not se.definition.is_hidden])}]'

def tolerance_after(__: None, additional_info: tuple[Agent, GameState, BattleState, list[Agent]]):
    by, _, _, _ = additional_info
    by.block += by.status_effect_state.get(StatusEffectRepo.TOLERANCE)

def bomb_after(__: None, additional_info: tuple[Agent, GameState, BattleState, list[Agent]]):
    by, _, _, other_side = additional_info
    bomb = [se for se in by.status_effect_state._get_obj(StatusEffectRepo.BOMB) if se.val == 1]
    for _ in bomb:
        for agent in other_side:
            agent.get_damaged(40)

def strength_apply(amount: int, additional_info: tuple[Agent, GameState, BattleState, Agent]):
    by, _, _, _ = additional_info
    amount += by.status_effect_state.get(StatusEffectRepo.STRENGTH)
    return amount

def vigor_apply(amount: int, additional_info: tuple[Agent, GameState, BattleState, Agent]):
    by, _, _, _ = additional_info
    amount += by.status_effect_state.get(StatusEffectRepo.VIGOR)
    return amount

def vigor_after(_, additional_info: tuple[Agent, GameState, BattleState, Agent]):
    by, _, _, _ = additional_info
    # TODO this should be applied for multiple damages on the same card
    by.status_effect_state.remove_status(StatusEffectRepo.VIGOR)

def vulnerable_apply(amount: int, additional_info: tuple[Agent, GameState, BattleState, Agent]):
    _, _, _, target = additional_info
    if target.status_effect_state.get(StatusEffectRepo.VULNERABLE) > 0:
        amount = int(amount * 1.5)
    return amount

def weak_apply(amount: int, additional_info: tuple[Agent, GameState, BattleState, Agent]):
    by, _, _, _ = additional_info
    if by.status_effect_state.get(StatusEffectRepo.WEAK) > 0:
        amount = int(amount * 0.75)
    return amount