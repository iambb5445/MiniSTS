from __future__ import annotations
from value import Value
from target import AgentTarget
from config import StatusEffect
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from battle import BattleState
    from game import GameState
    from agent import Agent

class Action:
    def play(self, by: Agent, game_state: GameState, battle_state: BattleState) -> None:
        raise NotImplementedError("The \"play\" method is not implemented for action {}.".format(self.__class__.__name__))
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
    def __init__(self, targeted: Targeted, target: AgentTarget):
        self.targeted = targeted
        self.target = target
    
    def play(self, by: Agent, game_state: GameState, battle_state: BattleState) -> None:
        self.targeted.play(by, game_state, battle_state, self.target.get(by, battle_state))
    
    def __repr__(self) -> str:
        return self.targeted.__repr__() + " to " + self.target.__repr__()

class Targeted:
    def To(self, target: AgentTarget):
        return TargetedAction(self, target)

    def And(self, other: Targeted) -> Targeted:
        return AndTargeted(self, other)

    def play(self, by: Agent, game_state: GameState, battle_state: BattleState, target: Agent) -> None:
        raise NotImplementedError("The \"play\" method is not implemented for this Targeted.")

class AndTargeted(Targeted):
    def __init__(self, *targeted_set: Targeted):
        self.targeted_set = [targeted for targeted in targeted_set]
    
    def play(self, by: Agent, game_state: GameState, battle_state: BattleState, target: Agent):
        for targeted in self.targeted_set:
            targeted.play(by, game_state, battle_state, target)
    
    def __repr__(self) -> str:
        return ' and '.join(*[targeted.__repr__() for targeted in self.targeted_set])

class DealDamage(Targeted):
    def __init__(self, val: Value):
        self.val = val
    
    def play(self, by: Agent, game_state: GameState, battle_state: BattleState, target: Agent) -> None:
        target.get_damaged(self.val.get())

class AddBlock(Targeted):
    def __init__(self, val: Value):
        self.val = val
    
    def play(self, by: Agent, game_state: GameState, battle_state: BattleState, target: Agent) -> None:
        target.gain_block(self.val.get())

class ApplyStatus(Targeted):
    def __init__(self, val: Value, status_effect: StatusEffect):
        self.val = val
        self.status_effect = status_effect
    
    def play(self, by: Agent, game_state: GameState, battle_state: BattleState, target: Agent) -> None:
        target.apply_status(self.status_effect, self.val.get())

class AddMana(Action):
    def __init__(self, val: Value):
        self.val = val
    
    def play(self, by: Agent, game_state: GameState, battle_state: BattleState) -> None:
        battle_state.add_to_mana(self.val.get())

class PlayCard(Action):
    def __init__(self, card_index: int):
        self.card_index = card_index
    
    def get_card_index(self):
        return self.card_index

    def play(self, by: Agent, game_state: GameState, battle_state: BattleState) -> None:
        assert self.card_index < len(battle_state.hand) and self.card_index >= 0, "Card index {} out of range for hand {}".format(self.card_index, battle_state.hand)
        print('Playing {}'.format(battle_state.hand[self.card_index].name))
        assert battle_state.is_playable(battle_state.hand[self.card_index])
        battle_state.hand[self.card_index].play(game_state, battle_state)
        battle_state.discard(self.card_index)


class NoAction(Action):
    def play(self, by: Agent, game_state: GameState, battle_state: BattleState) -> None:
        pass