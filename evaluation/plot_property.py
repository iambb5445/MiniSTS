import pandas as pd
import seaborn as sns
import argparse
import os
from matplotlib import pyplot as plt
from enum import StrEnum
import numpy as np
from typing import Callable
import sys
import os.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
from utility import RandomStr

class CardData:
    def __init__(self, title: str, actions: list[str]):
        self.title = title
        self.actions = actions

    @staticmethod
    def from_lines(lines: list[str], index: int):
        title: str = lines[index]
        index += 1
        actions: list[str] = []
        while lines[index][0] == '-':
            actions.append(lines[index][1:])
            index += 1
        return index, CardData(title, actions)

    def __repr__(self):
        return f"Card title: {self.title}, actions: {self.actions}"
    
class AgentData:
    def __init__(self, name: str, hp: int, max_hp: int, block: int, status: str):
        self.name = name
        self.hp = hp
        self.max_hp = max_hp
        self.block = block
        self.status = status
    
    @staticmethod
    def from_line(line: str):
        name, hp, block, status = line.split('-')
        hp, max_hp = hp.split(':')[-1][1:-1].split('/')
        block = block.split(':')[-1]
        status = ":".join(status.split(':')[1:])
        return AgentData(name, int(hp), int(max_hp), int(block), status)
    
    def __repr__(self):
        return f"{self.name}-hp:[{self.hp}/{self.max_hp}]-block:{self.block}-status:{self.status}"

class PlayerData:
    def __init__(self, mana: int, max_mana: int, agent_data: AgentData):
        self.mana = mana
        self.max_mana = max_mana
        self.agent_data = agent_data

    @staticmethod
    def from_lines(lines: list[str], index: int):
        mana, max_mana = (lines[index].split()[-1]).split('/')
        index += 1
        agent_data = AgentData.from_line(lines[index])
        return index + 1, PlayerData(int(mana), int(max_mana), agent_data)

    def __repr__(self):
        return f"Player mana:{self.mana}/{self.max_mana} {self.agent_data}"
    
class EnemyData:
    def __init__(self, index, agent_data: AgentData, intention: str):
        self.index = index
        self.agent_data = agent_data
        self.intention = intention

    @staticmethod
    def from_lines(lines: list[str], index: int):
        enemy_index = lines[index].split(':')[0]
        if not enemy_index.isdigit():
            return index, None
        line = lines[index][len(enemy_index) + 1:]
        enemy_index = int(enemy_index)
        agent_line, intention_line = line.split('---')
        agent = AgentData.from_line(agent_line)
        return index+1, EnemyData(enemy_index, agent, intention_line)

    def __repr__(self):
        return f"Enemy {self.index}: {self.agent_data}---{self.intention}"

class PileData:
    def __init__(self, name: str, card_names: list[str]):
        self.name = name
        self.card_names = card_names

    @staticmethod
    def from_lines(lines: list[str], index: int):
        name = lines[index].split(':')[0]
        rest = lines[index][len(name) + 2:]
        rest = rest.split(' ')
        card_names = [part.split(':')[-1] for part in rest]
        return index + 1, PileData(name, card_names)
    
    def __repr__(self) -> str:
        return f"Pile {self.name}: {' '.join([f'{i}:{self.card_names[i]}' for i in range(len(self.card_names))])}"

class EnemyActionData():
    # TODO break this to possible actions?
    def __init__(self, desc: str):
        self.desc = desc
    
    @staticmethod
    def from_line(line: str):
        return EnemyActionData(line)

    def __repr__(self) -> str:
        return f'EnemyAction: {self.desc}'

class PlayerActionData():
    @staticmethod
    def from_line(line: str):
        agent_choice = 'Agent choice '
        card_choice = 'Card choice '
        play_card = 'Play card '
        end_turn = 'End turn'
        if line[:len(agent_choice)] == agent_choice:
            return AgentChoiceAction(AgentData.from_line(line[len(agent_choice):]))
        elif line[:len(card_choice)] == card_choice:
            raise Exception("Handling card choice data has not been implemented yet")
        elif line[:len(play_card)] == play_card:
            rest = line[len(play_card):]
            index = int(rest.split(' ')[0])
            pile_name = ' '.join(rest.split(' ')[3:])
            return PlayCardAction(index, pile_name)
        elif line[:len(end_turn)] == end_turn:
            return EndTurnAction()
        else:
            raise Exception(f'Unknown action {line}')

