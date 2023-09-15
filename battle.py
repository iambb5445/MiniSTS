from __future__ import annotations
import copy
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from agent import Enemy, Agent
    from game import GameState
    from card import Card
    from action.action import Action
from config import MAX_MANA, Verbose

import random

class BattleSt:
    def __init__(self, sides: tuple[list[Agent], list[Agent]]):
        self.turn = 0
        self.sides = sides
    
    def visualise(self, verbose: Verbose):
        pass

    def take_action(self, action: Action):
        pass#action.play()

class BattleState:
    def __init__(self, game_state: GameState, *enemies: Enemy):
        self.player = game_state.player
        self.enemies = [enemy for enemy in enemies]
        self.game_state = game_state
        self.turn = 0
        self.mana = 0
        self.agent_turn_ended = False
        self.turn_phase = 0
        self.draw_pile: list[Card] = [copy.deepcopy(card) for card in self.game_state.deck]
        random.shuffle(self.draw_pile)
        self.discard_pile: list[Card] = []
        self.hand: list[Card] = []
        self.exhaust_pile: list[Card] = []

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
        print('Playing:\n{}'.format(card))
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
    
    def visualize(self, verbose: Verbose):
        if verbose == Verbose.NO_LOG:
            return
        print("*Turn {} - {}*".format(self.turn, "Player" if self.turn_phase == 0 else "Enemy {}".format(self.turn_phase-1)))
        print("mana: {}/{}".format(self.mana, self.game_state.max_mana))
        print(self.player)
        for i, enemy in enumerate(self.enemies):
            intention: Action = enemy.get_intention(self.game_state, self)
            print('{}:{}---{}'.format(i, enemy, intention))
        print("exhaust pile: ", end=' ')
        for i, card in enumerate(self.exhaust_pile):
            print('{}:{}'.format(i, card.get_name()), end=' ')
        print("\ndiscard pile: ", end=' ')
        for i, card in enumerate(self.discard_pile):
            print('{}:{}'.format(i, card.get_name()), end=' ')
        print("\ndraw pile: ", end=' ')
        for i, card in enumerate(self.draw_pile):
            print('{}:{}'.format(i, card.get_name()), end=' ')
        print("\nhand: ", end=' ')
        for i, card in enumerate(self.hand):
            print('{}:{}'.format(i, card.get_name()), end=' ')
        print()

    def end_agent_turn(self):
        self.agent_turn_ended = True
    
    def add_to_mana(self, amount: int):
        self.mana += amount
        if self.mana > MAX_MANA:
            self.mana = MAX_MANA
        assert self.mana >= 0, "Mana value cannot be negative"

    def _take_agent_turn(self, agent: Agent, verbose: Verbose):
        self.agent_turn_ended = False
        while self.step_agent(agent, verbose):
            self.enemies: list[Enemy] = [enemy for enemy in self.enemies if not enemy.is_dead()]
        self.turn_phase += 1

    def step_agent(self, agent: Agent, verbose: Verbose):
        if agent.is_dead() or self.ended() or self.agent_turn_ended:
            return False
        self.visualize(verbose)
        agent.play(self.game_state, self)
        return True
    
    def _play_side(self, side: list[Agent], other_side: list[Agent], verbose: Verbose):
        for agent in side:
            self._take_agent_turn(agent, verbose)
        for agent in side:
            agent.clear_status()
        for agent in other_side:
            agent.clear_block()

    def take_turn(self, verbose: Verbose):
        self.mana = self.game_state.max_mana
        self.turn += 1
        self.turn_phase = 0
        self.draw_hand()
        sides: tuple[list[Agent], list[Agent]] = ([self.player], [enemy for enemy in self.enemies])
        self._play_side(sides[0], sides[1], verbose)
        self._play_side(sides[1], sides[0], verbose)
        self.discard_hand()
        
    def ended(self):
        return self.get_end_result() != 0
    
    def get_end_result(self):
        if self.player.is_dead():
            return -1
        for enemy in self.enemies:
            if not enemy.is_dead():
                return 0
        return 1

    def run(self, verbose: Verbose):
        while not self.ended():
            self.take_turn(verbose)
        if self.get_end_result() == 1:
            print("WIN")
        else:
            print("LOSE")