from __future__ import annotations
import copy
import os.path
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from agent import Enemy, Agent
    from game import GameState
    from card import Card
    from action.action import Action
from config import MAX_MANA, Verbose
from utility import get_unique_filename

import random

class BattleState:
    def __init__(self, game_state: GameState, *enemies: Enemy, verbose: Verbose, log_filename: str|None = None):
        self.player = game_state.player
        self.enemies = [enemy for enemy in enemies]
        self.game_state = game_state
        self.turn = 0
        self.mana = 0
        self.agent_turn_ended = False
        self.turn_phase = 0
        self.draw_pile: list[Card] = []
        self.discard_pile: list[Card] = [copy.deepcopy(card) for card in self.game_state.deck]
        self.hand: list[Card] = []
        self.exhaust_pile: list[Card] = []
        self.verbose = verbose
        self.log_filename = log_filename

    def copy_undeterministic(self) -> BattleState:
        battle_state_copy = copy.deepcopy(self)
        random.shuffle(battle_state_copy.draw_pile)
        return battle_state_copy
    
    def get_undeterministic_repr_hash(self) -> str:
        import hashlib
        combined_hash = hashlib.sha256()
        for agent in [self.player] + self.enemies:
            combined_hash.update(hashlib.sha256(agent.__repr__().encode()).digest())
        combined_hash.update(hashlib.sha256(self.turn.__repr__().encode()).digest())
        combined_hash.update(hashlib.sha256(self.mana.__repr__().encode()).digest())
        combined_hash.update(hashlib.sha256(self.agent_turn_ended.__repr__().encode()).digest())
        combined_hash.update(hashlib.sha256(self.turn_phase.__repr__().encode()).digest())
        sorted_draw_pile = sorted(self.draw_pile, key=lambda card: repr(card))
        sorted_discard_pile = sorted(self.discard_pile, key=lambda card: repr(card))
        sorted_hand = sorted(self.hand, key=lambda card: repr(card))
        sorted_exhaust_pile = sorted(self.exhaust_pile, key=lambda card: repr(card))
        for card in sorted_draw_pile:
            combined_hash.update(hashlib.sha256(card.__repr__().encode()).digest())
        combined_hash.update(hashlib.sha256('-'.encode()).digest())
        for card in sorted_discard_pile:
            combined_hash.update(hashlib.sha256(card.__repr__().encode()).digest())
        combined_hash.update(hashlib.sha256('-'.encode()).digest())
        for card in sorted_hand:
            combined_hash.update(hashlib.sha256(card.__repr__().encode()).digest())
        combined_hash.update(hashlib.sha256('-'.encode()).digest())
        for card in sorted_exhaust_pile:
            combined_hash.update(hashlib.sha256(card.__repr__().encode()).digest())
        return combined_hash.hexdigest()

    def discard_hand(self):
        self.discard_pile += self.hand
        self.hand = []

    def reshuffle(self):
        self.draw_pile, self.discard_pile = self.draw_pile + self.discard_pile, []
        random.shuffle(self.draw_pile)

    def draw_one(self):
        if len(self.draw_pile) == 0:
            self.reshuffle()
        if len(self.draw_pile) > 0:
            self.hand.append(self.draw_pile.pop())
        else:
            #discard+draw+hand is empty
            pass

    def draw(self, count: int):
        for _ in range(count):
            self.draw_one()

    def draw_hand(self):
        draw_count = self.game_state.draw_count
        self.draw(draw_count)
    
    def get_hand(self):
        return self.hand
    
    def play_card(self, card_index: int):
        assert card_index < len(self.hand) and card_index >= 0, "Card index {} out of range for hand {}".format(card_index, self.hand)
        card = self.hand.pop(card_index)
        card.play(self.game_state, self)
        if not self.is_present(card):
            self.discard_pile.append(card)

    def is_present(self, card: Card):
        if card in self.hand:
            return True
        if card in self.draw_pile:
            return True
        if card in self.discard_pile:
            return True
        if card in self.exhaust_pile:
            return True
        return False
    
    def remove_card(self, card: Card):
        if card in self.hand:
            self.hand.remove(card)
        if card in self.draw_pile:
            self.draw_pile.remove(card)
        if card in self.discard_pile:
            self.discard_pile.remove(card)
        if card in self.exhaust_pile:
            self.exhaust_pile.remove(card)
    
    def exhaust(self, card: Card):
        self.remove_card(card)
        self.exhaust_pile.append(card)
    
    def log(self, log: str):
        if self.verbose == Verbose.NO_LOG:
            return
        if self.log_filename is None:
            print(log)
        else:
            with open(self.log_filename, 'a') as f:
                f.write(log)
    
    def visualize(self):
        if self.verbose == Verbose.NO_LOG:
            return
        log = ''
        log += "*Turn {} - {}*\n".format(self.turn, "Player" if self.turn_phase == 0 else "Enemy {}".format(self.turn_phase-1))
        log += "mana: {}/{}\n".format(self.mana, self.game_state.max_mana)
        log += str(self.player) + '\n'
        log += '\n'.join('{}:{}---{}'.format(i, enemy, enemy.get_intention(self.game_state, self)) for i, enemy in enumerate(self.enemies)) + '\n'
        log += "exhaust pile: "
        log += ' '.join(['{}:{}'.format(i, card.get_name()) for i, card in enumerate(self.exhaust_pile)]) + '\n'
        log += "discard pile: "
        log += ' '.join(['{}:{}'.format(i, card.get_name()) for i, card in enumerate(self.discard_pile)]) + '\n'
        log += "draw pile: "
        sorted_draw: list[Card] = sorted(self.draw_pile, key=lambda card: repr(card))
        log += ' '.join('{}:{}'.format(i, card.get_name()) for i, card in enumerate(sorted_draw)) + '\n'
        log += "hand: "
        log += ' '.join(['{}:{}'.format(i, card.get_name()) for i, card in enumerate(self.hand)]) + '\n'
        self.log(log)

    def end_agent_turn(self):
        self.agent_turn_ended = True
    
    def add_to_mana(self, amount: int):
        self.mana += amount
        if self.mana > MAX_MANA:
            self.mana = MAX_MANA
        assert self.mana >= 0, "Mana value cannot be negative"

    def _step_agent(self, agent: Agent) -> bool:
        if agent.is_dead() or self.ended() or self.agent_turn_ended:
            return False
        self.visualize()
        agent.play(self.game_state, self)
        assert agent.prev_action is not None, "Action taken is not recorded for agent {}".format(agent.name)
        self.log(str(agent.prev_action) + '\n')
        return True

    def _take_agent_turn(self, agent: Agent):
        self.agent_turn_ended = False
        while self._step_agent(agent):
            self.enemies: list[Enemy] = [enemy for enemy in self.enemies if not enemy.is_dead()]
        self.turn_phase += 1
    
    def _play_side(self, side: list[Agent], other_side: list[Agent]):
        for agent in side:
            self._take_agent_turn(agent)
        for agent in side:
            agent.decrease_status()
        for agent in other_side:
            agent.clear_block()

    def take_turn(self):
        self.mana = self.game_state.max_mana
        self.turn += 1
        self.turn_phase = 0
        self.draw_hand()
        self._play_side([self.player], [enemy for enemy in self.enemies])
        self._play_side([enemy for enemy in self.enemies], [self.player])
        self.discard_hand()

    def tick_player(self, action: Action) -> bool:
        if self.ended():
            return False
        action.play(self.player, self.game_state, self)
        self.enemies: list[Enemy] = [enemy for enemy in self.enemies if not enemy.is_dead()]
        if not self.agent_turn_ended:
            return True
        self.turn_phase += 1
        self.player.decrease_status()
        for enemy in self.enemies:
            enemy.clear_block()
        self._play_side([enemy for enemy in self.enemies], [self.player])
        self.discard_hand()
        self.mana = self.game_state.max_mana
        self.turn += 1
        self.turn_phase = 0
        self.draw_hand()
        self.agent_turn_ended = False
        return True
        
    def ended(self):
        return self.get_end_result() != 0
    
    def get_end_result(self):
        if self.player.is_dead():
            return -1
        for enemy in self.enemies:
            if not enemy.is_dead():
                return 0
        return 1
    
    def initiate_log(self):
        if self.verbose == Verbose.LOG and self.log_filename is not None:
            self.log_filename = get_unique_filename(self.log_filename, 'log')
        self.log(f'version {1.0}\n')
        for card in self.game_state.deck:
            self.log(f'{card}\n')
    
    def run(self):
        self.initiate_log()
        while not self.ended():
            self.take_turn()
        self.player.clean_up()
        self.log("WIN" if self.get_end_result() == 1 else "LOSE")