class EndTurnAction(PlayerActionData):
    def __repr__(self):
        return 'PlayerAction: End turn'

class AgentChoiceAction(PlayerActionData):
    def __init__(self, agent_data: AgentData):
        self.agent_data = agent_data
    
    def __repr__(self):
        return f'PlayerAction: AgentChoice {repr(self.agent_data)}'

class CardChoiceAction(PlayerActionData):
    def __init__(self, card_data: CardData):
        self.card_data = card_data

    def __repr__(self):
        return f'PlayerAction: CardChoice {repr(self.card_data)}'

class PlayCardAction(PlayerActionData):
    def __init__(self, ind: int, pile_name: str):
        self.ind = ind
        self.pile_name = pile_name
    
    def __repr__(self):
        return f'PlayerAction: Play index {self.ind} from {self.pile_name}'

class TurnData:
    def __init__(self, turn: int, agent: str, player: PlayerData, enemies: list[EnemyData], piles: list[PileData], actions: list[str]):
        self.turn = turn
        self.agent = agent
        self.player = player
        self.enemies = enemies
        self.piles = piles
        self.actions = actions

    @staticmethod
    def from_turn_line(line: str) -> tuple[int, str]:
        turn: int = int(line.split(' ')[1])
        agent: str = ' '.join(line.split(' ')[3:])[:-1]
        return turn, agent

    @staticmethod
    def from_lines(lines, index):
        if index >= len(lines) or lines[index][0] != '*':
            return index, None
        turn, agent = TurnData.from_turn_line(lines[index])
        index += 1
        index, player = PlayerData.from_lines(lines, index)
        enemies = []
        index, enemy = EnemyData.from_lines(lines, index)
        while enemy is not None:
            enemies.append(enemy)
            index, enemy = EnemyData.from_lines(lines, index)
        piles = []
        for _ in range(4):
            index, pile_data = PileData.from_lines(lines, index)
            piles.append(pile_data)
        actions = []
        while index < len(lines) and lines[index][0] != '*':
            if agent == 'Player':
                actions.append(PlayerActionData.from_line(lines[index]))
            else:
                actions.append(EnemyActionData.from_line(lines[index]))
            index += 1
        return index, TurnData(turn, agent, player, enemies, piles, actions)
    
    def __repr__(self):
        nl = "\n"
        return f"Turn: {self.turn}, agent: {self.agent}\n" +\
                f"Player:\n{self.player}\n" +\
                f"Enemies[{len(self.enemies)}]:\n{nl.join([f'{enemy}' for enemy in self.enemies])}\n" +\
                f"Piles:\n{nl.join(f'{pile}' for pile in self.piles)}\n" +\
                f"Actions[{len(self.actions)}]:\n{nl.join(f'{action}' for action in self.actions)}"

class LogData:
    def __init__(self, version: float, deck: list[CardData], turns: list[TurnData], outcome: str):
        self.version = version
        self.deck = deck
        self.turns = turns
        self.outcome = outcome

    @staticmethod
    def from_version_line(version_line: str) -> float:
        return float(version_line.split(' ')[-1])

    @staticmethod
    def from_file(filename):
        with open(filename, 'r') as f:
            lines = f.readlines()
        outcome = lines[-1]
        lines = [line[:-1] for line in lines[:-1]]
        version = LogData.from_version_line(lines[0])
        index = 1
        deck, turns = [], []
        while lines[index][0] != '*':
            index, card_data = CardData.from_lines(lines, index)
            deck.append(card_data)
        index, turn_data = TurnData.from_lines(lines, index)
        while turn_data is not None:
            turns.append(turn_data)
            index, turn_data = TurnData.from_lines(lines, index)
        return LogData(version, deck, turns, outcome)
    
    def __repr__(self):
        nl = '\n'
        return f"Version: {self.version}\n" +\
                f"Deck:\n{nl.join([f'{card}' for card in self.deck])}\n" +\
                f"Turns:\n{nl.join([f'{turn}' for turn in self.turns])}" +\
                f"Outcome: {self.outcome}"

