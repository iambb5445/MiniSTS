from __future__ import annotations
from target.agent_target import AgentSet, ChooseAgentTarget, SelfAgentTarget, AllAgentsTarget, RandomAgentTarget
from target.card_target import CardPile, SelfCardTarget, ChooseCardTarget
from action.action import Action, AddMana
from action.agent_targeted_action import DealAttackDamage, ApplyStatus, AddBlock, Heal
from action.card_targeted_action import CardTargetedL1, Exhaust, AddCopy, UpgradeCard, DiscardCard
from config import CardType, Character, Rarity
from status_effecs import StatusEffectRepo, StatusEffectDefinition
from value import Value, ConstValue, UpgradableOnce, LinearUpgradable
from utility import RandomStr
from typing import TYPE_CHECKING, Callable
if TYPE_CHECKING:
    from game import GameState
    from battle import BattleState

class Card:
    def __init__(self, name: str, card_type: CardType, mana_cost: Value, character: Character, rarity: Rarity, *actions: Action|CardTargetedL1, desc: str|None = None):
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
        self.desc = desc if desc is not None else " ".join([f"{action}" for action in self.actions])
    
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

    def get_name(self) -> str:
        return "{}{}".format(self.name, "+"*self.upgrade_count)
    
    def __repr__(self) -> str:
        return "{}-cost:{}-{}-{}\n-".format(self.get_name(), self.mana_cost.peek(), self.card_type, self.rarity) + \
            "\n-".join(['' + action.__repr__() for action in self.actions])

    def get_description(self) -> str:
        return self.desc

class CardGen:
    Strike = lambda: Card("Strike", CardType.ATTACK, ConstValue(1), Character.IRON_CLAD, Rarity.STARTER, DealAttackDamage(UpgradableOnce(6, 9)).To(ChooseAgentTarget(AgentSet.ENEMY)))
    Defend = lambda: Card("Defend", CardType.SKILL, ConstValue(1), Character.IRON_CLAD, Rarity.STARTER, AddBlock(UpgradableOnce(5, 8)).To(SelfAgentTarget()))
    Searing_Blow = lambda: Card("SearingBlow", CardType.ATTACK, ConstValue(2), Character.IRON_CLAD, Rarity.UNCOMMON, DealAttackDamage(LinearUpgradable(12, 4)).To(ChooseAgentTarget(AgentSet.ENEMY)))
    Bash = lambda: Card("Bash", CardType.ATTACK, ConstValue(2), Character.IRON_CLAD, Rarity.STARTER, DealAttackDamage(UpgradableOnce(8, 10)).And(ApplyStatus(UpgradableOnce(2, 3), StatusEffectRepo.VULNERABLE)).To(ChooseAgentTarget(AgentSet.ENEMY)))
    BashStar = lambda: Card("Bash", CardType.ATTACK, ConstValue(2), Character.IRON_CLAD, Rarity.STARTER, DealAttackDamage(UpgradableOnce(8, 10)).To(ChooseAgentTarget(AgentSet.ENEMY)).And(ApplyStatus(UpgradableOnce(2, 3), StatusEffectRepo.VULNERABLE).To(ChooseAgentTarget(AgentSet.ENEMY))))
    Anger = lambda: Card("Anger", CardType.ATTACK, ConstValue(0), Character.IRON_CLAD, Rarity.COMMON, DealAttackDamage(UpgradableOnce(6, 8)).To(ChooseAgentTarget(AgentSet.ENEMY)), AddCopy(CardPile.DISCARD).To(SelfCardTarget()))
    # TODO upgrade for Armament
    Armaments = lambda: Card("Armament", CardType.SKILL, ConstValue(1), Character.IRON_CLAD, Rarity.COMMON, AddBlock(ConstValue(5)).To(SelfAgentTarget()), UpgradeCard().To(ChooseCardTarget(CardPile.HAND)))
    Cleave = lambda: Card("Cleave", CardType.ATTACK, ConstValue(1), Character.IRON_CLAD, Rarity.COMMON, DealAttackDamage(UpgradableOnce(8, 11)).To(AllAgentsTarget(AgentSet.ENEMY)))
    Impervious = lambda: Card("Impervious", CardType.SKILL, ConstValue(2), Character.IRON_CLAD, Rarity.RARE, AddBlock(UpgradableOnce(30, 40)).To(SelfAgentTarget()), Exhaust().To(SelfCardTarget()))
    # TODO this doesn't work yet, here for reference
    Survivor = lambda: Card("Survivor", CardType.SKILL, ConstValue(1), Character.SILENT, Rarity.COMMON, AddBlock(ConstValue(8)).To(SelfAgentTarget()), DiscardCard().To(ChooseCardTarget(CardPile.HAND)))
    # NEW CARDS
    Stimulate = lambda: Card("Stimulate", CardType.SKILL, ConstValue(1), Character.IRON_CLAD, Rarity.COMMON, ApplyStatus(ConstValue(4), StatusEffectRepo.VIGOR).To(SelfAgentTarget()))
    Batter = lambda: Card("Batter", CardType.SKILL, ConstValue(1), Character.IRON_CLAD, Rarity.COMMON, DealAttackDamage(ConstValue(0), ConstValue(10)).To(ChooseAgentTarget(AgentSet.ENEMY)))
    Tolerate = lambda: Card("Tolerate", CardType.POWER, ConstValue(3), Character.IRON_CLAD, Rarity.COMMON, ApplyStatus(ConstValue(1), StatusEffectRepo.TOLERANCE).To(SelfAgentTarget()), desc="Gain 1 block every turn and increase this gain by 2.")
    Bomb = lambda: Card("Bomb", CardType.SKILL, ConstValue(2), Character.IRON_CLAD, Rarity.COMMON, ApplyStatus(ConstValue(3), StatusEffectRepo.BOMB).To(SelfAgentTarget()), desc="At the end of 3 turns, deal 40 damage to all enemies.")
    Suffer = lambda: Card("Suffer", CardType.ATTACK, ConstValue(1), Character.IRON_CLAD, Rarity.STARTER, DealAttackDamage(UpgradableOnce(15, 30)).To(ChooseAgentTarget(AgentSet.ENEMY)))

