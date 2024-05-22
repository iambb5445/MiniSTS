from __future__ import annotations
from action.action import Action
from config import Character, MAX_HEALTH
from value import RandomUniformRange, ConstValue
from utility import RoundRobin, RoundRobinRandomStart, ItemSet, ItemSequence, RandomizedItemSet, PreventRepeats
from action.action import EndAgentTurn
from action.agent_targeted_action import DealAttackDamage, AddBlock, ApplyStatus
from target.agent_target import PlayerAgentTarget, SelfAgentTarget
from config import MAX_BLOCK, CHARACTER_NAME
from status_effecs import StatusEffectState, StatusEffectRepo
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from battle import BattleState
    from game import GameState
    from action.action import Action
    from ggpa.ggpa import GGPA

class Agent:
    def __init__(self, name: str, max_health: int):
        self.max_health = max_health
        self.health = max_health
        self.block = 0
        self.status_effect_state = StatusEffectState()
        self.name = name
        self.prev_action: Action|None = None
    
    def set_name(self) -> None:
        raise NotImplementedError("Set name is not implemented for {}.".format(self.__class__.__name__))
    
    def is_dead(self):
        return self.health <= 0

    def get_damaged(self, amount: int):
        assert amount >= 0, "Damage amount cannot be less than 0"
        blocked = min(self.block, amount)
        amount -= blocked
        self.block -= blocked
        self.health -= amount
        if self.health <= 0:
            self.health = 0
    
    def clear_block(self):
        self.block = 0

    def clean_up(self):
        self.status_effect_state.clean_up()
        self.block = 0

    def gain_block(self, amount: int):
        assert amount >= 0, "Block amount cannot be less than 0"
        self.block += amount
        if self.block >= MAX_BLOCK:
            self.block = MAX_BLOCK
        
    def get_healed(self, amount: int):
        assert amount >= 0, "Heal amount cannot be less than 0"
        self.health += amount
        if self.health >= self.max_health:
            self.health = self.max_health
    
    def _get_action(self, game_state: GameState, battle_state: BattleState) -> Action:
        raise NotImplementedError("The \"_get_action\" method is not implemented for {}.".format(self.__class__.__name__))
    
    def play(self, game_state: GameState, battle_state: BattleState) -> None:
        self.prev_action = self._get_action(game_state, battle_state)
        self.prev_action.play(self, game_state, battle_state)
    
    def __repr__(self) -> str:
        return "{}-hp:[{}/{}]-block:{}-status:{}".format(
            self.name, self.health, self.max_health, self.block, self.status_effect_state
        )

class Player(Agent):
    def __init__(self, character: Character, bot: GGPA):
        self.character = character
        self.bot = bot
        super().__init__(CHARACTER_NAME[self.character], MAX_HEALTH[self.character])
    
    def _get_action(self, game_state: GameState, battle_state: BattleState):
        return self.bot.choose_card(game_state, battle_state)

class Enemy(Agent):
    def __init__(self, name: str, max_health: int, action_set: ItemSet[Action]):
        super().__init__(name, max_health)
        self.action_set = action_set

    def _get_action(self, game_state: GameState, battle_state: BattleState) -> Action:
        return self.action_set.get().And(EndAgentTurn())

    def get_intention(self, game_state: GameState, battle_state: BattleState) -> Action:
        return self.action_set.peek()

class AcidSlimeSmall(Enemy):
    def __init__(self, game_state: GameState):
        max_health = RandomUniformRange(8, 12) if game_state.ascention < 7 else RandomUniformRange(9, 13)
        if game_state.ascention < 17:
            action_set: ItemSet[Action] = RoundRobinRandomStart(
                DealAttackDamage(ConstValue(3 if game_state.ascention < 2 else 4)).To(PlayerAgentTarget()),
                ApplyStatus(ConstValue(1), StatusEffectRepo.WEAK).To(PlayerAgentTarget())
            )
        else:
            action_set: ItemSet[Action] = RoundRobin(0,
                DealAttackDamage(ConstValue(3 if game_state.ascention < 2 else 4)).To(PlayerAgentTarget()),
                ApplyStatus(ConstValue(1), StatusEffectRepo.WEAK).To(PlayerAgentTarget())
            )
        super().__init__("AcidSlime(S)", max_health.get(), action_set)

class SpikeSlimeSmall(Enemy):
    def __init__(self, game_state: GameState):
        max_health = RandomUniformRange(10, 14) if game_state.ascention < 7 else RandomUniformRange(11, 15)
        action_set: ItemSet[Action] = RoundRobin(0, DealAttackDamage(ConstValue(5 if game_state.ascention < 2 else 6)).To(PlayerAgentTarget()))
        super().__init__("SpikeSlime(S)", max_health.get(), action_set)

class JawWorm(Enemy):
    def __init__(self, game_state: GameState):
        max_health = RandomUniformRange(40, 44) if game_state.ascention < 7 else RandomUniformRange(42, 46)
        chomp: Action = DealAttackDamage(ConstValue(11 if game_state.ascention < 2 else 12)).To(PlayerAgentTarget())
        thrash: Action = DealAttackDamage(ConstValue(7)).To(PlayerAgentTarget()).And(AddBlock(ConstValue(5)).To(SelfAgentTarget()))
        bellow: Action = ApplyStatus(ConstValue(3 if game_state.ascention < 2 else 4 if game_state.ascention < 17 else 5), StatusEffectRepo.STRENGTH).And(AddBlock(ConstValue(5))).To(SelfAgentTarget())
        regular_turn: ItemSet[Action] = RandomizedItemSet((bellow, 0.45), (thrash, 0.30), (chomp, 0.25))
        all_turns: ItemSet[Action] = ItemSequence(chomp, regular_turn)
        action_set = PreventRepeats(all_turns, (bellow, 2), (thrash, 3), (chomp, 2), consecutive=True)
        super().__init__("JawWorm", max_health.get(), action_set)
        
class Goblin(Enemy):
    def __init__(self, game_state: GameState):
        max_health = ConstValue(44)
        slash: Action = DealAttackDamage(ConstValue(11)).To(PlayerAgentTarget())
        stand: Action = DealAttackDamage(ConstValue(7)).To(PlayerAgentTarget()).And(AddBlock(ConstValue(5)).To(SelfAgentTarget()))
        action_set: ItemSet[Action] = RoundRobin(0, slash, stand)
        super().__init__("Goblin", max_health.get(), action_set)

class HobGoblin(Enemy):
    def __init__(self, game_state: GameState):
        max_health = ConstValue(44)
        slash: Action = DealAttackDamage(ConstValue(22)).To(PlayerAgentTarget())
        stand: Action = DealAttackDamage(ConstValue(10)).To(PlayerAgentTarget()).And(AddBlock(ConstValue(10)).To(SelfAgentTarget()))
        action_set: ItemSet[Action] = RoundRobin(0, slash, stand)
        super().__init__("Goblin", max_health.get(), action_set)

class Leech(Enemy):
    def __init__(self, game_state: GameState):
        max_health = ConstValue(70)
        drink: Action = DealAttackDamage(ConstValue(1)).To(PlayerAgentTarget()).And(ApplyStatus(ConstValue(1), StatusEffectRepo.WEAK).To(PlayerAgentTarget()))
        bite: Action = DealAttackDamage(ConstValue(4)).To(PlayerAgentTarget())
        action_set: ItemSet[Action] = RoundRobin(0, drink, bite)
        super().__init__("Leach", max_health.get(), action_set)