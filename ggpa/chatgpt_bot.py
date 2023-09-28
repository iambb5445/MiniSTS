from __future__ import annotations
import openai
import time
from ggpa.ggpa import GGPA
from action.action import EndAgentTurn, PlayCard
from enum import StrEnum
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game import GameState
    from battle import BattleState
    from agent import Agent
    from card import Card
    from action.action import Action

class ChatGPTBot(GGPA):
    class ModelName(StrEnum):
        GPT_4 = "gpt-4"
        GPT_Turbo_35 = "gpt-3.5-turbo"
        Instruct_Davinci = "text-davinci-003"
        Instruct_GPT_Turbo_35 = "gpt-3.5-turbo-instruct"

    CHAT_MODELS = [ModelName.GPT_4, ModelName.GPT_Turbo_35]
    COMPLETION_MODELS = [ModelName.Instruct_GPT_Turbo_35, ModelName.Instruct_Davinci]

    def ask_gpt(self) -> str:
        if self.model_name == ChatGPTBot.ModelName.GPT_4:
            time.sleep(0.5) # prevent rate limit
        if self.model_name in ChatGPTBot.CHAT_MODELS:
            response_all = openai.ChatCompletion.create(
                    model=self.model_name,
                    messages=self.messages,
                    request_timeout=15,
                )
            assert isinstance(response_all, dict), "GPT response is not a dictionary"
            return response_all['choices'][0]['message']['content']
        elif self.model_name in ChatGPTBot.COMPLETION_MODELS:
            response_all = openai.Completion.create(
                    model=self.model_name,
                    prompt=self.translate_to_string_input(self.messages),
                    request_timeout=15,
                )
            assert isinstance(response_all, dict), "GPT response is not a dictionary"
            return response_all['choices'][0]['text']
        else:
            raise Exception(f"Model API type not recognized for {self.model_name}")

    # loosely adapted from https://github.com/adamkarvonen/chess_gpt_eval/blob/master/gpt_query.py
    def translate_to_string_input(self, openai_messages: list[dict[str, str]]):
        # Translate from OpenAI's dict to a single string input
        return "\n".join([message["content"] for message in openai_messages])

    API_KEY = '' # redacted

    def __init__(self, model_name: ChatGPTBot.ModelName):
        super().__init__("ChatGPT")
        self.model_name = model_name

    def get_agent_prompt(self, agent: Agent):
        return f'''
        * {agent.health} <HP> out of {agent.max_health}
        * {agent.block} <BLOCK>
        * The following <STATUS_EFFECT>s with their respective amounts: {agent.status_effects}
        '''
    
    def get_enemies_prompt(self, game_state: GameState, battle_state: BattleState):
        ret = ""
        for i, enemy in enumerate(battle_state.enemies):
            intention: Action = enemy.get_intention(game_state, battle_state)
            ret += f'''
            Enemy {i} is of type {enemy.name}. It has:
            {self.get_agent_prompt(enemy)}
            * It intends to do the following for next turn:
            {intention}
            '''
        return ret
    
    def get_card_prompt(self, card: Card):
        actions = "\n-".join([action.__repr__() for action in card.actions])
        return f'''
        * It's called {card.get_name()}
        * It has a cost of {card.mana_cost.peek()} <MANA>
        * It has a type of {card.card_type}
        * It does the following actions, when played:
        {actions}
        '''
    
    def get_pile_prompt(self, cards: list[Card]):
        ret = ""
        for i, card in enumerate(cards):
            ret += f'''
            Card {i} has the following properties:
            {self.get_card_prompt(card)}
            '''
        return ret

    # TODO add __repr__ for actions
    # TODO remove status effects from prompt, or actually apply status effects
    # TODO fix future prediction in BT agents

    def get_options_prompt(self, options: list[PlayCard|EndAgentTurn]):
        ret = ""
        for i, option in enumerate(options):
            ret += f"Option {i}: {option.__repr__()}\n"
        return ret

    def choose_card(self, game_state: GameState, battle_state: BattleState) -> EndAgentTurn|PlayCard:
        print(battle_state.turn, game_state.player.health)
        options = self.get_choose_card_options(game_state, battle_state)
        status_effects_definition = '''
        Every <STATUS_EFFECT> have a value.
        Every <STATUS_EFFECT> have a rule on how its value changes at the end of the turn.
        Every <STATUS_EFFECT> have a rule of how its value stacks if the same status is applied multiple times on the same creature.
        - <VULNERABLE>: Take 50% more damage from attacks. At the end of turn, the value decreases until it reaches zero, at which point it's removed. It stacks by adding up.
        - <WEAK>: Deal 25% less attack damage. At the end of turn, the value decreases until it reaches zero, at which point it's removed. It stacks by adding up.
        - <ENTANGLE>: Target cannot play any attacks. At the end of turn, it's removed. It does not stack.
        - <STRENGTH>: Deal X more attack damage, where X is the value of this <STATUS_EFFECT>. At the end of turn, nothing happens. It stacks by adding up.
        '''
        sorted_draw_pile: list[Card] = [card for card in battle_state.draw_pile] # TODO sort
        prompt = f'''
        In this game, the player have a deck of cards.
        The cards are intially put in your <DRAW_PILE>. The game is played in a number of turns.
        Every turn:
        - Your mana is set to {game_state.max_mana}.
        - You draw a set of {5} cards from your <DRAW_PILE> into your <HAND>. If your <DRAW_PILE> doesn't have enough cards, you draw as much as you can, then you shuffle all the cards from your <DISCARD_PILE> into your <DRAW_PILE>. Then, you draw the remaing number of cards from your <DRAW_PILE> into your <HAND>.
        - You play as many cards as you want as long as you have enough <MANA> to play them. Then you end your turn.
        - When you end your turn, all the remainig cards in your <HAND> move to your <DISCARD_PILE>
        - After you end your turn, all your <STATUS_EFFECT>s change.
        - Your enemies lose any remaining <BLOCK>.
        - Your enemies one by one do their intended action.
        - Your enemies one by one have their <STATUS_EFFECT>s change.
        - You lose any remaining <BLOCK>.
        The <STATUS_EFFECTS> in game are defined as follows:
        {status_effects_definition}
        When any creature gets attacked, first it loses <BLOCK>. Whatever damage is left, it loses as <HP>.
        Any creature that reaches the <HP> of zero or less, is removed from the game.
        If you are removed from the game, you lose the game.
        If all the enemies are removed from the game, you win the game.
        To "Exhaust" a card means that the cards will move to your <EXHAUST_PILE> and will not be playable anymore in this game. It will not enter the <DRAW_PILE> again, meaning that you won't see it in your hand in this game.
        Right now, the game is in turn {battle_state.turn}, and it's time for your to play.
        You have {battle_state.mana} <MANA> out of the {game_state.max_mana} <MANA> that you get every turn.
        You have:
        {self.get_agent_prompt(battle_state.player)}
        Your enemies are:
        {self.get_enemies_prompt(game_state, battle_state)}
        You have the following cards in your <EXHAUST_PILE>:
        {self.get_pile_prompt(battle_state.exhaust_pile)}
        You have the following cards in your <DISCARD_PILE>:
        {self.get_pile_prompt(battle_state.discard_pile)}
        You have the following cards in your <DRAW_PILE>, but in an unknown order:
        {self.get_pile_prompt(sorted_draw_pile)}
        You have the following cards in your <HAND>:
        {self.get_pile_prompt(battle_state.hand)}
        This turn, you can do one of the following (your <OPIONS>):
        {self.get_options_prompt(options)}
        Answer this:
        In the first line, give the number of the action you want to take. It should be one of the provided <OPIONS>.
        It should be in range 0-{len(options)-1}. Only print this number in line 1, and nothing else.
        After that, starting at the second line, give the explanation of why you have chosen this option.
        '''
        #print('----------------------prompt---------------------')
        #print(prompt)
        openai.api_key = self.API_KEY
        self.messages = [
            {"role": "system", "content": "You are a bot specialized in playing a card game."},
            {"role": "user", "content": prompt},
        ]
        while True:
            try:
                response: str = self.ask_gpt()
            except Exception as e:
                print(e)
                continue
            try:
                value = int(response.split()[0])
                if value >= 0 and value < len(options):
                    break
            except Exception:
                continue
        self.messages.append({
            "role": "assistant",
            "content": response
        })
        return options[value]
    
    def choose_agent_target(self, battle_state: BattleState, list_name: str, agent_list: list[Agent]) -> Agent:
        enemies_options = battle_state.enemies
        options_prompt = ''
        for i, agent in enumerate(agent_list):
            options_prompt += f'{i}:Enemy-{enemies_options.index(agent)}\n' if agent in enemies_options else f'{i}:Player'
        self.messages.append(
            {
            "role": "user",
            "content": f'''On which one of the targets among {list_name} you want to apply this?
            The valid options are: (provided in <index>:<option> format)
            {options_prompt}Give a single number in the first line, indicating the <index> of the target.
            In the second line, give your explanation.
            '''
            })
        while True:
            try:
                response: str = self.ask_gpt()
            except Exception as e:
                print(e)
                continue
            try:
                value = int(response.split()[0])
                if value >= 0 and value < len(agent_list):
                    break
            except Exception:
                continue
        self.messages.append({
            "role": "assistant",
            "content": response
        })
        return agent_list[value]
    
    def choose_card_target(self, battle_state: BattleState, list_name: str, card_list: list[Card]) -> Card:
        self.messages.append(
            {
            "role": "user",
            "content": f'''On which card target you want to apply this? These are your options: {self.get_pile_prompt(card_list)}
            Give a single number in the first line, indicating the answer.
            In the second line, give your explanation.
            '''
            })
        while True:
            try:
                response: str = self.ask_gpt()
            except Exception as e:
                print(e)
                continue
            try:
                value = int(response.split()[0])
                if value >= 0 and value < len(card_list):
                    break
            except Exception:
                continue
        self.messages.append({
            "role": "assistant",
            "content": response
        })
        return card_list[value]
    