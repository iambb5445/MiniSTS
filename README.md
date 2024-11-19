# MiniStS

- [MiniStS](#minists)
  * [Description](#description)
  * [Slay the Spire](#slay-the-spire)
    + [Main Game Loop](#main-game-loop)
    + [Keywords](#keywords)
  * [MiniStS Structure](#minists-structure)
    + [Values](#values)
    + [Actions](#actions)
    + [Status Effects](#status-effects)
  * [How to Run](#how-to-run)
    + [Requirements](#requirements)
    + [Running MiniStS](#running-minists)
    + [Creating New Cards](#creating-new-cards)
      - [Example: Bash](#example--bash)
      - [Example: AfterImage](#example--afterimage)
    + [Comparing General Game-playing Bots](#comparing-general-game-playing-bots)

## Description
This repository includes a simplified implementation of the core loop of the game *Slay the Spire*. This implementation is introduced with the goal of enabling experimentations with adding new cards and game playing agents. MiniStS is discussed as a testbed for dynamic rule systems in paper "MiniStS: A Testbed for Dynamic Rule Exploration" by Bahar Bateni and Jim Whitehead, published at the 20th AAAI Conference on Artificial Intelligence and Interactive Digital Entertainment (AIIDE), workshop on Experimental AI in Games (EXAG), 2024.

MiniStS is also used to explore the use of Large Language Models (LLMs) as game playing agents and the effectiveness of language-based reasoning for game-playing. The results can be found in the paper "Language-Driven Play: Large Language Models as Game-Playing Agents in Slay the Spire" by Bahar Bateni and Jim Whitehead, published at Foundation of Digital Games Conference (FDG) 2024.

## Slay the Spire

MiniStS is a simplified, headless implementation of the game *Slay the Spire*. MiniStS only includes some of the cards from the game, however it is designed in a way to allow for introducing new cards by defining/combining actions, targets, and status effects. We discuss the use of MiniStS both for defining game palying agents and for defining new cards in the future sections.

<p align="center"><img alt="Slay the Spire" src="figures/StS.gif"></p>

*Slay the Spire* is a single-player deck-building roguelike card game. The game starts with a started deck of cards. Each battle, the player is given the choice to add at most one of the three card options to their deck. The battles get progressively harder, ending in a boss battle at the end of each act. MiniStS is specifically focused on simulating the battles, and does not include the game map and level progression system.

Below, you can find a simple explanation of the main game loop during each battle and an explanation of some of the keywords used in the game. Please refer to *Slay the Spire* wiki for more information. We also suggest using MiniStS human player agent to play the game yourself if you want a better understanding of the game.

### Main Game Loop

*Slay the Spire* is a single-player game played against one or more enemies.

The player starts the battle with some amount of healthpoint. If the player's HP reaches zero, the game ends and the player loses. The enemies also each have some amount of HP at the start of battle. Any enemy with zero HP will die and would not affect the game anymore. If all the enemies die, the game ends and the player wins.

At the start of every turn, each enemy also shows an intention. This intention describes what action that enemy performs after the player ends their turn. Example enemy actions are "deal 5 damage" or "gain 5 block".

There are four card piles in the game: draw pile, discard pile, exhaust pile, and hand. Initially, the player starts the game by shuffling the deck of cards into the draw pile. The other piles are empty.
Every turn, these actions are performed in this exact order:

1. The player gains some amount of energy. Most of the time this amount is 3, but some items or cards in the game can change this amount.
2. The player draws some number of cards from the draw pile into their hand. Most of the time this number is 5, but some items or cards in the game can change this amount.
If there are not enough cards in the draw pile, all the cards in the discard pile shuffle back into the draw pile. Then the remaining cards are drawn.
3. The player plays as many cards as they wants, as long as there is enough energy to play them. Then they end their turn.
4. When the player ends their turn, all the remaining cards in their hand are moved to the discard pile. New cards will be drawn next turn.
5. When the player ends their turn, the enemies perform their actions that was shown as their intention at the start of the turn.

### Keywords

The following are some of the main keywords and concepts used in the game:

* Card Type: Either Attack, Skill or Power. Power cards are played and then removed from that battle, but Attack or Skill cards move to discard pile if they are played. There are also Status or Curse card types, which are mostly unplayable and are designed to disadvantage the player in some way.
* Block: Until next turn, prevents damage. For example, if the player gains 5 block, and the enemy deals 7 damage to them that turn, the player loses only 2 HP and all their block. The Block only lasts one turn, so if there are any remining Blocks on the enemy or the player, this Block is removed right before they perform their next set of actions.
* Status Effects: Certain effects can be put on the player or the enemies that can buff or debuff that agent. Each status effect can have a value which, based on what the status effect is, shows either for how many turns that effect is active or how intense the effect is. Example effects can be found at [Status Effects](#status-effects).
* Exhaust: Remove card until end of combat.
* Ethereal: If an Ethereal card is in player's hand at the end of turn, it is Exhasted.
* Status Cards: These cards are mostly unplayable and are designed to disadvantage the player in some way.
    * Wound: An unplayable card with no effects.
    * Dazed: An unplayable card which is Ethereal.
    * Burn: An unplayable card. If the card is in player's hand at the end of his turn, the player will take 2 damage.
* Innate: Start each combat with this card in your hand.
* X cost card: If a card's cost is X, it means that when the card is played, it will consume all the avaialble energy the player has. This number of energy consumed is X, and the effect of the card is often described in terms of X.

## MiniStS Structure

In this section, we discuss various components that create MiniStS. Understanding these components may be required for defining new cards, as some cards require new Actions, new Value types, or new Status Effects to be defined.

### Values

The values object in the game is used to define any values used in card definition or enemy behavior. The values can be defined to be upgradable (be changed to another value when the card is upgraded), or sample a random distribution. The following value types are currently supported in the game:

- ConstValue: A value with a constant amount.
- UpgradableOnce: A value that can be upgraded at most once to a new amount.
- LinearUpgradable: A value that can be linearly increased or decreased through upgrading. The value can be upgraded any number of times. (Used for cards such as `Searing Blow`)
- RandomUniformRange: A value that is sampled randomly from a uniform range. The value is deterministic, and it can be `peek`ed at without changing its internal state.

A new value type can be defined as long it implements a set of functions:

- get: Get the amount of this value. Any random value should be sampled again with this funciton is called.
- peek: Get the amount of this value without changing its internal state. Any random value should return the same amount whenever it's peeked at, until it's sampled with get.
- negative: The amount of this value times -1.
- upgrade: Upgrade the value. Some values do not react to this function in any way.

### Actions

MiniStS uses a set of actions both for enemy behavior and for card effects, such as `DealAttackDamage`, `GainBlock`, `DiscardCard`, `ApplyStatus`. The existing actions are located in the `actions` directory. There are three action types in the game:
- Actions requiring an agent target (i.e. player or enemy), such as `DealAttackDamage` or `GainBlock` actions.
- Actions requiring a card target, such as `DiscardCard` or `Exhause` actions.
- Actions not requiring any targets, such as `DrawCard`or `AddMana` actions.

To define a new action, it should implement the `play` function. The `play` function has the following input arguments:
- `by`: the agent who have performed this action
- `game_state`: the state of the game including player's deck, ascention level, etc.
- `battle_state`: the state of the battle including turn number, enemies, card piles (hand, draw, discard, etc).
- [only for targeting actions] `target`: the target of this action, which can be an agent or a card based on whether this action is a `AgentTargetedAction` or a `CardTargetedAction`.

### Status Effects

In *Slay the Spire*, status effects can be applied to different agents in the game (i.e. enemies or the player). These status effect have a wide range of possible effects, such as:

* Vulnerable: Take 50% more damage from Attack damage. Note that this only applies to damage coming from an Attack type card or an enemy Attack action. The value of the Vulnerable effect shows how many turns it will last.
* Weak: Deal 25% less damage with Attacks. Note that this only applies to damage coming from an Attack type card or an enemy Attack action. The value of the Weak effect shows how many turns it will last.
* Strength: Adds additional damage to Attacks. Note that this only applies to damage coming from an Attack type card or an enemy Attack action. The value of the Strength effect shows how much additional damage is applied to Attack damage values.
* Intangible: Reduce all damage taken and HP loss to 1 this turn. The value shows how many turns Intangible is applied.
* Barricade: Block is not removed at the start of the turn.
* No Draw: You may not draw any more cards this turn.
* ...

Any status effect should have a definition with the following properties defined:

- `stack`: How does this status effect stacks, if is added multiple times? Some status effects have their value added together when applied multiple times, such as Vulnerable, while some do not stack such as Barricade. For more information, please refer to [Buffs](https://slay-the-spire.fandom.com/wiki/Buffs) and [Debuffs](https://slay-the-spire.fandom.com/wiki/Debuff).
- `end_turn`: Defines how a status effect is changed at the end of the turn. For example, that status effects for which their value shows how many turns they last, their value is decreased by one at the end of every turn (e.g. Vulnerable). Alternatively, some status effects only last for one turn (e.g. Intangible), or some last forever (Barricade). If the status effect are removed or changed at other trigger points (e.g. Buffer is decreased when the player receives damage), it should be implemented by using triggers.
- `done`: Defines when the status effect is removed. For example, is it removed when its value reaches zero?
- `repr`: Is the status effect represented to the player, or is it hidden? The intended use for hidden status effects are when effects in the game are not visualized for the player, such as stances for Watcher character.

After defining a status effect, triggers and events can be defined to apply its effect. Example trigger callbacks can be seen in `status_effects.py`. Some callbacks are applied on a value (e.g. Vulnerable changes the damage amount to a new amount), in which case they receive the current value as input and should return the new value. Others only result in some effect (e.g. AfterImage). Each callback also receives additional information such as the agent who had this status effect, the game state, and so on.

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
[linux/mac] source venv/bin/activate
pip install -r requirements.txt
```

To learn more, refer to virtualenv documents.

### Running MiniStS

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

### Creating New Cards

The cards in MiniStS are defined by combining actions, targets, and status effects.

To create a card, a factory method of that card should be added to `CardRepo` in `card.py`. The rest of this section includes description of different components required to define a card and example card definitions.

#### Example: Bash

The card `Bash` is defined as:

```Bash: Deal 8 Damage. Apply 2 Vulnerable.```

and can be upgraded to:

```Bash+: Deal 10 Damage. Apply 3 Vulnerable.```

Note that both actions are applied to the same enemy. To define this card in MiniStS, the following code is used:

```python
Bash = lambda: Card(
    name="Bash",
    card_type=CardType.ATTACK,
    mana_cost=ConstValue(2),
    character=Character.IRON_CLAD,
    rarity=Rarity.STARTER,
    DealAttackDamage(UpgradableOnce(8, 10)).And(
        ApplyStatus(UpgradableOnce(2, 3), StatusEffectRepo.VULNERABLE)
    ).To(ChooseAgentTarget(AgentSet.ENEMY)))
```

Note that the `DealAttackDamage` action and `ApplyStatus` action both are applied to the same enemy. The n imaginary card, `Bash*`:

```Bash*: Deal 8 Damage to an enemy. Apply 2 Vulnerable to another, possibly different, enemy.```

Can be defined as:

```python
Bash = lambda: Card(
    name="Bash",
    card_type=CardType.ATTACK,
    mana_cost=ConstValue(2),
    character=Character.IRON_CLAD,
    rarity=Rarity.STARTER,
    DealAttackDamage(UpgradableOnce(8, 10).To(
        ChooseAgentTarget(AgentSet.ENEMY))
    ).And(
        ApplyStatus(UpgradableOnce(2, 3), StatusEffectRepo.VULNERABLE).To(
            ChooseAgentTarget(AgentSet.ENEMY)
        )
    ))
```

#### Example: AfterImage

While many cards in *Slay the Spire* can be implemented using a set of actions (either existing actions or by defining new ones), some cards have lasting effects that needs to continously be applied to the game at various trigger points. For example, the card `AfterImage` is defined as:

`AfterImage: Whenever you play a card, gain 1 Block.`

To apply this action, a special effect should be triggered any time a card is played. *Slay the Spire* visualizes these effects as status effects. MiniStS also implemets these type of effects as status effects, and offers an event system to allow for defining and subscribing to specific triggers. More information on how to implement status effects can be found at [Status Effects](#status-effects).

After implementing the AfterImage status effect, the card can then be defined easily as follows:

```python
Bash = lambda: Card(
    name="AfterImage",
    card_type=CardType.POWER,
    mana_cost=ConstValue(1),
    character=Character.SILENT,
    rarity=Rarity.RARE,
    ApplyStatus(ConstValue(1), StatusEffectRepo.AFTER_IMAGE).To(
            SelfAgentTarget()
        )
    )
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
