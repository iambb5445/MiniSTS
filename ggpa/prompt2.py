from __future__ import annotations
from enum import Enum
from config import Verbose
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game import GameState
    from battle import BattleState
    from action.action import PlayCard, EndAgentTurn
    from agent import Agent
    from card import Card

# TODO connect this
class PromptOption(Enum):
    NONE = 0
    CoT_rev = 1
    CoT = 2
    DAG = 3

def get_action_prompt(game_state: GameState, battle_state: BattleState, options: list[PlayCard|EndAgentTurn], prompt_option: PromptOption, get_context: bool, show_option_results: bool):
    state = _get_game_state(game_state, battle_state, options, show_option_results)
    request = _get_action_request(options, prompt_option)
    if get_context:
        context = _get_game_context(game_state, battle_state, options)
        return f'{context}\n{state}\n{request}'
    return f'{state}\n{request}'

def _get_game_context(game_state: GameState, battle_state: BattleState, options: list[PlayCard|EndAgentTurn]):
    nl = '\n'
    deck: dict[str, tuple[Card, int]] = {}
    for card in battle_state.exhaust_pile + battle_state.discard_pile + battle_state.draw_pile + battle_state.hand:
        name: str = card.get_name()
        if name not in deck:
            deck[name] = (card, 0)
        deck[name] = (deck[name][0], deck[name][1] + 1)
    return \
f'''In this game, the player have a deck of cards. The game is played in a number of turns.
Every turn, in this exact order:
- Your mana is set to {game_state.max_mana}.
- You draw a set of {game_state.draw_count} cards from your <DRAW_PILE> into your <HAND>. If your <DRAW_PILE> doesn't have enough cards, you draw as much as you can, then you shuffle all the cards from your <DISCARD_PILE> into your <DRAW_PILE>. Then, you draw the remaing number of cards from your <DRAW_PILE> into your <HAND>.
- You play as many cards as you want as long as you have enough <MANA> to play them. Then you end your turn.
- When you end your turn, all the remainig cards in your <HAND> move to your <DISCARD_PILE>. You will draw new cards next turn.
- When you end your turn, Your enemies one by one do their intended action (this is shown for each enemy as "intention"). Note that the intention of an enemy will be affected by its status effects. For example, if an enemy intends to attack for 3, but has 4 <STRENGTH>s, it will deal 7 damage.
When any creature gets attacked, first it loses <BLOCK>. Whatever damage is left, it loses as <HP>. Any block lasts only for one turn.
Any creature that reaches an <HP> of zero or less, is removed from the game.
The <STATUS_EFFECTS> in the game are defined as follows:
Every <STATUS_EFFECT> has a value x. The value of a <STATUS_EFFECT> can stack, meaning that if applied multiple times on the same target, their x values are added together.
- <VULNERABLE>: Take 50% more damage from attacks for x turns.
- <WEAK>: Deal 25% less attack damage for x turns.
- <STRENGTH>: Deal x more attack damage. It affects multi-attacks multiple times.
- <VIGOR>: Deal x more attack damage only on the next attack card you play (this turn or after). It affects multi-attacks multiple times.
- <BOMB>: Deal 40 damage to all enemies after x turns.
- <TOLERANCE>: Gain X block at the end of your turn. Increase X by 2.
If your character is removed from the game, you lose the game.
If all the enemies are removed from the game, you win the game.
Your goal is to win the game with as much remaining health as possible.
To "Exhaust" a card means that the cards will move to your <EXHAUST_PILE> and will not be playable for the rest of the game.
You started with the following cards in your deck:
{nl.join([f'{count} of card <name: {card.name}, mana cost:{card.mana_cost.peek()}, type:{card.card_type}{nl}' +
          f'description: {card.get_description()}>' for card, count in deck.values()])}'''

def _get_game_state(game_state: GameState, battle_state: BattleState, options: list[PlayCard|EndAgentTurn], show_option_results: bool):
    player = battle_state.player
    nl = '\n'
    deck: dict[str, tuple[Card, int]] = {}
    for card in battle_state.exhaust_pile + battle_state.discard_pile + battle_state.draw_pile + battle_state.hand:
        name: str = card.get_name()
        if name not in deck:
            deck[name] = (card, 0)
        deck[name] = (deck[name][0], deck[name][1] + 1)
    return \
f'''Right now, the game is in turn {battle_state.turn}, and it's time for you to play.
You have {battle_state.mana} <MANA> out of the {game_state.max_mana} <MANA> that you get every turn.
You have:
hp:{player.health}/{player.max_health}, block:{player.block}, status effects:{repr(player.status_effect_state)}
Your enemies are:
{nl.join([f'{i}: hp:{enemy.health}/{enemy.max_health}, block:{enemy.block}, status effects:{repr(enemy.status_effect_state)}, intention: {enemy.get_intention(game_state, battle_state)}' for i, enemy in enumerate(battle_state.enemies)])}
You have the following cards in your <EXHAUST_PILE>:
{'-empty-' if len(battle_state.exhaust_pile) == 0 else
  ' '.join([f'{i}: {card.get_name()}' for i, card in enumerate(battle_state.exhaust_pile)])}
You have the following cards in your <DISCARD_PILE>:
{'-empty-' if len(battle_state.discard_pile) == 0 else
 ' '.join([f'{i}: {card.get_name()}' for i, card in enumerate(battle_state.discard_pile)])}
You have the following cards in your <DRAW_PILE>, but in an unknown order:
{'-empty-' if len(battle_state.draw_pile) == 0 else
 ' '.join([f'{i}: {card.get_name()}' for i, card in enumerate(battle_state.draw_pile)])}
You have the following cards in your <HAND>:
{'-empty-' if len(battle_state.hand) == 0 else
 ' '.join([f'{i}: {card.get_name()}' for i, card in enumerate(battle_state.hand)])}
This turn, you can do one of the following (your <OPIONS>):
{nl.join([f'{i}: {option}{(nl + get_option_result(game_state, battle_state, option)) if show_option_results else ""}' for i, option in enumerate(options)])}'''

