from __future__ import annotations
import copy
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from agent import Enemy
    from game import GameState
    from card import Card
    from action.action import Action
from config import MAX_MANA

import random

class BattleState:
    def __init__(self, game_state: GameState, *enemies: Enemy):
        self.player = game_state.player
        self.enemies = [enemy for enemy in enemies]
        self.game_state = game_state
        self.turn = 0
        self.mana = 0
        self._start()
        self.player_turn_ended = False
        self.turn_phase = 0

    def _start(self):
        self.draw_pile: list[Card] = [copy.deepcopy(card) for card in self.game_state.deck]
        random.shuffle(self.draw_pile)
        self.discard_pile: list[Card] = []
        self.hand: list[Card] = []
        self.exhause_pile: list[Card] = []

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

    def discard(self, card_index: int):
        assert card_index < len(self.hand) and card_index >= 0, "Card index {} out of range for hand {}".format(card_index, self.hand)
        discarded = self.hand.pop(card_index)
        self.discard_pile.append(discarded)
    
    def exhaust(self, card: Card):
        if card in self.hand:
            self.hand.remove(card)
        if card in self.draw_pile:
            self.draw_pile.remove(card)
        if card in self.discard_pile:
            self.discard_pile.remove(card)
        self.exhause_pile.append(card)
    
    def visualize(self):
        print("*Turn {} - {}*".format(self.turn, "Player" if self.turn_phase == 0 else "Enemy {}".format(self.turn_phase-1)))
        print("mana: {}/{}".format(self.mana, self.game_state.max_mana))
        print(self.player)
        for i, enemy in enumerate(self.enemies):
            intention: Action = enemy.get_intention(self.game_state, self)
            print('{}:{}---{}'.format(i, enemy, intention))
        print("exhaust pile: ", end=' ')
        for i, card in enumerate(self.exhause_pile):
            print('{}:{}'.format(i, card.name), end=' ')
        print("\ndiscard pile: ", end=' ')
        for i, card in enumerate(self.discard_pile):
            print('{}:{}'.format(i, card.name), end=' ')
        print("\ndraw pile: ", end=' ')
        for i, card in enumerate(self.draw_pile):
            print('{}:{}'.format(i, card.name), end=' ')
        print("\nhand: ", end=' ')
        for i, card in enumerate(self.hand):
            print('{}:{}'.format(i, card.name), end=' ')
        print()

    def end_player_turn(self):
        self.player_turn_ended = True
    
    def add_to_mana(self, amount: int):
        self.mana += amount
        if self.mana > MAX_MANA:
            self.mana = MAX_MANA
        assert self.mana >= 0, "Mana value cannot be negative"

    def is_playable(self, card: Card) -> bool:
        return card.mana_cost.get() <= self.mana
    
    def take_turn(self):
        self.mana = self.game_state.max_mana
        self.turn += 1
        self.turn_phase = 0
        self.draw_hand()
        self.player_turn_ended = False
        while not self.player_turn_ended:
            self.visualize()
            self.player.play(self.game_state, self)
            self.enemies: list[Enemy] = [enemy for enemy in self.enemies if not enemy.is_dead()]
            if self.get_end_result() != 0:
                return
        self.player.clear_status()
        for enemy in self.enemies:
            enemy.clear_block()
        self.discard_hand()
        for enemy in self.enemies:
            self.turn_phase += 1
            if not enemy.is_dead():
                self.visualize()
                enemy.play(self.game_state, self)
                if self.get_end_result() != 0:
                    return
        self.player.clear_block()
        for enemy in self.enemies:
            enemy.clear_status()
        self.enemies = [enemy for enemy in self.enemies if not enemy.is_dead()]
        
    def get_end_result(self):
        if self.player.is_dead():
            return -1
        for enemy in self.enemies:
            if not enemy.is_dead():
                return 0
        return 1

    def run(self):
        while self.get_end_result() == 0:
            self.take_turn()
        if self.get_end_result() == 1:
            print("WIN")
        else:
            print("LOSE")