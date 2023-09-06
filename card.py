from __future__ import annotations
from target import AgentSet, ChooseAgentTarget, SelfAgentTarget, AllAgentsTarget, CardPile, SelfCardTarget, ChooseCardTarget
from action.action import Action, AddMana
from action.agent_targeted_action import DealDamage, ApplyStatus, AddBlock
from action.card_targeted_action import CardTargetedL1, Exhaust, AddCopy, UpgradeCard
from config import CardType, Character, Rarity, StatusEffect
from value import Value, ConstValue, UpgradableOnce, LinearUpgradable
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game import GameState
    from battle import BattleState

class Card:
    def __init__(self, name: str, card_type: CardType, mana_cost: Value, character: Character, rarity: Rarity, *actions: Action|CardTargetedL1):
        self.name = name
        self.card_type = card_type
        self.mana_cost = mana_cost
        self.character = character
        self.rarity = rarity
        self.mana_action = AddMana(mana_cost.negative())
        self.actions: list[Action] = []
        for action in actions:
            if isinstance(action, Action):
                self.actions.append(action)
            else:
                self.actions.append(action.By(self))
    
    def play(self, game_state: GameState, battle_state: BattleState):
        self.mana_action.play(game_state.player, game_state, battle_state)
        for action in self.actions:
            action.play(game_state.player, game_state, battle_state)

    def upgrade(self, times: int = 1):
        self.mana_cost.upgrade(times)
        for action in self.actions:
            for val in action.values:
                val.upgrade(times)
    
    def __repr__(self) -> str:
        return "-{}-cost:{}-{}-{}-{}\n-".format(self.name, self.mana_cost, self.card_type, self.rarity, self.character) + \
            "\n-".join([action.__repr__() for action in self.actions])

class CardGen:
    Strike = lambda: Card("Strike", CardType.ATTACK, ConstValue(1), Character.IRON_CLAD, Rarity.STARTER, DealDamage(UpgradableOnce(6, 9)).To(ChooseAgentTarget(AgentSet.ENEMY)))
    Defend = lambda: Card("Defend", CardType.SKILL, ConstValue(1), Character.IRON_CLAD, Rarity.STARTER, AddBlock(UpgradableOnce(5, 8)).To(SelfAgentTarget()))
    Searing_Blow = lambda: Card("SearingBlow", CardType.ATTACK, ConstValue(2), Character.IRON_CLAD, Rarity.UNCOMMON, DealDamage(LinearUpgradable(12, 4)).To(ChooseAgentTarget(AgentSet.ENEMY)))
    Bash = lambda: Card("Bash", CardType.ATTACK, ConstValue(2), Character.IRON_CLAD, Rarity.STARTER, DealDamage(UpgradableOnce(8, 10)).And(ApplyStatus(UpgradableOnce(2, 3), StatusEffect.VULNERABLE)).To(ChooseAgentTarget(AgentSet.ENEMY)))
    Anger = lambda: Card("Anger", CardType.ATTACK, ConstValue(0), Character.IRON_CLAD, Rarity.COMMON, DealDamage(UpgradableOnce(6, 8)).To(ChooseAgentTarget(AgentSet.ENEMY)), AddCopy(CardPile.DISCARD).To(SelfCardTarget()))
    Armaments = lambda: Card("Armament", CardType.SKILL, ConstValue(1), Character.IRON_CLAD, Rarity.COMMON, AddBlock(ConstValue(5)).To(SelfAgentTarget()), UpgradeCard().To(ChooseCardTarget(CardPile.HAND)))
    Cleave = lambda: Card("Cleave", CardType.ATTACK, ConstValue(1), Character.IRON_CLAD, Rarity.COMMON, DealDamage(UpgradableOnce(8, 11)).To(AllAgentsTarget(AgentSet.ENEMY)))
    Impervious = lambda: Card("Impervious", CardType.SKILL, ConstValue(2), Character.IRON_CLAD, Rarity.RARE, AddBlock(UpgradableOnce(30, 40)).To(SelfAgentTarget()), Exhaust().To(SelfCardTarget()))

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