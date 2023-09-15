from __future__ import annotations
from copy import deepcopy
from ggpa.ggpa import GGPA
from action.action import EndAgentTurn, PlayCard
from typing import TYPE_CHECKING
from config import Verbose
if TYPE_CHECKING:
    from game import GameState
    from battle import BattleState
    from agent import Agent
    from card import Card
    from agent import Agent
    from card import Card

class BacktrackBot(GGPA):
    def __init__(self, depth: int):
        self.depth = depth

    def _evaluate_state(self, game_state: GameState, battle_state: BattleState) -> int:
        return battle_state.player.health - sum([enemy.health for enemy in battle_state.enemies])
    
    def _get_best_choose_card(self, game_state: GameState, battle_state: BattleState, depth_remaining: int) -> tuple[int|None, PlayCard|EndAgentTurn|None]:
        if depth_remaining == 0:
            return self._evaluate_state(game_state, battle_state), None
        options = self.get_choose_card_options(game_state, battle_state)
        best_value, best_action = None, None
        for option in options:
            battle_state_copy: BattleState = deepcopy(battle_state)
            battle_state_copy.verbose = Verbose.NO_LOG
            if not battle_state_copy.tick_player(option):
                estimate = battle_state_copy.get_end_result() * 1000
            else:
                estimate, _ = self._get_best_choose_card(battle_state_copy.game_state, battle_state_copy, depth_remaining-1)
            if best_value is None or (estimate is not None and best_value < estimate):
                best_value = estimate
                best_action = option
        return best_value, best_action

    def choose_card(self, game_state: GameState, battle_state: BattleState) -> EndAgentTurn|PlayCard:
        _, action = self._get_best_choose_card(game_state, battle_state, self.depth)
        if action is None:
            raise Exception("Depth is 0 or no action is available")
        return action
    
    def choose_agent_target(self, battle_state: BattleState, list_name: str, agent_list: list[Agent]) -> Agent:
        return agent_list[0]
    
    def choose_card_target(self, battle_state: BattleState, list_name: str, card_list: list[Card]) -> Card:
        return card_list[0]
    