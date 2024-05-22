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
    strip_response, _get_game_context
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
        GPT_Turbo_4 = "gpt-4-1106-preview"
        GPT_Turbo_35 = "gpt-3.5-turbo"
        Instruct_Davinci = "text-davinci-003"
        Instruct_GPT_Turbo_35 = "gpt-3.5-turbo-instruct"
    
    call_timestamp: dict[ModelName, float] = {}
    token_count: dict[ModelName, int] = {}
    token_limit_per_minute = { #https://platform.openai.com/account/limits
        ModelName.GPT_4: 80000, #10000,
        ModelName.GPT_Turbo_4: 600000, #150000,
        ModelName.GPT_Turbo_35: 160000, #90000,
        ModelName.Instruct_Davinci: 250000,
        ModelName.Instruct_GPT_Turbo_35: 250000,
    }

    CHAT_MODELS = [ModelName.GPT_4, ModelName.GPT_Turbo_4, ModelName.GPT_Turbo_35]
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
        prev = ChatGPTBot.call_timestamp.get(self.model_name, current - 1000) # default: long time ago
        if self.model_name in ChatGPTBot.CHAT_MODELS:
            est_tokens: int = sum([len(key) + len(val) for d in request['messages'] for key, val in d.items()])//4
        elif self.model_name in ChatGPTBot.COMPLETION_MODELS:
            est_tokens: int = len(request['prompt'])//4
        else:
            raise Exception(f"Model type not recognized for {self.model_name}")
        if self.model_name not in ChatGPTBot.call_timestamp or\
            ChatGPTBot.token_count[self.model_name] + est_tokens > (ChatGPTBot.token_limit_per_minute[self.model_name] * self.share_of_limit):
            sleep_time = 60 - min(current - prev, 60)
            sleep_time += 3 # eps
            print(f'{self.name} sleeping for {sleep_time}')
            time.sleep(sleep_time)
            ChatGPTBot.call_timestamp[self.model_name] = current
            ChatGPTBot.token_count[self.model_name] = 0
        print(f'name: {self.name}, tokens: {ChatGPTBot.token_count[self.model_name]}, est: {est_tokens}')
        try:
            if self.model_name in ChatGPTBot.CHAT_MODELS:
                before_request = time.time()
                response = openai.ChatCompletion.create(**request)
                self.metadata["response_time"].append(time.time() - before_request)
                print(f"Added to metadata: {self.metadata['response_time'][-1]}")
                self.history.append({'request': request, 'response': response})
                ChatGPTBot.token_count[self.model_name] += int(response['usage']['total_tokens'])
                return response['choices'][0]['message']['content']
            elif self.model_name in ChatGPTBot.COMPLETION_MODELS:
                before_request = time.time()
                response = openai.Completion.create(**request)
                self.metadata["response_time"].append(time.time() - before_request)
                print(f"Added to metadata: {self.metadata['response_time'][-1]}")
                self.history.append({'request': request, 'response': response})
                ChatGPTBot.token_count[self.model_name] += int(response['usage']['total_tokens'])
                return response['choices'][0]['text']
            else:
                raise Exception(f"Model API type not recognized for {self.model_name}")
        except openai.error.RateLimitError as e:
            ChatGPTBot.token_count[self.model_name] = int(ChatGPTBot.token_limit_per_minute[self.model_name] * self.share_of_limit + 100)
            raise e
            

    # loosely adapted from https://github.com/adamkarvonen/chess_gpt_eval/blob/master/gpt_query.py
    def translate_to_string_input(self, openai_messages: list[dict[str, str]]):
        # Translate from OpenAI's dict to a single string input
        return "\n".join([message["content"] for message in openai_messages])

    API_KEY = GPT_AUTH # redacted

    def __init__(self, model_name: ChatGPTBot.ModelName, prompt_option: PromptOption, few_shot: int, show_option_results: bool, share_of_limit: float=1):
        model_name_dict = {
            ChatGPTBot.ModelName.GPT_4: '4',
            ChatGPTBot.ModelName.GPT_Turbo_4: 't4',
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
        self.model_name = model_name
        self.prompt_option = prompt_option
        self.share_of_limit = share_of_limit
        self.few_shot = few_shot
        self.show_option_results = show_option_results
        self.messages: list[dict[str, str]] = []
        super().__init__(f"ChatGPT-{model_name_dict[model_name]}-{prompt_dict[prompt_option]}-f{self.few_shot}{'-results' if show_option_results else ''}")
        self.clear_metadata()
        self.clear_history()

    def get_integer_response(self, min: int, max: int, prompt_option: PromptOption) -> int:
        if max == min:
            self.history.append({'auto-answer': str(min)})
            self.messages = self.messages[:-1]
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
                self.metadata["wrong_format_count"] += 1
                continue
            print(f'Wrong range for {self.name}: *{response}*\nValue: {value}')
            self.metadata["wrong_range_count"] +=1
        self.messages.append({"role": "assistant", "content": response})
        return value

    def choose_card(self, game_state: GameState, battle_state: BattleState) -> EndAgentTurn|PlayCard:
        options = self.get_choose_card_options(game_state, battle_state)
        get_context = False
        if self.few_shot==0:
            self.messages: list[dict[str, str]] = [{"role": "system", "content": "You are a bot specialized in playing a card game."}]
            get_context = True
        elif len(self.messages) == 0:
            self.messages: list[dict[str, str]] = [
                {"role": "system", "content": "You are a bot specialized in playing a card game."},
                {"role": "user", "content": _get_game_context(game_state, battle_state, options)}
            ]
        if len(self.messages)-2+2 > self.few_shot*2:
            self.messages = self.messages[:2] + self.messages[-(self.few_shot-1)*2:]
        prompt = get_action_prompt(game_state, battle_state, options, self.prompt_option, get_context, self.show_option_results)
        self.messages.append({"role": "user", "content": prompt})
        openai.api_key = self.API_KEY
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

    def dump_metadata(self, filename: str):
        print(filename)
        with open(filename, "a") as file:
            json.dump(self.metadata, file, indent=4)
            file.write('\n')
    
    def clear_metadata(self):
        self.metadata["response_time"] = []
        self.metadata["wrong_format_count"] = 0
        self.metadata["wrong_range_count"] = 0

    def clear_history(self):
        self.history: list[dict[str, Any]] = [{
            'model': str(self.model_name),
            'prompt_option': str(self.prompt_option),
        }]