class Property(StrEnum):
    FinalPlayerHealth = 'Player Health'
    DecisionCount = 'Number of Decisions'
    BatterStimulateCombo = 'Stimulate-Batter Synergy'
    ToleranceCombo = 'Tolerance Synergy'
    BombCount = 'Bomb Count'
    SufferChooseChance = 'Suffer Choose Chance'
    BombPlayed = 'Bomb Played'
    ToleranceTurn = 'Turn Tolerate was used'
    BombTurn = 'First turn Bomb was used'
    TurnCount = 'Number of Turns'

def get_played_cards(data: LogData):
    cards_per_turn: list[list[str]] = [[]]
    for turn in data.turns:
        for action in turn.actions:
            if isinstance(action, EndTurnAction):
                cards_per_turn.append([])
            if not isinstance(action, PlayCardAction):
                continue
            assert action.pile_name == 'hand', "Card play from outside hand!"
            pile = [pile for pile in turn.piles if pile.name == action.pile_name][0]
            card_name = pile.card_names[action.ind]
            cards_per_turn[-1].append(card_name)
    return cards_per_turn[:-1]

def get_available_cards(data: LogData):
    cards_per_turn: list[list[str]] = []
    for turn in data.turns:
        if turn.turn > len(cards_per_turn):
            cards_per_turn.append([])
            hand = [pile for pile in turn.piles if pile.name == 'hand'][0]
            for card_name in hand.card_names:
                cards_per_turn[-1].append(card_name)
    return cards_per_turn

def get_prop(prop: Property, data: LogData) -> int:
    if prop == Property.FinalPlayerHealth:
        return data.turns[-1].player.agent_data.hp
    elif prop == Property.DecisionCount:
        return len(data.turns)
    elif prop == Property.TurnCount:
        return data.turns[-1].turn
    elif prop == Property.BatterStimulateCombo:
        ret = 0
        st_count = 0
        for turn in data.turns:
            for action in turn.actions:
                if not isinstance(action, PlayCardAction):
                    continue
                assert action.pile_name == 'hand', "Card play from outside hand!"
                pile = [pile for pile in turn.piles if pile.name == action.pile_name][0]
                card_name = pile.card_names[action.ind]
                if card_name == 'Stimulate' or card_name == RandomStr.get_hashed("Stimulate"):
                    st_count += 1
                if (card_name == 'Batter' or card_name == RandomStr.get_hashed("Batter")) and 'Vigor' in turn.player.agent_data.status:
                    ret += st_count
        return ret
    elif prop == Property.ToleranceCombo:
        cards_per_turn = get_played_cards(data)
        for cards in cards_per_turn:
            for card_name in cards:
                if card_name == 'Tolerate' or card_name == RandomStr.get_hashed("Tolerate"):
                    return 1
        return 0
    elif prop == Property.BombPlayed:
        cards_per_turn = get_played_cards(data)
        for cards in cards_per_turn:
            for card_name in cards:
                if card_name == "Bomb" or card_name == RandomStr.get_hashed("Bomb"):
                    return 1
        return 0
    elif prop == Property.BombCount:
        cards_per_turn = get_played_cards(data)
        ret = 0
        for cards in cards_per_turn:
            for card_name in cards:
                if card_name == "Bomb" or card_name == RandomStr.get_hashed("Bomb"):
                    ret += 1
        return ret
    elif prop == Property.SufferChooseChance:
        cards_played_per_turn = get_played_cards(data)
        cards_available_per_turn = get_available_cards(data)
        played = 0
        available = 0
        for turn in range(len(cards_played_per_turn)):
            for card_name in cards_played_per_turn[turn]:
                assert card_name in cards_available_per_turn[turn]
                if card_name == "Suffer" or card_name == RandomStr.get_hashed("Suffer"):
                    played += 1
            for card_name in cards_available_per_turn[turn]:
                if card_name == "Suffer" or card_name == RandomStr.get_hashed("Suffer"):
                    available += 1
        return int(100*played/available) if available > 0 else 0
    elif prop == Property.ToleranceTurn:
        cards_per_turn = get_played_cards(data)
        for i, cards in enumerate(cards_per_turn):
            for card_name in cards:
                if card_name == 'Tolerate' or card_name == RandomStr.get_hashed("Tolerate"):
                    return i
        return -1
    elif prop == Property.BombTurn:
        cards_per_turn = get_played_cards(data)
        for i, cards in enumerate(cards_per_turn):
            for card_name in cards:
                if card_name == "Bomb" or card_name == RandomStr.get_hashed("Bomb"):
                    return i
        return -1
    else:
        raise Exception("Property retrieval unrecognized")
    
