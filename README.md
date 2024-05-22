# MiniStS

## Description
This repository includes a simplified implementation of the core loop of the game Slay the Spire. This implementation is introduced with the goal of enabling experimentations with adding new cards and game playing agents. This relates to the paper "Language-Driven Play: Large Language Models as Game-Playing Agents in Slay the Spire" by Bahar Bateni and Jim Whitehead, published at Foundation of Digital Games Conference (FDG) 2024.

## How to Run

### Requirements

The list of requirements are available in the `requirements.txt` file. You can install these requirements with `pip` by using:

```bash
pip install -r requirements.txt
```

It is recommended but not required to use a virtual environment when installing the requirements. You can use virtualenv by running:

```bash
pip install virtualenv
virtualenv venv
[windows] venv\Scripts\activate
[linux] source venv/bin/activate
pip install -r requirements.txt
```

To learn more, refer to virtualenv documents.

### Running StS


You may run this repository as a single playthrough or as a set of experiments. To run a single playthrough, you can run `main.py`. By default, this uses human input to play the game. To change the agent, you can use the examples in `main.py`. To understand the arguments for defining an agent, refer to the short description provided in the next subsection, or to the paper. Note that the LLM agent requires to include your personal authentication token to OpenAI's chatgpt in `auth.py`.

```python
agent = HumanInput(True)
agent = BacktrackBot(4, False)
agent = ChatGPTBot(ChatGPTBot.ModelName.GPT_Turbo_35, PromptOption.CoT, 0, False, 1)
```

By default, the code uses the starter deck for the character IronClad. To change the set of cards, you can use one of the following options:

```python
# option 1: use of the decks defined in the paper
game_state.set_deck(*CardRepo.get_scenario_0()[1])
# option 2: use any set of cards defined in the CardGen object
game_state.set_deck(CardGen.Strike(), CardGen.Defend(), CardGen.Defend())
# option 3: add one or more cards to the current deck
game_state.add_to_deck(CardGen.Strike(), CardGen.Defend(), CardGen.Defend())
```

### Comparing General Game-playing Bots

To run a simulation of the same scenario for different cards, you can use the following command:

```
python evaluation\\evaluate_bot.py {test_count} {thread_count} {scenario} {enemies} {bots} [options]

test_count: the number of runs per bot
thread_count: the number of threads to runs the tests concurrently (max thread_count is test_count)
scenario: the index of the scenario - a number in range [0, 4]
enemies: a string containing letters for each enemy in {g: Goblin, h: HobGoblin, l: Leach, j: JawWorm}
bots: name of bots seperated by whitespace
options:
-- name: can be used to define a custom name to use in the directory that is used to save the results
-- dir: can be used to define a directory for saving the results
-- log: used to define which verbose level should be used for simulaitons (recommended: not use this option unless the number of simulations are small)
-- anonymize: whether or not to anonymize the name of cards when passed to the LLM agent (recommended: use this optino, since it improves the performance of the LLM agent by preventing some bias)
-- time: whether or not to time the execution of each simulation. This will force different agents to not be run in parallel with each other to prevent effect of execution time for one agent to affect the other by sharing resources. In other words, if this option is true, this would make it so that different simulations of test_count are run in parallel but are awaited before moving to the next agent.
```

The existing agents for this command are the following:

```
r: random bot, chooses one of the actions randomly.
bt: backtrack agent. should also indicate the depth of the agent (e.g. bt3, bt4, bt5)
bts: backtrack agent with save option. will save the seen-before states of the game to not calculate the same subtree twice. we did not notice a significant change in the execution time. should also indicate the depth of the agent (e.g. bts3, bts4, bts5)
gpt: the LLM agent using OpenAI's chatgpt api. has the following options:
    model-name: is one of the following: {t3.5: gpt 3.5 turbo, 4: gpt 4, t4: gpt 4 turbo, it3.5: gpt instruct 3.5, idav: gpt instruct davinci} this is the only required option
    promot-option: can be one of the following: {none, cot: chain-of-thought reasoning, cotr: reverse-chain-of-thought, dag: uses a set of questions in the prompt} refer to the paper for more information
    -f: is used to indicate how many shots are used. a few shot option (e.g. f3, f4, f5) can be used to include some number of previous state (e.g. 3, 4 or 5 in the examples) in the prompt. we found this to results in worse perfromance, but can be used for experimentations. the default value is f0.
    -results: if included, will show the outcome of each option to the agent in the prompt. we found this to results in worse perfromance, but can be used for experimentations.
an example of the gpt agent can be: gpt-t3.5-none gpt-t3.5-cot, gpt-t3.5-f5, gpt3.5-results
```

An example of the simulation command can be the following:
```
python evaluation\\evaluate_bot.py 50 50 0 h r bt3 gpt-t3.5-cot --log --dir final\\test --anonymize --time
```
