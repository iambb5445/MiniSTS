from __future__ import annotations
import openai
import time
import json
from enum import StrEnum
from ggpa.ggpa import GGPA
from action.action import EndAgentTurn, PlayCard
from auth import GPT_AUTH
from utility import get_unique_filename
from ggpa.prompt2 import PromptOption, get_action_prompt,\
    get_agent_target_prompt, get_card_target_prompt,\
    strip_response
from typing import TYPE_CHECKING, Any
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
    
    call_timestamp: dict[ModelName, float] = {}
    token_count: dict[ModelName, int] = {}
    token_limit_per_minute = { #https://platform.openai.com/account/limits
        ModelName.GPT_4: 10000,
        ModelName.GPT_Turbo_35: 90000,
        ModelName.Instruct_Davinci: 250000,
        ModelName.Instruct_GPT_Turbo_35: 250000,
    }

    CHAT_MODELS = [ModelName.GPT_4, ModelName.GPT_Turbo_35]
    COMPLETION_MODELS = [ModelName.Instruct_GPT_Turbo_35, ModelName.Instruct_Davinci]

    # argmax
    # temp=0
    def get_request(self) -> dict[str, Any]:
        if self.model_name in ChatGPTBot.CHAT_MODELS:
            return {
                'model': self.model_name,
                'messages': self.messages,
                'request_timeout': 30,
            }
        elif self.model_name in ChatGPTBot.COMPLETION_MODELS:
            return {
                'model': self.model_name,
                'prompt': self.translate_to_string_input(self.messages),
                'request_timeout': 30,
            }
        else:
            raise Exception(f"Model API type not recognized for {self.model_name}")
    
    def ask_gpt(self) -> str:
        request = self.get_request()
        current = time.time()
        prev = ChatGPTBot.call_timestamp.get(self.model_name, current)
        est_tokens = len(request)/4
        if self.model_name not in ChatGPTBot.call_timestamp or\
            ChatGPTBot.token_count[self.model_name] + est_tokens > ChatGPTBot.token_limit_per_minute[self.model_name]:
            time.sleep(60 - (current - prev))
            ChatGPTBot.call_timestamp[self.model_name] = current
            ChatGPTBot.token_count[self.model_name] = 0
        # print(self.get_request())
        # exit()
        if self.model_name in ChatGPTBot.CHAT_MODELS:
            response = openai.ChatCompletion.create(**request)
            self.history.append({'request': request, 'response': response})
            ChatGPTBot.token_count[self.model_name] += int(response['usage']['total_tokens'])
            return response['choices'][0]['message']['content']
        elif self.model_name in ChatGPTBot.COMPLETION_MODELS:
            response = openai.Completion.create(**request)
            self.history.append({'request': request, 'response': response})
            ChatGPTBot.token_count[self.model_name] += int(response['usage']['total_tokens'])
            return response['choices'][0]['text']
        else:
            raise Exception(f"Model API type not recognized for {self.model_name}")

    # loosely adapted from https://github.com/adamkarvonen/chess_gpt_eval/blob/master/gpt_query.py
    def translate_to_string_input(self, openai_messages: list[dict[str, str]]):
        # Translate from OpenAI's dict to a single string input
        return "\n".join([message["content"] for message in openai_messages])

    API_KEY = GPT_AUTH # redacted

    def __init__(self, model_name: ChatGPTBot.ModelName, prompt_option: PromptOption):
        model_name_dict = {
            ChatGPTBot.ModelName.GPT_4: '4',
            ChatGPTBot.ModelName.GPT_Turbo_35: 't35',
            ChatGPTBot.ModelName.Instruct_GPT_Turbo_35: 'it35',
            ChatGPTBot.ModelName.Instruct_Davinci: 'idav',
        }
        prompt_dict = {
            PromptOption.NONE: 'none',
            PromptOption.CoT: 'cot',
            PromptOption.CoT_rev: 'cotr',
            PromptOption.DAG: 'dag',
        }
        super().__init__(f"ChatGPT-{model_name_dict[model_name]}-{prompt_dict[prompt_option]}")
        self.model_name = model_name
        self.prompt_option = prompt_option
        self.clear_history()

    def get_integer_response(self, min: int, max: int, prompt_option: PromptOption) -> int:
        if max == min:
            self.history.append({'auto-answer': str(min)})
            return min
        while True:
            try:
                response: str = self.ask_gpt()
            except Exception as e:
                print(e)
                continue
            try:
                value = int(strip_response(response, prompt_option))
                if value >= min and value <= max:
                    break
            except Exception as e:
                print(f"Wrong format for {self.name}, option {prompt_option}:\n*{response}*\nExtracted: *{strip_response(response, prompt_option)}*")
                continue
            print(f'Wrong range for {self.name}: *{response}*\nValue: {value}')
        self.messages.append({"role": "assistant", "content": response})
        return value

    def choose_card(self, game_state: GameState, battle_state: BattleState) -> EndAgentTurn|PlayCard:
        options = self.get_choose_card_options(game_state, battle_state)
        prompt = get_action_prompt(game_state, battle_state, options, self.prompt_option)
        openai.api_key = self.API_KEY
        self.messages: list[dict[str, str]] = [
            {"role": "system", "content": "You are a bot specialized in playing a card game."},
            {"role": "user", "content": prompt},
        ]
        value = self.get_integer_response(0, len(options)-1, self.prompt_option)
        return options[value]
    
    def choose_agent_target(self, battle_state: BattleState, list_name: str, agent_list: list[Agent]) -> Agent:
        prompt = get_agent_target_prompt(battle_state, list_name, agent_list)
        self.messages.append({"role": "user", "content": prompt})
        value = self.get_integer_response(0, len(agent_list)-1, PromptOption.NONE)
        return agent_list[value]
    
    def choose_card_target(self, battle_state: BattleState, list_name: str, card_list: list[Card]) -> Card:
        prompt = get_card_target_prompt(battle_state, list_name, card_list)
        self.messages.append({"role": "user", "content": prompt})
        value = self.get_integer_response(0, len(card_list)-1, PromptOption.NONE)
        return card_list[value]
    
    def dump_history(self, filename: str):
        filename = get_unique_filename(filename, 'json')
        with open(filename, "w") as file:
            json.dump(self.history, file, indent=4)
    
    def clear_history(self):
        self.history: list[dict[str, Any]] = [{
            'model': str(self.model_name),
            'prompt_option': str(self.prompt_option),
        }]