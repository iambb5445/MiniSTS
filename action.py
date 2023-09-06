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
    def __init__(self, *values: Value) -> None:
        self.values = values

    def play(self, by: Agent, game_state: GameState, battle_state: BattleState) -> None:
        raise NotImplementedError("The \"play\" method is not implemented for action {}.".format(self.__class__.__name__))

    def __repr__(self) -> str:
        return self.__class__.__name__ + "({})".format('-'.join([value.__repr__() for value in self.values]))

class TargetedAction(Action):
    def __init__(self, targeted: Targeted, target: AgentTarget):
        super().__init__(*targeted.values)
        self.targeted = targeted
        self.target = target
    
    def play(self, by: Agent, game_state: GameState, battle_state: BattleState) -> None:
        self.targeted.play(by, game_state, battle_state, self.target.get(by, battle_state))
    
    def __repr__(self) -> str:
        return self.targeted.__repr__() + " to " + self.target.__repr__()

class Targeted:
    def __init__(self, *values: Value) -> None:
        self.values = values

    def To(self, target: AgentTarget):
        return TargetedAction(self, target)

    def And(self, other: Targeted) -> Targeted:
        return AndTargeted(self, other)

    def play(self, by: Agent, game_state: GameState, battle_state: BattleState, target: Agent) -> None:
        raise NotImplementedError("The \"play\" method is not implemented for this Targeted.")
    
    def __repr__(self) -> str:
        return self.__class__.__name__ + "({})".format('-'.join([value.__repr__() for value in self.values]))

class AndTargeted(Targeted):
    def __init__(self, *targeted_set: Targeted):
        super().__init__(*[value for targeted in targeted_set for value in targeted.values])
        self.targeted_set = targeted_set
    
    def play(self, by: Agent, game_state: GameState, battle_state: BattleState, target: Agent):
        for targeted in self.targeted_set:
            targeted.play(by, game_state, battle_state, target)
    
    def __repr__(self) -> str:
        return ' and '.join(*[targeted.__repr__() for targeted in self.targeted_set])

class DealDamage(Targeted):
    def __init__(self, val: Value):
        super().__init__(val)
        self.val = val
    
    def play(self, by: Agent, game_state: GameState, battle_state: BattleState, target: Agent) -> None:
        target.get_damaged(self.val.get())

class AddBlock(Targeted):
    def __init__(self, val: Value):
        super().__init__(val)
        self.val = val
    
    def play(self, by: Agent, game_state: GameState, battle_state: BattleState, target: Agent) -> None:
        target.gain_block(self.val.get())

class ApplyStatus(Targeted):
    def __init__(self, val: Value, status_effect: StatusEffect):
        super().__init__(val)
        self.val = val
        self.status_effect = status_effect
    
    def play(self, by: Agent, game_state: GameState, battle_state: BattleState, target: Agent) -> None:
        target.apply_status(self.status_effect, self.val.get())

    def __repr__(self) -> str:
        return self.__class__.__name__ + "({}-{})".format('-'.join([value.__repr__() for value in self.values]), self.status_effect)

class AddMana(Action):
    def __init__(self, val: Value):
        super().__init__(val)
        self.val = val
    
    def play(self, by: Agent, game_state: GameState, battle_state: BattleState) -> None:
        battle_state.add_to_mana(self.val.get())

class PlayCard(Action):
    def __init__(self, card_index: int):
        super().__init__()
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