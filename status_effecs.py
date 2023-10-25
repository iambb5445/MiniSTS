from __future__ import annotations
from enum import StrEnum
from config import MAX_STATUS
from typing import Callable
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from battle import BattleState
    from game import GameState
    from agent import Agent

class StatusEffect(StrEnum):
    VULNERABLE = "Vulnerable"
    WEAK = "Weak"
    ENTANGLE = "Entangle"
    STRENGTH = "Strength"
    VIGOR = "Vigor"

def add_stack(val1: int, val2: int) -> int:
    if val1 + val2 < MAX_STATUS:
        return val1 + val2
    else:
        return MAX_STATUS
def no_stack(val1: int, val2: int) -> int:
    return val1
STACK_BEHAVIOR: dict[StatusEffect, Callable[[int, int], int]] = {
    StatusEffect.VULNERABLE: add_stack,
    StatusEffect.WEAK: add_stack,
    StatusEffect.ENTANGLE: no_stack,
    StatusEffect.STRENGTH: add_stack,
    StatusEffect.VIGOR: add_stack,
}
def decrease(val: int) -> int:
    return (val-1) if val > 0 else 0
def remove(val: int) -> int:
    return 0
def no_change(val: int) -> int:
    return val
END_TURN_BEHAVIOR: dict[StatusEffect, Callable[[int], int]] = {
    StatusEffect.VULNERABLE: decrease,
    StatusEffect.WEAK: decrease,
    StatusEffect.ENTANGLE: remove,
    StatusEffect.STRENGTH: no_change,
    StatusEffect.VIGOR: no_change
}

def strength_apply(amount: int, additional_info: tuple[Agent, GameState, BattleState, Agent]):
    by, _, _, _ = additional_info
    amount += by.status_effects.get(StatusEffect.STRENGTH, 0)
    return amount

def vigor_apply(amount: int, additional_info: tuple[Agent, GameState, BattleState, Agent]):
    by, _, _, _ = additional_info
    amount += by.status_effects.get(StatusEffect.VIGOR, 0)
    # TODO this should be applied for multiple damages on the same card
    by.remove_status(StatusEffect.VIGOR)
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