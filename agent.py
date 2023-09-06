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
    
    def clear(self):
        self.block = 0
        # TODO status effects decrease

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
    
    def _get_action(self, game_state: GameState, battle_state: BattleState) -> Action:
        raise NotImplementedError("The \"_get_action\" method is not implemented for {}.".format(self.__class__.__name__))
    
    def play(self, game_state: GameState, battle_state: BattleState) -> None:
        self._get_action(game_state, battle_state).play(self, game_state, battle_state)
    
    def __repr__(self) -> str:
        return "{}-hp:[{}/{}]-block:{}-status:{}".format(
            self.name, self.health, self.max_health, self.block, self.status_effects
        )

class Player(Agent):
    def __init__(self, character: Character):
        self.character = character
        super().__init__(CHARACTER_NAME[self.character], MAX_HEALTH[self.character])
    
    def _get_action(self, game_state: GameState, battle_state: BattleState):
        while True:
            card_index = UserInput.ask_for_number(
                "Enter card number, or -1 for ending your turn: ",
                lambda val: val >= -1 and val < len(battle_state.get_hand())
            )
            if card_index < 0:
                battle_state.end_player_turn()
                return NoAction()
            elif battle_state.is_playable(battle_state.hand[card_index]):
                return PlayCard(card_index)
            else:
                print("Card is not playable.")

class Enemy(Agent):
    def __init__(self, name: str, max_health: int, action_set: ItemSet[Action]):
        super().__init__(name, max_health)
        self.action_set = action_set

    def _get_action(self, game_state: GameState, battle_state: BattleState) -> Action:
        return self.action_set.get()

    def get_intention(self, game_state: GameState, battle_state: BattleState) -> Action:
        return self.action_set.peek()

class AcidSlimeSmall(Enemy):
    def __init__(self, game_state: GameState):
        max_health = RandomUniformRange(8, 12) if game_state.ascention < 7 else RandomUniformRange(9, 13)
        if game_state.ascention < 17:
            action_set: ItemSet[Action] = RoundRobinRandomStart(
                DealDamage(ConstValue(3 if game_state.ascention < 2 else 4)).To(PlayerAgentTarget()),
                ApplyStatus(ConstValue(1), StatusEffect.WEAK).To(PlayerAgentTarget())
            )
        else:
            action_set: ItemSet[Action] = RoundRobin(0,
                DealDamage(ConstValue(3 if game_state.ascention < 2 else 4)).To(PlayerAgentTarget()),
                ApplyStatus(ConstValue(1), StatusEffect.WEAK).To(PlayerAgentTarget())
            )
        super().__init__("AcidSlime (S)", max_health.get(), action_set)