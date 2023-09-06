from __future__ import annotations
from value import Value
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