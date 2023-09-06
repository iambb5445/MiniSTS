from __future__ import annotations
from config import Character, MAX_HEALTH
from value import RandomUniformRange, ConstValue
from utility import RoundRobin, RoundRobinRandomStart, ItemSet
from action import Action, DealDamage, PlayCard, ApplyStatus, NoAction
from target import PlayerAgentTarget
from config import StatusEffect, MAX_BLOCK, CHARACTER_NAME
from utility import UserInput
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from battle import BattleState
    from game import GameState

class Agent:
    def __init__(self, name: str, max_health: int):
        self.max_health = max_health
        self.health = max_health
        self.block = 0
        self.status_effects:dict[StatusEffect, int] = {}
        self.name = name
    
    def set_name(self) -> None:
        raise NotImplementedError("Set name is not implemented for this agent.")
    
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
        self.status_effects[status] = self.status_effects.get(status, 0) + amount
    
    def get_action(self, game_state: GameState, battle_state: BattleState) -> Action:
        raise NotImplementedError("The \"get_action\" method is not implemented for this Agent.")
    
    def __repr__(self) -> str:
        return "{}-hp:[{}/{}]-block:{}-status:{}".format(
            self.name, self.health, self.max_health, self.block, self.status_effects
        )

class Player(Agent):
    def __init__(self, character: Character):
        self.character = character
        super().__init__(CHARACTER_NAME[self.character], MAX_HEALTH[self.character])
    
    def get_action(self, game_state: GameState, battle_state: BattleState):
        hand = battle_state.get_hand()
        if len(hand) > 0:
            return PlayCard(UserInput.ask_for_number(
                "Enter card number: ",
                lambda val: val >= 0 and val < len(battle_state.get_hand())
            ))
        print("No card available.")
        return NoAction()

class Enemy(Agent):
    def __init__(self, name: str, max_health: int):
        super().__init__(name, max_health)

class AcidSlimeSmall(Enemy):
    def __init__(self, game_state: GameState):
        max_health_gen = RandomUniformRange(8, 12) if game_state.ascention < 7 else RandomUniformRange(9, 13)
        super().__init__("AcidSlime (S)", max_health_gen.get())
        if game_state.ascention < 17:
            self.action_set: ItemSet[Action] = RoundRobinRandomStart(
                DealDamage(ConstValue(3 if game_state.ascention < 2 else 4)).To(PlayerAgentTarget()),
                ApplyStatus(ConstValue(1), StatusEffect.WEAK).To(PlayerAgentTarget())
            )
        else:
            self.action_set: ItemSet[Action] = RoundRobin(0,
                DealDamage(ConstValue(3 if game_state.ascention < 2 else 4)).To(PlayerAgentTarget()),
                ApplyStatus(ConstValue(1), StatusEffect.WEAK).To(PlayerAgentTarget())
            )
    
    def get_action(self, game_state: GameState, battle_state: BattleState) -> Action:
        return self.action_set.get()