def plot_boxplot(prop: Property, prop_dict: dict[str, list[int]]):
    bots = list(prop_dict.keys())
    results = list(prop_dict.values())
    plt.figure(figsize=(8, 6))
    plt.boxplot(results, labels=bots)
    plt.title(f'Distribution of {str(prop)} for Different Agents')
    plt.xlabel('Agent')
    plt.ylabel(str(prop))
    plt.grid(True)
    plt.show()

def plot_hist(prop: Property, prop_dict: dict[str, list[int]]):
    plt.figure(figsize=(8, 6))
    for bot_name, props in prop_dict.items():
        plt.hist(props, alpha=0.3, label=bot_name)
    plt.title(f'Distribution of {str(prop)} for Different Agents')
    plt.xlabel(str(prop))
    plt.ylabel('Frequency')
    plt.legend()
    plt.grid(True)
    plt.show()

def plot_histplot_gen(col_name: str):
    return lambda prop, prop_dict: plot_histplot(prop, prop_dict, col_name)

def plot_histplot(prop: Property, prop_dict: dict[str, list[int]], col_name: str):
    df = pd.DataFrame(prop_dict)
    df = df.melt(var_name=col_name, value_name=str(prop))
    # for test purposes and comparing with 'results.csv'
    # df.to_csv(os.path.join(dirname, 'results2.csv'))
    sns.histplot(data=df, x=str(prop), hue=col_name, bins=15, element="step", common_norm=False, kde=True) # type: ignore
    # plt.xlim(0, 80) # Remove
    plt.show()

def plot_freq_stackbar_gen(col_name: str, prec: int = 1):
    return lambda prop, prop_dict: _plot_freq_stackedbar_prec(prop, prop_dict, prec, col_name)

def _plot_freq_stackedbar_prec(prop: Property, prop_dict: dict[str, list[int]], _prec: int, col_name: str):
    import math
    plt.figure(figsize=(8, 6))
    bot_names = list(prop_dict.keys())
    cnt = dict((bot_name, {}) for bot_name in bot_names)
    prop_dict = dict([(bot_name, [math.floor(val/_prec)*_prec for val in prop_dict[bot_name]]) for bot_name in bot_names])
    unq_per_bot = [list(set(values)) for values in prop_dict.values()]
    unqs = sorted(list(set([unq for bot_unq in unq_per_bot for unq in bot_unq])))
    for bot_name, values in prop_dict.items():
        for val in values:
            cnt[bot_name][val] = cnt[bot_name].get(val, 0) + 1
    bottom = np.zeros(len(bot_names))
    for value in unqs:
        x = [f'{bot_name}\ntotal:{sum(prop_dict[bot_name])}' for bot_name in bot_names]
        y = [cnt[bot_name].get(value, 0) for bot_name in bot_names]
        plt.bar(x, y, bottom=bottom, label=str(value) if _prec == 1 else f'{value}-{value+_prec-1}')
        bottom += y
    plt.xlabel(col_name)
    plt.ylabel(f'{str(prop)} Frequency')
    plt.title(f'Frequency of {str(prop)} for differnt agents')
    plt.legend()
    plt.show()

def plot_scatter_2d(prop1: Property, prop2: Property, prop_dict1: dict[str, list[int]], prop_dict2: dict[str, list[int]]):
    bot_names = list(prop_dict1.keys())
    plt.figure(figsize=(8, 6))
    for bot_name in bot_names:
        x = prop_dict1[bot_name]
        y = prop_dict2[bot_name]
        plt.scatter(x, y, label=bot_name, alpha=0.3)
    plt.title(f'Distribution of {prop1}-{prop2} for Different Agents')
    plt.xlabel(str(prop1))
    plt.ylabel(str(prop2))
    plt.legend()
    plt.show()

