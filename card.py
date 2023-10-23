from __future__ import annotations
from target.agent_target import AgentSet, ChooseAgentTarget, SelfAgentTarget, AllAgentsTarget
from target.card_target import CardPile, SelfCardTarget, ChooseCardTarget
from action.action import Action, AddMana
from action.agent_targeted_action import DealAttackDamage, ApplyStatus, AddBlock
from action.card_targeted_action import CardTargetedL1, Exhaust, AddCopy, UpgradeCard
from config import CardType, Character, Rarity
from status_effecs import StatusEffect
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
        self.upgrade_count = 0
        self.mana_action = AddMana(mana_cost.negative())
        self.actions: list[Action] = []
        for action in actions:
            if isinstance(action, Action):
                self.actions.append(action)
            else:
                self.actions.append(action.By(self))
    
    def play(self, game_state: GameState, battle_state: BattleState):
        assert self.is_playable(game_state, battle_state)
        self.mana_action.play(game_state.player, game_state, battle_state)
        for action in self.actions:
            action.play(game_state.player, game_state, battle_state)

    def is_playable(self, game_state: GameState, battle_state: BattleState):
        return self.mana_cost.peek() <= battle_state.mana

    def upgrade(self, times: int = 1):
        self.upgrade_count += times
        self.mana_cost.upgrade(times)
        for action in self.actions:
            for val in action.values:
                val.upgrade(times)

    def get_name(self):
        return "{}{}".format(self.name, "+"*self.upgrade_count)
    
    def __repr__(self) -> str:
        return "{}-cost:{}-{}-{}\n-".format(self.get_name(), self.mana_cost.peek(), self.card_type, self.rarity) + \
            "\n-".join(['' + action.__repr__() for action in self.actions])

class CardGen:
    Strike = lambda: Card("Strike", CardType.ATTACK, ConstValue(1), Character.IRON_CLAD, Rarity.STARTER, DealAttackDamage(UpgradableOnce(6, 9)).To(ChooseAgentTarget(AgentSet.ENEMY)))
    Defend = lambda: Card("Defend", CardType.SKILL, ConstValue(1), Character.IRON_CLAD, Rarity.STARTER, AddBlock(UpgradableOnce(5, 8)).To(SelfAgentTarget()))
    Searing_Blow = lambda: Card("SearingBlow", CardType.ATTACK, ConstValue(2), Character.IRON_CLAD, Rarity.UNCOMMON, DealAttackDamage(LinearUpgradable(12, 4)).To(ChooseAgentTarget(AgentSet.ENEMY)))
    Bash = lambda: Card("Bash", CardType.ATTACK, ConstValue(2), Character.IRON_CLAD, Rarity.STARTER, DealAttackDamage(UpgradableOnce(8, 10)).And(ApplyStatus(UpgradableOnce(2, 3), StatusEffect.VULNERABLE)).To(ChooseAgentTarget(AgentSet.ENEMY)))
    Anger = lambda: Card("Anger", CardType.ATTACK, ConstValue(0), Character.IRON_CLAD, Rarity.COMMON, DealAttackDamage(UpgradableOnce(6, 8)).To(ChooseAgentTarget(AgentSet.ENEMY)), AddCopy(CardPile.DISCARD).To(SelfCardTarget()))
    # TODO upgrade for Armament
    Armaments = lambda: Card("Armament", CardType.SKILL, ConstValue(1), Character.IRON_CLAD, Rarity.COMMON, AddBlock(ConstValue(5)).To(SelfAgentTarget()), UpgradeCard().To(ChooseCardTarget(CardPile.HAND)))
    Cleave = lambda: Card("Cleave", CardType.ATTACK, ConstValue(1), Character.IRON_CLAD, Rarity.COMMON, DealAttackDamage(UpgradableOnce(8, 11)).To(AllAgentsTarget(AgentSet.ENEMY)))
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
    
    @staticmethod
    def anonymize_deck(cards: list[Card]) -> list[Card]:
        anonymized = {
            'Strike': 'Charge',
            'Defend': 'Brace',
            'Bash': 'Knock'
        }
        deck = [card for card in cards]
        for card in deck:
            if card.name in anonymized:
                card.name = anonymized[card.name]
            else:
                raise Exception(f'Unrecognized card name {card.name}')
        return deck