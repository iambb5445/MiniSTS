from __future__ import annotations
from enum import Enum
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

def get_action_prompt(game_state: GameState, battle_state: BattleState, options: list[PlayCard|EndAgentTurn], prompt_option: PromptOption):
    state = _get_game_state(game_state, battle_state, options)
    request = _get_action_request(options, prompt_option)
    return f'{state}\n{request}'

def _get_game_state(game_state: GameState, battle_state: BattleState, options: list[PlayCard|EndAgentTurn]):
    player = battle_state.player
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
- When you end your turn, Your enemies one by one do their intended action.
When any creature gets attacked, first it loses <BLOCK>. Whatever damage is left, it loses as <HP>. Any block lasts only for one turn.
Any creature that reaches an <HP> of zero or less, is removed from the game.
The <STATUS_EFFECTS> in the game are defined as follows:
Every <STATUS_EFFECT> has a value x. The value of a <STATUS_EFFECT> can stack, meaning that if applied multiple times on the same target, their x values are added together.
- <VULNERABLE>: Take 50% more damage from attacks for x turns.
- <WEAK>: Deal 25% less attack damage for x turns.
- <STRENGTH>: Deal x more attack damage.
- <VIGOR>: Deal x more attack damage only on the next attack card you play (this turn or after).
If your character is removed from the game, you lose the game.
If all the enemies are removed from the game, you win the game.
To "Exhaust" a card means that the cards will move to your <EXHAUST_PILE> and will not be playable for the rest of the game.
Right now, the game is in turn {battle_state.turn}, and it's time for you to play.
You have the following cards in your deck:
{nl.join([f'{count} of card <name: {card.name}, mana cost:{card.mana_cost.peek()}, type:{card.card_type}{nl}' +
          f'description: {" ".join([f"{action}" for action in card.actions])}' for card, count in deck.values()])}
You have {battle_state.mana} <MANA> out of the {game_state.max_mana} <MANA> that you get every turn.
You have:
hp:{player.health}/{player.max_health}, block:{player.block}, status effects:{player.status_effects}
Your enemies are:
{nl.join([f'{i}: hp:{enemy.health}/{enemy.max_health}, block:{enemy.block}, status effects:{enemy.status_effects}' for i, enemy in enumerate(battle_state.enemies)])}
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
{nl.join([f'{i}: {option}' for i, option in enumerate(options)])}'''

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
In the first paragraph, think of the possible synergies based on your deck. A synergy between a set of cards is when the cards are better when they are used together. Also consdier which one of these synergies are useful or critical in this scenario based on their effect and their cost. For example, a synergy of cost 2 which results in 20 damage is much better than a synergy of cost 2 but only 10 damage. List up to 3 strategies for the rest of the game based on your deck and these synergies.
In the second paragraph, write which one of these strategies you want to use based on the avaialble cards, resources, and overal state of the game.
In the third paragraph, tell us what would be your move between the provided <OPTIONS> based on your target strategy.
Finally, in the last line, write only the index of the option you want to take. It should be one of the provided <OPIONS>.
It should be in range 0-{len(options)-1}. Only print this number in a single line for the final line, and nothing else.'''
    else:
        raise Exception(f"Unrecognized prompt option: {prompt_option}")
    
def strip_response(response: str, prompt_option: PromptOption) -> str:
    response = ''.join(c if c not in '.-' else ' ' for c in response) # remove - or . to be more inclusive
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
          f'description: {" ".join([f"{action}" for action in card.actions])}' for i, card in enumerate(options)])}
Respond with a single number in a single line, indicating the <index> of the target. Do not add anything other than this one number.'''