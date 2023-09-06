from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from agent import Enemy
    from game import GameState
    from card import Card
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

    def _start(self):
        self.draw_pile: list[Card] = [card for card in self.game_state.deck]
        random.shuffle(self.draw_pile)
        self.discard_pile: list[Card] = []
        self.hand: list[Card] = []

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
            pass
            #discard+draw+hand is empty

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
    
    def visualize(self):
        print("*Turn {}*".format(self.turn))
        print("mana: {}/{}".format(self.mana, self.game_state.max_mana))
        print(self.player)
        for i, enemy in enumerate(self.enemies):
            print('{}:{}'.format(i, enemy))
        print("discard pile: ", end=' ')
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
        self.draw_hand()
        for agent in self.enemies + [self.player]:
            agent.clear()
        self.player_turn_ended = False
        while not self.player_turn_ended:
            self.visualize()
            self.player.play(self.game_state, self)
            # TODO mana
        self.discard_hand()
        for enemy in self.enemies:
            self.visualize()
            enemy.play(self.game_state, self)

    def run(self):
        while(True):
            self.take_turn()