class CardRepo:
    @staticmethod
    def get_random() -> Callable[[], Card]:
        import random, string
        import numpy as np
        def get_random_pile():
            return random.choice([CardPile.HAND, CardPile.DISCARD, CardPile.DRAW])
        def get_random_target():
            return random.choice([AllAgentsTarget(AgentSet.ALL), AllAgentsTarget(AgentSet.ENEMY), SelfAgentTarget(), ChooseAgentTarget(AgentSet.ENEMY), RandomAgentTarget(AgentSet.ENEMY)])
        def get_deal_damage(cost: Value) -> Action:
            val = random.randint(0, int((cost.peek() + 1) * 10))
            multi = 1 if random.randint(0, 3) != 0 else random.randint(2, 10)
            target = get_random_target()
            return DealAttackDamage(ConstValue(int(val/multi)), ConstValue(multi)).To(target)
        def get_add_copy():
            return AddCopy(CardPile.DISCARD).To(SelfCardTarget())
        def get_add_block(cost: Value) -> Action:
            val = random.randint(0, int((cost.peek() + 1) * 7))
            return AddBlock(ConstValue(val)).To(get_random_target())
        def get_apply_status(cost: Value) -> Action:
            val = random.randint(0, int((cost.peek() + 1) * 5))
            ses: list[StatusEffectDefinition] = [StatusEffectRepo.STRENGTH, StatusEffectRepo.VIGOR, StatusEffectRepo.VULNERABLE, StatusEffectRepo.WEAK]
            status = random.choice(ses)
            return ApplyStatus(ConstValue(val), status).To(get_random_target())
        def get_random_action(cost: Value) -> Action|CardTargetedL1:
            return random.choice([
                get_deal_damage(cost), get_add_copy(), get_add_block(cost), get_apply_status(cost)
                ])
        name = RandomStr.get_random()
        type = random.choice([CardType.ATTACK, CardType.POWER, CardType.SKILL])
        p = np.array([1, 1, 0.8, 0.3, 0.1, 0.05])
        p /= sum(p)
        cost = np.random.choice([0, 1, 2, 3, 4, 5], p=p)
        char = Character.IRON_CLAD
        rarity = Rarity.COMMON
        acs: list[CardTargetedL1|Action] = []
        p = np.array([1, 0.5, 0.1])
        p /= sum(p)
        ac_count = np.random.choice([1, 2, 3], p=p)
        if type == CardType.ATTACK:
            acs.append(get_deal_damage(ConstValue(int(cost/ac_count))))
        while len(acs) != ac_count:
            acs.append(get_random_action(ConstValue(int(cost/ac_count))))
        if random.randint(0, 3) == 0:
            acs.append(Exhaust().To(SelfCardTarget()))
        # TODO check copy
        gen = lambda: Card(name, type, ConstValue(cost), char, rarity, *acs)
        return gen

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
    def get_basics() -> list[Card]:
        deck: list[Card] = []
        deck += [CardGen.Strike() for _ in range(5)]
        deck += [CardGen.Defend() for _ in range(4)]
        return deck
    
    @staticmethod
    def get_scenario_0() -> tuple[str, list[Card]]:
        deck: list[Card] = CardRepo.get_starter(Character.IRON_CLAD)
        return "starter-ironclad", deck

    @staticmethod
    def get_scenario_1() -> tuple[str, list[Card]]:
        deck: list[Card] = CardRepo.get_basics()
        deck += [CardGen.Batter(), CardGen.Stimulate()]
        return "basics-batter-stimulate", deck
    
    @staticmethod
    def get_scenario_2() -> tuple[str, list[Card]]:
        deck: list[Card] = []
        deck += [CardGen.Strike() for _ in range(1)]
        deck += [CardGen.Defend() for _ in range(3)]
        deck += [CardGen.Tolerate()]
        return "1s3d-tolerate", deck

    @staticmethod
    def get_scenario_3() -> tuple[str, list[Card]]:
        deck: list[Card] = CardRepo.get_basics()
        deck += [CardGen.Bomb()]
        return "basics-bomb", deck

    @staticmethod
    def get_scenario_4() -> tuple[str, list[Card]]:
        deck: list[Card] = CardRepo.get_basics()
        deck += [CardGen.Suffer()]
        return "basics-suffer", deck
    
    @staticmethod
    def anonymize_scenario(scenario: tuple[str, list[Card]]) -> tuple[str, list[Card]]:
        name, cards = scenario
        cards = CardRepo.anonymize_deck(cards)
        return name, cards
    
    @staticmethod
    def anonymize_deck(cards: list[Card]):
        for card in cards:
            card.name = RandomStr.get_hashed(card.name)
        return cards