def get_option_result(game_state: GameState, battle_state: BattleState, option: PlayCard|EndAgentTurn):
    battle_state = battle_state.copy_undeterministic()
    battle_state.verbose = Verbose.NO_LOG
    battle_state.tick_player(option)
    game_state = battle_state.game_state
    nl = '\n*** '
    player = battle_state.player
    return \
f'''*** Choosing this option results in a state in which you have {battle_state.mana} <MANA> remaining, and:
*** hp:{player.health}/{player.max_health}, block:{player.block}, status effects:{repr(player.status_effect_state)}
*** And you're enemies will be:
*** {'*** None (no enemy survives)' if len(battle_state.enemies) == 0 else
 nl.join([f'{i}: hp:{enemy.health}/{enemy.max_health}, block:{enemy.block}, status effects:{repr(enemy.status_effect_state)}, intention: {enemy.get_intention(game_state, battle_state)}' for i, enemy in enumerate(battle_state.enemies)])}'''

def _get_action_request(options: list[PlayCard|EndAgentTurn], prompt_option: PromptOption):
    if prompt_option == PromptOption.NONE:
        return \
f'''Answer this:
In a single line, write only the index of the option you want to take. It should be one of the provided <OPIONS>.
It should be in range 0-{len(options)-1}. Only print this number in line 1, and nothing else.'''
    elif prompt_option == PromptOption.CoT_rev:
        return \
f'''Answer this:
In the first line, write only the index of the option you want to take. It should be one of the provided <OPIONS>.
It should be in range 0-{len(options)-1}. Only print this number in line 1, and nothing else.
After that, starting at the second line, give the explanation of why you have chosen this option.'''
    elif prompt_option == PromptOption.CoT:
        return \
f'''Answer this:
In the first paragraph, give the explanation of which option you think is best.
After that, starting at the second paragraph, write only the index of the option you want to take. It should be one of the provided <OPIONS>.
It should be in range 0-{len(options)-1}. Only print this number in a single line for the second paragraph, and nothing else.'''
    elif prompt_option == PromptOption.DAG:
        return \
f'''Answer this:
Let's think about the possible strategies based on your deck. Considering the cost and effect of your card, let's find which cards are better to use in general, or if there are any synergies between your cards.
A synergy between a set of cards is when the cards are better when they are used together. Of course, we don't want to use two cards just because they affect each other, but we want to see if there are any specifically powerful card/cards that we can use.
In the first paragraph, list up to 3 strategies for the rest of the game based on your deck.
In the second paragraph, rank these strategies. Write which one of these strategies you want to use now based on the avaialble cards, resources, and overal state of the game.
In the third paragraph, tell us what would be your move between the provided <OPTIONS> based on your target strategy.
Finally, in the last line, write only the index of the option you want to take. It should be one of the provided <OPIONS>.
It should be in range 0-{len(options)-1}. Only print this number in a single line for the final line, and nothing else.'''
    else:
        raise Exception(f"Unrecognized prompt option: {prompt_option}")
    
def strip_response(response: str, prompt_option: PromptOption) -> str:
    response = ''.join(c if c not in '.-' else ' ' for c in response) # remove - or . to be more inclusive
    if len(response) == 0:
        return ''
    lines = response.split() #new line or any space (instead of new line only) to include more responses
    lines = [line for line in lines if len(line) > 0]
    if prompt_option in [PromptOption.CoT, PromptOption.DAG, PromptOption.NONE]:
        return lines[-1]
    elif prompt_option in [PromptOption.CoT_rev]:
        return lines[0]
    else:
        raise Exception(f"Unrecognized prompt option: {prompt_option}")

def get_agent_target_prompt(battle_state: BattleState, list_name: str, options: list[Agent]):
    nl = '\n'
    def get_agent_name(agent: Agent):
        if agent in battle_state.enemies:
            return f'Enemy-{battle_state.enemies.index(agent)}'
        elif agent == battle_state.player:
            return 'Player'
        else:
            raise Exception(f'Cannot find agent: {agent.name}-{agent}')
    return \
f'''On which one of the targets among {list_name} you want to apply this?
The valid options are: (provided in <index>:<option> format)
{nl.join([f'{i}: {get_agent_name(agent)}' for i, agent in enumerate(options)])}
Respond with a single number in a single line, indicating the <index> of the target. Do not add anything other than this one number.'''

def get_card_target_prompt(battle_state: BattleState, list_name: str, options: list[Card]):
    nl = '\n'
    return \
f'''On which one of the cards among {list_name} you want to apply this?
The valid options are: (provided in <index>:<option> format)
{nl.join([f'{i}: name:{card.get_name()}, cost:{card.mana_cost.peek()}, type:{card.card_type}{nl}' +
          f'description: {card.get_description}' for i, card in enumerate(options)])}
Respond with a single number in a single line, indicating the <index> of the target. Do not add anything other than this one number.'''