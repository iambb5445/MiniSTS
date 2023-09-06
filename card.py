from __future__ import annotations
from target import AgentSet, ChooseAgentTarget, SelfAgentTarget, AllAgentsTarget
from action import Action, DealDamage, ApplyStatus, AddBlock, AddMana
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
        self.mana_action = AddMana(mana_cost.negative())
        self.actions: list[Action] = []
        for action in actions:
            self.actions.append(action)
    
    def play(self, game_state: GameState, battle_state: BattleState):
        self.mana_action.play(game_state.player, game_state, battle_state)
        for action in self.actions:
            action.play(game_state.player, game_state, battle_state)

class CardGen:
    Strike = lambda: Card("Strike", CardType.ATTACK, ConstValue(1), Character.IRON_CLAD, Rarity.STARTER, DealDamage(UpgradableOnce(6, 9)).To(ChooseAgentTarget(AgentSet.ENEMY)))
    Defend = lambda: Card("Defend", CardType.SKILL, ConstValue(1), Character.IRON_CLAD, Rarity.STARTER, AddBlock(UpgradableOnce(5, 8)).To(SelfAgentTarget()))
    Searing_Blow = lambda: Card("SearingBlow", CardType.ATTACK, ConstValue(2), Character.IRON_CLAD, Rarity.UNCOMMON, DealDamage(LinearUpgradable(12, 4)).To(ChooseAgentTarget(AgentSet.ENEMY)))
    Bash = lambda: Card("Bash", CardType.ATTACK, ConstValue(2), Character.IRON_CLAD, Rarity.STARTER, DealDamage(UpgradableOnce(8, 10)).And(ApplyStatus(UpgradableOnce(2, 3), StatusEffect.VULNERABLE)).To(ChooseAgentTarget(AgentSet.ENEMY)))
    CLEAVE = lambda: Card("Cleave", CardType.ATTACK, ConstValue(1), Character.IRON_CLAD, Rarity.COMMON, DealDamage(UpgradableOnce(8, 11)).To(AllAgentsTarget(AgentSet.ENEMY)))

class CardRepo:
    @staticmethod
    def get_starter(character: Character) -> list[Card]:
        starter: list[Card] = []
        if character == Character.IRON_CLAD:
            starter += [CardGen.Strike() for _ in range(5)]
            starter += [CardGen.Defend() for _ in range(4)]
            starter += [CardGen.Bash() for _ in range(1)]
            return starter
        else:
            raise Exception("Undefined started deck for character {}.".format(character))