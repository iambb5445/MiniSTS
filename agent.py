from __future__ import annotations
from action.action import Action
from config import Character, MAX_HEALTH
from value import RandomUniformRange, ConstValue
from utility import RoundRobin, RoundRobinRandomStart, ItemSet, ItemSequence, RandomizedItemSet, PreventRepeats
from action.action import EndAgentTurn
from action.agent_targeted_action import DealAttackDamage, AddBlock, ApplyStatus
from target.agent_target import PlayerAgentTarget, SelfAgentTarget
from config import StatusEffect, STACK_BEHAVIOR, END_TURN_BEHAVIOR, MAX_BLOCK, CHARACTER_NAME
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
        self.status_effects:dict[StatusEffect, int] = {}
        self.name = name
    
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
        
    def decrease_status(self):
        for key in self.status_effects:
            self.status_effects[key] = END_TURN_BEHAVIOR[key](self.status_effects[key])
        self.status_effects = dict([(effect, value) for effect, value in self.status_effects.items() if value > 0])

    def clean_up(self):
        self.status_effects = {}
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
    
    def apply_status(self, status: StatusEffect, amount: int):
        assert amount >= 0, "StatusEffect amount cannot be less than 0"
        self.status_effects[status] = STACK_BEHAVIOR[status](self.status_effects.get(status, 0), amount)
    
    def _get_action(self, game_state: GameState, battle_state: BattleState) -> Action:
        raise NotImplementedError("The \"_get_action\" method is not implemented for {}.".format(self.__class__.__name__))
    
    def play(self, game_state: GameState, battle_state: BattleState) -> None:
        self._get_action(game_state, battle_state).play(self, game_state, battle_state)
    
    def __repr__(self) -> str:
        return "{}-hp:[{}/{}]-block:{}-status:{}".format(
            self.name, self.health, self.max_health, self.block, self.status_effects
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
                ApplyStatus(ConstValue(1), StatusEffect.WEAK).To(PlayerAgentTarget())
            )
        else:
            action_set: ItemSet[Action] = RoundRobin(0,
                DealAttackDamage(ConstValue(3 if game_state.ascention < 2 else 4)).To(PlayerAgentTarget()),
                ApplyStatus(ConstValue(1), StatusEffect.WEAK).To(PlayerAgentTarget())
            )
        super().__init__("AcidSlime (S)", max_health.get(), action_set)

class SpikeSlimeSmall(Enemy):
    def __init__(self, game_state: GameState):
        max_health = RandomUniformRange(10, 14) if game_state.ascention < 7 else RandomUniformRange(11, 15)
        action_set: ItemSet[Action] = RoundRobin(0, DealAttackDamage(ConstValue(5 if game_state.ascention < 2 else 6)).To(PlayerAgentTarget()))
        super().__init__("SpikeSlime (S)", max_health.get(), action_set)

class JawWorm(Enemy):
    def __init__(self, game_state: GameState):
        max_health = RandomUniformRange(40, 44) if game_state.ascention < 7 else RandomUniformRange(42, 46)
        chomp: Action = DealAttackDamage(ConstValue(11 if game_state.ascention < 2 else 12)).To(PlayerAgentTarget())
        thrash: Action = DealAttackDamage(ConstValue(7)).To(PlayerAgentTarget()).And(AddBlock(ConstValue(5)).To(SelfAgentTarget()))
        bellow: Action = ApplyStatus(ConstValue(3 if game_state.ascention < 2 else 4 if game_state.ascention < 17 else 5), StatusEffect.STRENGTH).And(AddBlock(ConstValue(5))).To(SelfAgentTarget())
        regular_turn: ItemSet[Action] = RandomizedItemSet((bellow, 0.45), (thrash, 0.30), (chomp, 0.25))
        all_turns: ItemSet[Action] = ItemSequence(chomp, regular_turn)
        action_set = PreventRepeats(all_turns, (bellow, 2), (thrash, 3), (chomp, 2), consecutive=True)
        super().__init__("JawWorm", max_health.get(), action_set)
        