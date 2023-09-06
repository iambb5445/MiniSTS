from __future__ import annotations
from target import AgentSet, ChooseAgentTarget
from action import Action, DealDamage, ApplyStatus
from config import CardType, Character, Rarity, StatusEffect
from value import Value, ConstValue, UpgradableOnce, LinearUpgradable
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game import GameState
    from battle import BattleState

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
    
    def play(self, game_state: GameState, battle_state: BattleState):
        for action in self.actions:
            action.play(game_state, battle_state)

class CardGen:
    Strike = lambda: Card("Strike", CardType.ATTACK, ConstValue(1), Character.IRON_CLAD, Rarity.STARTER, DealDamage(UpgradableOnce(6, 9)).To(ChooseAgentTarget(AgentSet.ENEMY)))
    # TODO
    #Defend = lambda: Card("Defend", CardType.SKILL, ConstValue(1), Character.IRON_CLAD, Rarity.STARTER, GainBlock(UpgradableOnce(5, 8)))
    Searing_Blow = lambda: Card("SearingBlow", CardType.ATTACK, ConstValue(2), Character.IRON_CLAD, Rarity.UNCOMMON, DealDamage(LinearUpgradable(12, 4)).To(ChooseAgentTarget(AgentSet.ENEMY)))
    Bash = lambda: Card("Bash", CardType.ATTACK, ConstValue(2), Character.IRON_CLAD, Rarity.STARTER, DealDamage(UpgradableOnce(8, 10)).And(ApplyStatus(UpgradableOnce(2, 3), StatusEffect.VULNERABLE)).To(ChooseAgentTarget(AgentSet.ENEMY)))

class CardRepo:
    @staticmethod
    def get_starter(character: Character) -> list[Card]:
        starter: list[Card] = []
        if character == Character.IRON_CLAD:
            starter += [CardGen.Strike() for _ in range(5)]
            # TODO
            #starter += [CardGen.Defend() for _ in range(4)]
            starter += [CardGen.Bash() for _ in range(1)]
            return starter
        else:
            raise Exception("Undefined started deck for character {}.".format(character))