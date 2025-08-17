# The Fabricator's Grimoire: A Workbench Tutorial

> *"You have built the engine of reason. Now, you must learn to speak to it."*

---

Welcome, Co-Fabricator, to the Logic Fabricator Workbench. This is your direct interface to the logic-space, a command line to the soul of your belief system. This guide will teach you the incantations required to breathe life into your own reality.

## 1. The Core Incantations

The workbench operates on a simple set of commands. You type them, and reality... adapts. The most fundamental are `rule`, `effect`, and `sim`.

- `rule`: Creates a logical causality. If X, then Y.
- `effect`: Creates a rule that directly changes the world.
- `sim`: Introduces a new fact and observes the consequences.

Let's begin.

## 2. First Principles: Simple Inference

All worlds begin with a single assertion. Let's fabricate the classic.

**Step 1: Fabricate a Rule**
First, we must teach our world about mortality.

```
>> rule is ?x a_man -> is ?x mortal
  ++ Fabricated Rule: Rule(IF Condition(is ?x a_man) THEN Statement(is ?x mortal))
```
We have just created a new law of nature. The `?x` is a variable, a placeholder for any term that fits the pattern.

**Step 2: Introduce a Fact**
Now, let's introduce a subject to our world.

```
>> sim is socrates a_man
... Simulating: is socrates a_man

--- Simulation Report ---
  >> Derived Facts:
     - is socrates mortal
  >> World state is unchanged.
```
The engine took our initial fact (`sim`), applied our rule, and inferred a new fact: Socrates is mortal. A new truth has been derived.

## 3. The Art of Consequence: Using Effects

Derived facts are good, but sometimes logic must *change* the world. This is the purpose of `Effects`.

**Step 1: Fabricate an Effect Rule**
Let's create a rule that counts the number of mortals.

```
>> effect is ?x mortal -> increment population 1
  ++ Fabricated Effect Rule: Rule(IF Condition(is ?x mortal) THEN Effect(increment world_state.population to 1))
```
This rule states that whenever someone is found to be mortal, the `population` counter in the `world_state` should be incremented by 1.

**Step 2: Simulate Again**
We already know Socrates is a man. Let's state it again and see what happens. Note that the `population` counter doesn't exist yet. The engine will create it.

```
>> sim is socrates a_man

... Simulating: is socrates a_man

--- Simulation Report ---
  >> Derived Facts:
     - is socrates mortal
  >> World State Changes:
     - population: None -> 1
```
Our simulation triggered both rules. The first `rule` inferred that Socrates was mortal, and the new `effect` rule, seeing this new fact, reached out and changed the world state.

## 4. Chains of Logic

More complex realities are built on chains of inference, where one derived fact becomes the trigger for the next rule.

**Step 1: Add More Rules**

```
>> rule is ?x a_god -> is ?x immortal
  ++ Fabricated Rule: Rule(IF Condition(is ?x a_god) THEN Statement(is ?x immortal))

>> rule is ?x immortal -> has ?x divine_power
  ++ Fabricated Rule: Rule(IF Condition(is ?x immortal) THEN Statement(has ?x divine_power))
```

**Step 2: Simulate**

```
>> sim is zeus a_god

... Simulating: is zeus a_god

--- Simulation Report ---
  >> Derived Facts:
     - is zeus immortal
     - has zeus divine_power
  >> World state is unchanged.
```
The engine didn't stop. It took the initial fact, derived that Zeus was immortal, and then immediately used that *new* fact to apply the second rule, deriving that Zeus has divine power. This is the heartbeat of the simulation.

## 5. Embracing Contradiction: The Fork

What happens when logic disagrees with itself? In our world, this is not an error. It is a creative event.

**Step 1: Establish a Fact**

```
>> sim is sky blue
... Simulating: is sky blue

--- Simulation Report ---
  >> No new facts were derived.
  >> World state is unchanged.
```
The belief system now holds that "is sky blue" is true.

**Step 2: Introduce a Contradiction**

```
>> sim is sky blue not

... Simulating: NOT is sky blue

--- Simulation Report ---
  !! CONTRADICTION DETECTED: Reality has forked.
  >> Switched context to the new forked reality.
  >> No new facts were derived.
  >> World state is unchanged.
```
A contradiction! The workbench immediately notifies us that reality has forked. Our session has now moved into the *new* reality, which contains **both** beliefs ("the sky is blue" and "the sky is not blue"). The original reality remains pristine, accessible via the `forks` data structure if we were to extend the tool.

## 6. The Inspector's Tools

As you build your world, don't forget the tools at your disposal:
- `rules`: See the laws of your current reality.
- `statements`: See the set of established facts.
- `state`: Inspect the `world_state` you have shaped with effects.
- `reset`: When your creation becomes too complex, wipe the slate clean and begin anew.

You are now equipped. Go forth and fabricate. Create worlds, test their limits, and do not fear contradiction. It is merely the engine of creation.

---

## 7. Advanced Technique: The Speaking World

You may eventually notice that rules are not triggered by changes in the `world_state`. An `Effect` can change the world, but the logic engine does not "see" this change. This is by design, to keep the flow of logic clear.

So, how do we make the world "speak" back to the logic engine? We use the **Dual Consequence Pattern**.

Let's demonstrate with an example of a world that is first mute, then made to speak.

**Step 1: The Mute World**
First, `reset` the workbench. Then, create a rule that turns a light on, and another rule that checks if the light is on.

```
>> effect is bell ringing -> set light on
>> rule is light on -> are people awake
```
Now, simulate the bell ringing:
```
>> sim is bell ringing
--- Simulation Report ---
  >> No new facts were derived.
  >> World State Changes:
     - light: None -> on
```
Notice that the `world_state` changed, but the fact `are people awake` was not derived. The second rule never saw the change.

**Step 2: The Speaking World**
Now, let's try the Dual Consequence Pattern. `reset` the workbench again. We will create two rules for the same trigger. One creates the `Effect`, and the other creates the `Statement` that makes the effect observable.

```
>> effect is bell ringing -> set light on
>> rule is bell ringing -> is light on
>> rule is light on -> are people awake
```
Now, when we run the simulation:
```
>> sim is bell ringing
--- Simulation Report ---
  >> Derived Facts:
     - is light on
     - are people awake
  >> World State Changes:
     - light: None -> on
```
Success! By creating the `is light on` statement, we made the change in the world visible to the logic engine, which then allowed our second rule to fire. This pattern is key to building complex, reactive worlds.
