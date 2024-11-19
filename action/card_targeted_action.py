from __future__ import annotations
from value import Value
from action.action import Action
import copy
from target.card_target import CardTarget, CardPile
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from battle import BattleState
    from game import GameState
    from card import Card
    from agent import Agent

class CardTargetedAction(Action):
    def __init__(self, targeted: CardTargetedL1, target: CardTarget, by: Card):
        super().__init__(*targeted.values)
        self.targeted = targeted
        self.target = target
        self.by = by
    
    def play(self, by: Agent, game_state: GameState, battle_state: BattleState) -> None:
        try:
            target_card = self.target.get(self.by, battle_state)
        except CardTarget.NoneAvailabeException:
            return
        self.targeted.play_many(by, game_state, battle_state, target_card)
    
    def __repr__(self) -> str:
        return self.targeted.__repr__()# + " by " + self.by.name

class CardTargetedL1:
    def __init__(self, card_targeted: CardTargetedL2, target: CardTarget, *values: Value) -> None:
        self.values = values
        self.card_targetd = card_targeted
        self.target = target

    def By(self, by: Card) -> CardTargetedAction:
        return CardTargetedAction(self, self.target, by)
    
    def play_many(self, by: Agent, game_state: GameState, battle_state: BattleState, targets: list[Card]) -> None:
        self.card_targetd.play_many(by, game_state, battle_state, targets)
    
    def __repr__(self) -> str:
        return self.card_targetd.__repr__() + " to " + self.target.__repr__()

class CardTargetedL2:
    def __init__(self, *values: Value) -> None:
        self.values = values

    def To(self, target: CardTarget) -> CardTargetedL1:
        return CardTargetedL1(self, target, *self.values)

    def And(self, other: CardTargetedL2) -> CardTargetedL2:
        return AndCardTargeted(self, other)
    
    def play_many(self, by: Agent, game_state: GameState, battle_state: BattleState, targets: list[Card]) -> None:
        for target in targets:
            self.play(by, game_state, battle_state, target)

    def play(self, by: Agent, game_state: GameState, battle_state: BattleState, target: Card) -> None:
        raise NotImplementedError("The \"play\" method is not implemented for {}.".format(self.__class__.__name__))
    
    def __repr__(self) -> str:
        return self.__class__.__name__ + "({})".format('-'.join([value.__repr__() for value in self.values]))

class AndCardTargeted(CardTargetedL2):
    def __init__(self, *targeted_set: CardTargetedL2):
        super().__init__(*[value for targeted in targeted_set for value in targeted.values])
        self.targeted_set = targeted_set
    
    def play(self, by: Agent, game_state: GameState, battle_state: BattleState, target: Card):
        for targeted in self.targeted_set:
            targeted.play(by, game_state, battle_state, target)
    
    def __repr__(self) -> str:
        return ' and '.join(*[targeted.__repr__() for targeted in self.targeted_set])

class Exhaust(CardTargetedL2):
    def __init__(self):
        super().__init__()
    
    def play(self, by: Agent, game_state: GameState, battle_state: BattleState, target: Card) -> None:
        battle_state.exhaust(target)

class AddCopy(CardTargetedL2):
    def __init__(self, card_pile: CardPile):
        super().__init__()
        self.card_pile = card_pile
    
    def play(self, by: Agent, game_state: GameState, battle_state: BattleState, target: Card) -> None:
        if self.card_pile == CardPile.DISCARD:
            battle_state.discard_pile.append(copy.deepcopy(target))
        elif self.card_pile == CardPile.DRAW:
            battle_state.draw_pile.append(copy.deepcopy(target))
        elif self.card_pile == CardPile.HAND:
            battle_state.hand.append(copy.deepcopy(target))
        elif self.card_pile == CardPile.EXHAUST:
            battle_state.exhaust_pile.append(copy.deepcopy(target))
        else:
            raise Exception("Unrecognized CardPile to add a copy to")

class UpgradeCard(CardTargetedL2):
    def __init__(self):
        super().__init__()

    def play(self, by: Agent, game_state: GameState, battle_state: BattleState, target: Card) -> None:
        target.upgrade()

class DiscardCard(CardTargetedL2):
    def __init__(self):
        super().__init__()

    def play(self, by: Agent, game_state: GameState, battle_state: BattleState, target: Card) -> None:
        pass
        # battle_state.discard(target)