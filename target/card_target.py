from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from card import Card
    from battle import BattleState
from enum import Enum

class CardPile(Enum):
    HAND = 1
    DISCARD = 2
    DRAW = 3
    EXHAUST = 4

def get_card_pile_name(card_pile: CardPile) -> str:
    if card_pile == CardPile.HAND:
        return "hand"
    elif card_pile == CardPile.DISCARD:
        return "discard"
    elif card_pile == CardPile.DRAW:
        return "draw"
    elif card_pile == CardPile.EXHAUST:
        return "exhaust"
    else:
        raise Exception("CardPile {} not recognized.".format(card_pile))

def get_card_pile_data(card_pile: CardPile, battle_state: BattleState) -> list[Card]:
    if card_pile == CardPile.HAND:
        card_list: list[Card] = [card for card in battle_state.hand]
        return card_list
    elif card_pile == CardPile.DISCARD:
        card_list: list[Card] = [card for card in battle_state.discard_pile]
        return card_list
    elif card_pile == CardPile.DRAW:
        card_list: list[Card] = [card for card in battle_state.draw_pile]
        return card_list
    elif card_pile == CardPile.EXHAUST:
        card_list: list[Card] = [card for card in battle_state.exhaust_pile]
        return card_list
    else:
        raise Exception("CardPile {} not recognized.".format(card_pile))

class CardTarget:
    class NoneAvailabeException(Exception):
        pass

    def get(self, by: Card, battle_state: BattleState) -> list[Card]:
        raise NotImplementedError("The \"get\" method is not implemented for this CreateTarget.")

    def __repr__(self) -> str:
        return self.__class__.__name__
    
class SelfCardTarget(CardTarget):
    def get(self, by: Card, battle_state: BattleState) -> list[Card]:
        return [by]
    
    def __repr__(self) -> str:
        return "self (this card)"

class ChooseCardTarget(CardTarget):
    def __init__(self, among: CardPile, count: int = 1):
        self.among = among
        self.count = count
    
    def get(self, by: Card, battle_state: BattleState) -> list[Card]:
        card_list: list[Card] = get_card_pile_data(self.among, battle_state)
        name: str = get_card_pile_name(self.among)
        if len(card_list) == 0:
            raise CardTarget.NoneAvailabeException()
        card = battle_state.get_player_card_target(name, card_list)
        return [card]
    
    def __repr__(self) -> str:
        return f"your choice in {get_card_pile_name(self.among)}"
'''
class AllCardsTarget(CardTarget):
    def __init__(self, among: CardPile):
        self.among = among
'''