from enum import StrEnum
from config import MAX_STATUS
from typing import Callable

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