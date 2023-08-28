from config import CardType, Character, Rarity
from value import Value, ConstValue, Upgradable, LinearUpgradable

class CardAction:
    def __init__(self):
        pass
    
    def play(self) -> None:
        raise NotImplementedError("The \"play\" method is not implemented for this CardAction.")
    
class DealDamage(CardAction):
    def __init__(self, val: Value):
        self.val = val

class GainBlock(CardAction):
    def __init__(self, val: Value):
        self.val = val

class Card:
    def __init__(self, name: str, card_type: CardType, mana_cost: Value, character: Character, rarity: Rarity, *actions: CardAction):
        self.name = name
        self.card_type = card_type
        self.mana_cost = mana_cost
        self.character = character
        self.rarity = rarity
        self.actions: list[CardAction] = []
        for action in actions:
            self.actions.append(action)
    
    def play(self):
        for action in self.actions:
            action.play()

CARDS = [
    Card("Strike", CardType.ATTACK, ConstValue(1), Character.IRON_CLAD, Rarity.STARTER, DealDamage(Upgradable(6, 9))),
    Card("Defend", CardType.SKILL, ConstValue(1), Character.IRON_CLAD, Rarity.STARTER, GainBlock(Upgradable(5, 8))),
    Card("Searing Blow", CardType.ATTACK, ConstValue(2), Character.IRON_CLAD, Rarity.UNCOMMON, DealDamage(LinearUpgradable(12, 4))),
]

CARD_DICT = dict([(card.name, card) for card in CARDS]) # TODO cards with same name