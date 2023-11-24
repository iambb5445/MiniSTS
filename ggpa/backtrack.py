from __future__ import annotations
from ggpa.ggpa import GGPA
from action.action import EndAgentTurn, PlayCard
from typing import TYPE_CHECKING
import random
from config import Verbose
if TYPE_CHECKING:
    from game import GameState
    from battle import BattleState
    from agent import Agent
    from card import Card
    from agent import Agent
    from card import Card

class BacktrackBot(GGPA):
    def __init__(self, depth: int, should_save_states: bool):
        super().__init__(f"Backtrack-Depth{depth}{'-save' if should_save_states else ''}")
        self.depth = depth
        self.should_save_states = should_save_states
        self.memory: dict[str, float|None] = {}
        self.memory_hit = 0

    def _rollout_state(self, game_state: GameState, battle_state: BattleState, count: int) -> list[BattleState]:
        def stop(battle_state: BattleState):
            return battle_state.ended() or isinstance(battle_state.player.prev_action, EndAgentTurn)
        if stop(battle_state) or count == 0:
            return [battle_state]
        ret: list[BattleState] = [battle_state.copy_undeterministic() for _ in range(count)]
        for i in range(count):
            ret[i].verbose = Verbose.NO_LOG
            while not stop(ret[i]):
                options = self.get_choose_card_options(ret[i].game_state, ret[i])
                option = random.choice(options)
                ret[i].tick_player(option)
        return ret

    def _evaluate_state(self, game_state: GameState, battle_state: BattleState) -> float:
        #print("Visualization")
        #print(battle_state.get_visualization())
        win = battle_state.get_end_result()
        if win == -1:
            return -1000
        def _get_value(battle_state: BattleState) -> float:
            return battle_state.player.health - sum([enemy.health for enemy in battle_state.enemies]) + (0.5 if win == 1 else 0)
        rollout = self._rollout_state(game_state, battle_state, 0)
        values = [_get_value(rolledout_battle_state) for rolledout_battle_state in rollout]
        return sum(values)/len(values)
    
    def _get_best_choose_card(self, game_state: GameState, battle_state: BattleState, depth_remaining: int) -> tuple[float|None, PlayCard|EndAgentTurn|None]:
        #print(f"Depth remaining: {depth_remaining}")
        if depth_remaining == 0:
            value = self._evaluate_state(game_state, battle_state), None
            #print(f"{depth_remaining}: Returning: {value}")
            return value
        options = self.get_choose_card_options(game_state, battle_state)
        best_value, best_action = None, None
        for option in options:
            battle_state_copy: BattleState = battle_state.copy_undeterministic()
            battle_state_copy.verbose = Verbose.NO_LOG
            #print(f"{depth_remaining}: Tick battle {option}")
            if not battle_state_copy.tick_player(option):
                estimate = self._evaluate_state(battle_state_copy.game_state, battle_state_copy)
                #print(f"{depth_remaining-1}: Ended {estimate}")
            else:
                state_hash = ''
                if self.should_save_states:
                    state_hash = battle_state_copy.get_undeterministic_repr_hash()
                    if state_hash in self.memory:
                        estimate = self.memory[state_hash]
                        self.memory_hit += 1
                    else:
                        estimate, _ = self._get_best_choose_card(battle_state_copy.game_state, battle_state_copy, depth_remaining-1)
                        self.memory[state_hash] = estimate
                else:
                    #print(f"{depth_remaining}: Recursive")
                    estimate, _ = self._get_best_choose_card(battle_state_copy.game_state, battle_state_copy, depth_remaining-1)
                    #print(f"{depth_remaining}: Back")
            #print(f"{depth_remaining}: Estimate: {estimate}")
            if best_value is None or (estimate is not None and best_value < estimate):
                best_value = estimate
                best_action = option
                #print(f"{depth_remaining}: Best changed")
            #print(f"{depth_remaining}: Best is: {best_value}, {best_action}")
        #print(f"{depth_remaining}: Returning: {best_value}, {best_action}")
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
    