from __future__ import annotations
from value import Value
from target import CreatureTarget
from config import StatusEffect

class Action:
    def play(self) -> None: # TODO figure out the inputs
        raise NotImplementedError("The \"play\" method is not implemented for this Action.")

'''
    def And(self, other: Action) -> Action:
        return AndAction(self, other)
    
class AndAction(Action):
    def __init__(self, *actions: Action):
        self.actions = [action for action in actions]
    
    def play(self):
        for action in self.actions:
            action.play()
'''
class TargetedAction(Action):
    def __init__(self, targeted: Targeted, target: CreatureTarget):
        self.targeted = targeted
        self.target = target
    
    def play(self) -> None:
        self.targeted.play(self.target)
    
    def __repr__(self) -> str:
        return self.targeted.__repr__() + " to " + self.target.__repr__()

class Targeted:
    def To(self, target: CreatureTarget):
        return TargetedAction(self, target)

    def And(self, other: Targeted) -> Targeted:
        return AndTargeted(self, other)

    def play(self, target: CreatureTarget) -> None:
        raise NotImplementedError("The \"play\" method is not implemented for this Targeted.")

class AndTargeted(Targeted):
    def __init__(self, *targeted_set: Targeted):
        self.targeted_set = [targeted for targeted in targeted_set]
    
    def play(self, target: CreatureTarget):
        target.get() # TODO
        for targeted in self.targeted_set:
            targeted.play(target)
    
    def __repr__(self) -> str:
        return ' and '.join(*[targeted.__repr__() for targeted in self.targeted_set])

class DealDamage(Targeted):
    def __init__(self, val: Value):
        self.val = val

class GainBlock(Action):
    def __init__(self, val: Value):
        self.val = val

class ApplyStatus(Targeted):
    def __init__(self, val: Value, status_effect: StatusEffect):
        self.val = val
        self.status_effect = status_effect

class PlayCard(Action):
    def __init__(self, card_index: int):
        self.card_index = card_index
    
    def get_card_index(self):
        return self.card_index

    # TODO
    #def play(battle_state: BattleState) -> None:
    #    battle_state.discard(self.card_index)