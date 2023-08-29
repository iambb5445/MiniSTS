from target import CreatureSet, ChooseCreature
from action import Action, DealDamage, GainBlock
from config import CardType, Character, Rarity
from value import Value, ConstValue, UpgradableOnce, LinearUpgradable

class Card:
    def __init__(self, name: str, card_type: CardType, mana_cost: Value, character: Character, rarity: Rarity, *actions: Action):
        self.name = name
        self.card_type = card_type
        self.mana_cost = mana_cost
        self.character = character
        self.rarity = rarity
        self.actions: list[Action] = []
        for action in actions:
            self.actions.append(action)
    
    def play(self):
        for action in self.actions:
            action.play()

CARDS = [
    Card("Strike", CardType.ATTACK, ConstValue(1), Character.IRON_CLAD, Rarity.STARTER, DealDamage(UpgradableOnce(6, 9), ChooseCreature(CreatureSet.ENEMY))),
    Card("Defend", CardType.SKILL, ConstValue(1), Character.IRON_CLAD, Rarity.STARTER, GainBlock(UpgradableOnce(5, 8))),
    Card("Searing Blow", CardType.ATTACK, ConstValue(2), Character.IRON_CLAD, Rarity.UNCOMMON, DealDamage(LinearUpgradable(12, 4), ChooseCreature(CreatureSet.ENEMY))),
]

CARD_DICT = dict([(card.name, card) for card in CARDS]) # TODO cards with same name