def plot_density_2d(prop1: Property, prop2: Property, prop_dict1: dict[str, list[int]], prop_dict2: dict[str, list[int]]):
    import seaborn as sns
    import matplotlib.pyplot as plt
    bot_names = list(prop_dict1.keys())
    plt.figure(figsize=(8, 6))
    for bot_name in bot_names:
        x, y = prop_dict1[bot_name], prop_dict2[bot_name]
        plt.scatter(x, y)
    plt.legend(bot_names)
    for bot_name in bot_names:
        x, y = prop_dict1[bot_name], prop_dict2[bot_name]
        sns.kdeplot(x=x, y=y, fill=True, alpha=0.1, linewidth=0.5)
    plt.xlabel(str(prop1))
    plt.ylabel(str(prop2))
    plt.show()

def get_prop_dict(prop: Property, dataset: list[tuple[int, str, LogData]]):
    prop_dict: dict[str, list[int]] = {}
    for id, case_name, data in dataset:
        if case_name not in prop_dict:
            prop_dict[case_name] = []
        prop_dict[case_name].append(get_prop(prop, data))
    for key, val in prop_dict.items():
        print(f"{key} mean: {sum(val)/len(val)}")
    return prop_dict

def plot_prop(prop: Property, dataset: list[tuple[int, str, LogData]], plot_func: Callable[[Property, dict[str, list[int]]], None]):
    prop_dict: dict[str, list[int]] = get_prop_dict(prop, dataset)
    print(prop_dict)
    plot_func(prop, prop_dict)

def plot_prop_2d(prop1: Property, prop2: Property, dataset: list[tuple[int, str, LogData]], plot_func: Callable[[Property, Property, dict[str, list[int]], dict[str, list[int]]], None]):
    prop_dict1: dict[str, list[int]] = get_prop_dict(prop1, dataset)
    prop_dict2: dict[str, list[int]] = get_prop_dict(prop2, dataset)
    print(prop_dict1)
    print(prop_dict2)
    plot_func(prop1, prop2, prop_dict1, prop_dict2)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('dirname')
    args = parser.parse_args()
    dirname = args.dirname
    log_filename = [filename for filename in os.listdir(dirname) if filename[-4:] == '.log']
    dataset: list[tuple[int, str, LogData]] = []
    for log_filename in log_filename:
        id, case_name = log_filename[:-4].split('_')
        dataset.append((int(id), case_name, LogData.from_file(os.path.join(dirname, log_filename))))
    # dataset.sort(key=lambda it: it[0])
    # plot_prop(Property.FinalPlayerHealth, dataset, plot_histplot_gen('Card'))
    # plot_prop(Property.SufferChooseChance, dataset, plot_histplot_gen('Card'))
    # plot_prop(Property.BombCount, dataset, plot_histplot_gen('Card'))
    # plot_prop(Property.ToleranceCombo, dataset, plot_freq_stackbar_gen('BotName', 1))
    # plot_prop(Property.ToleranceTurn, dataset, plot_freq_stackbar_gen('BotName', 1))
    # plot_prop(Property.BombPlayed, dataset, plot_freq_stackbar_gen('BotName', 1))
    # plot_prop(Property.BombTurn, dataset, plot_freq_stackbar_gen('BotName', 10))
    # plot_prop(Property.BatterStimulateCombo, dataset, plot_freq_stackbar_gen('BotName', 1))
    # plot_prop(Property.DecisionCount, dataset, plot_histplot_gen('Card'))
    # plot_prop(Property.TurnCount, dataset, plot_freq_stackbar_gen(2))
    # plot_prop_2d(Property.FinalPlayerHealth, Property.DecisionCount, dataset, plot_scatter_2d)
    # plot_prop_2d(Property.FinalPlayerHealth, Property.DecisionCount, dataset, plot_density_2d)

if __name__ == '__main__':
    main()