from __future__ import annotations
import openai
import time
from ggpa.ggpa import GGPA
from action.action import EndAgentTurn, PlayCard
from enum import StrEnum
from auth import GPT_AUTH
from ggpa.prompt import get_action_prompt, get_agent_target_prompt, get_card_target_prompt
from typing import TYPE_CHECKING, Callable
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

    def get_request(self):
        if self.model_name in ChatGPTBot.CHAT_MODELS:
            return {
                'model': self.model_name,
                'messages': self.messages,
                'request_timeout': 15,
            }
        elif self.model_name in ChatGPTBot.COMPLETION_MODELS:
            return {
                'model': self.model_name,
                'prompt': self.translate_to_string_input(self.messages),
                'request_timeout': 15,
            }
        else:
            raise Exception(f"Model API type not recognized for {self.model_name}")
    
    def ask_gpt(self) -> str:
        if self.model_name == ChatGPTBot.ModelName.GPT_4:
            time.sleep(0.5) # prevent rate limit
        request = self.get_request()
        if self.model_name in ChatGPTBot.CHAT_MODELS:
            response = openai.ChatCompletion.create(**request)
            self.history.append({'request': request, 'response': response})
            return response['choices'][0]['message']['content']
        elif self.model_name in ChatGPTBot.COMPLETION_MODELS:
            response = openai.Completion.create(**request)
            self.history.append({'request': request, 'response': response})
            return response['choices'][0]['text']
        else:
            raise Exception(f"Model API type not recognized for {self.model_name}")

    # loosely adapted from https://github.com/adamkarvonen/chess_gpt_eval/blob/master/gpt_query.py
    def translate_to_string_input(self, openai_messages: list[dict[str, str]]):
        # Translate from OpenAI's dict to a single string input
        return "\n".join([message["content"] for message in openai_messages])

    API_KEY = GPT_AUTH # redacted

    def __init__(self, model_name: ChatGPTBot.ModelName):
        super().__init__("ChatGPT")
        self.model_name = model_name
        self.history = []

    def get_integer_response(self, min: int, max: int) -> int:
        while True:
            try:
                response: str = self.ask_gpt()
            except Exception as e:
                print(e)
                continue
            try:
                value = int(response.split()[0])
                if value >= min and value <= max:
                    break
            except Exception as e:
                print(f"Wrong format: {response}")
                continue
            print(f'Wrong range: {response}')
        self.messages.append({"role": "assistant", "content": response})
        return value

    def choose_card(self, game_state: GameState, battle_state: BattleState) -> EndAgentTurn|PlayCard:
        options = self.get_choose_card_options(game_state, battle_state)
        prompt = get_action_prompt(game_state, battle_state, options)
        openai.api_key = self.API_KEY
        self.messages = [
            {"role": "system", "content": "You are a bot specialized in playing a card game."},
            {"role": "user", "content": prompt},
        ]
        value = self.get_integer_response(0, len(options)-1)
        return options[value]
    
    def choose_agent_target(self, battle_state: BattleState, list_name: str, agent_list: list[Agent]) -> Agent:
        prompt = get_agent_target_prompt(battle_state, list_name, agent_list)
        self.messages.append({"role": "user", "content": prompt})
        value = self.get_integer_response(0, len(agent_list)-1)
        return agent_list[value]
    
    def choose_card_target(self, battle_state: BattleState, list_name: str, card_list: list[Card]) -> Card:
        prompt = get_card_target_prompt(battle_state, list_name, card_list)
        self.messages.append({"role": "user", "content": prompt})
        value = self.get_integer_response(0, len(card_list)-1)
        return card_list[value]
    