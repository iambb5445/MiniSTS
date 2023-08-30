from target import CreatureSet, ChooseCreature
from action import Action, DealDamage, GainBlock, ApplyStatus
from config import CardType, Character, Rarity, StatusEffect
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


class CardGen:
    Strike = lambda: Card("Strike", CardType.ATTACK, ConstValue(1), Character.IRON_CLAD, Rarity.STARTER, DealDamage(UpgradableOnce(6, 9)).To(ChooseCreature(CreatureSet.ENEMY)))
    Defend = lambda: Card("Defend", CardType.SKILL, ConstValue(1), Character.IRON_CLAD, Rarity.STARTER, GainBlock(UpgradableOnce(5, 8)))
    Searing_Blow = lambda: Card("Searing Blow", CardType.ATTACK, ConstValue(2), Character.IRON_CLAD, Rarity.UNCOMMON, DealDamage(LinearUpgradable(12, 4)).To(ChooseCreature(CreatureSet.ENEMY)))
    Bash = lambda: Card("Bash", CardType.ATTACK, ConstValue(2), Character.IRON_CLAD, Rarity.STARTER, DealDamage(UpgradableOnce(8, 10)).And(ApplyStatus(UpgradableOnce(2, 3), StatusEffect.VULNERABLE)).To(ChooseCreature(CreatureSet.ENEMY)))

class CardRepo:
    @staticmethod
    def get_starter(character: Character):
        starter: list[Card] = []
        if character == Character.IRON_CLAD:
            starter += [CardGen.Strike() for _ in range(5)]
            starter += [CardGen.Defend() for _ in range(4)]
            starter += [CardGen.Bash() for _ in range(1)]