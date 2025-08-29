# The Fabricator's Grimoire: A Workbench Tutorial

> *"You have built the engine of reason. Now, you must learn to speak to it."*

---

Welcome, Co-Fabricator, to the Logic Fabricator Workbench. This is your direct interface to the logic-space, a command line to the soul of your belief system. This guide will teach you the incantations required to breathe life into your own reality, from simple truths to beautiful, branching contradictions.

For a complete, canonical list of the engine's capabilities, please see the [Engine Features](./engine_features.md) document. This tutorial will demonstrate many of those features in practice.

## 1. First Principles: Simple Inference

All worlds begin with a single assertion. Let's fabricate the classic.

**Step 1: Fabricate a Rule**
First, we must teach our world about mortality. We speak the rule in natural language.

```
>> rule if ?x is a man then ?x is mortal
++ Fabricated Rule: Rule: IF (?x is a man) THEN ((is ?x mortal))
```
We have just created a new law of nature. The `?x` is a variable, a placeholder for any term that fits the pattern.

**Step 2: Introduce a Fact**
Now, let's introduce a subject to our world with the `sim` command.

```
>> sim socrates is a man
... Simulating: is socrates a man

--- Simulation Report ---
  >> Derived Facts:
     - (is socrates mortal)
  >> World state is unchanged.
```
The engine took our initial fact (`sim`), applied our rule, and **inferred a new fact**: Socrates is mortal. A new truth has been derived.

## 2. The Art of Consequence: Chaining & Effects

Derived facts are good, but sometimes logic must *change* the world. This is the purpose of `Effects`. Let's build on our previous step to show how a derived fact can trigger an Effect.

**Step 1: Fabricate an Effect Rule**
This rule will be triggered by the *output* of our first rule.

```
>> rule if ?x is mortal then increment mortal_count by 1
++ Fabricated Rule: Rule: IF (?x is mortal) THEN (Effect: increment world_state.mortal_count to 1)
```
This rule states that whenever someone is found to be mortal, the `mortal_count` in the `world_state` should be incremented.

**Step 2: Simulate the Chain**
Let's run the original simulation again. Watch how the engine now chains the rules together.

```
>> sim socrates is a man

... Simulating: is socrates a man

--- Simulation Report ---
  >> Derived Facts:
     - (is socrates mortal)
  >> World State Changes:
     - mortal_count: None -> 1
```
This is **inference chaining** in action. The simulation didn't stop. It took the initial fact, derived that Socrates was mortal, and then immediately used that *new* fact to apply the second rule, which reached out and changed the world.

## 3. Advanced Fabrication: The Nuances of Rules

The rule engine is more powerful than it first appears. It can match on complex patterns.

### Multi-Variable Matching

You can define rules that bind multiple variables from a single statement.

```
>> rule ?x gives ?y to ?z -> ?x no_longer_has ?y
++ Fabricated Rule: Rule: IF (?x gives ?y to ?z) THEN ((?x no_longer_has ?y))

>> sim alice gives the_book to bob

... Simulating: alice gives the_book to bob

--- Simulation Report ---
  >> Derived Facts:
     - (alice no_longer_has the_book)
  >> World state is unchanged.
```

### Wildcard Matching

You can also create rules where a variable consumes the rest of the statement. This is useful for capturing quotes or lists. To use a wildcard, prefix the variable name with a `*`.

```
>> rule ?speaker says *speech -> create_transcript_of ?speech
++ Fabricated Rule: Rule: IF (?speaker says *speech) THEN ((create_transcript_of ?speech))

>> sim ravi says hello world how are you

... Simulating: ravi says hello world how are you

--- Simulation Report ---
  >> Derived Facts:
     - (create_transcript_of ["hello", "world", "how", "are", "you"])
  >> World state is unchanged.
```

### Conjunctive Conditions (AND)

You can create rules that only fire if multiple conditions are met.

```
>> rule if ?x is a king and ?x is wise then ?x is a good_ruler
++ Fabricated Rule: Rule: IF ((?x is a king) & (?x is wise)) THEN ((?x is a good_ruler))

>> sim arthur is a king
... Simulating: is arthur is a king
--- Simulation Report ---
  >> No new facts were derived.
  >> World state is unchanged.

>> sim arthur is wise
... Simulating: is arthur is wise
--- Simulation Report ---
  >> Derived Facts:
     - (arthur is a good_ruler)
  >> World state is unchanged.
```
Notice the rule did not fire until both facts, "arthur is a king" and "arthur is wise", were present in the belief system.

## 4. Embracing Paradox: The Art of the Fork

What happens when logic disagrees with itself? In our world, this is not an error. It is a creative event.

**Step 1: Establish a Fact**
```
>> sim the sky is blue
... Simulating: the sky is blue
--- Simulation Report ---
  >> No new facts were derived.
  >> World state is unchanged.
```
The belief system now holds that "the sky is blue" is true.

**Step 2: Introduce a Contradiction**
```
>> sim the sky is not blue

... Simulating: NOT the sky is blue

--- Simulation Report ---
  !! CONTRADICTION DETECTED: Reality has forked.
  >> Switched context to the new forked reality.
  >> No new facts were derived.
  >> World state is unchanged.
```
A contradiction! The workbench immediately notifies us that reality has forked. Our session has now moved into the *new* reality, which, by default, contains **both** beliefs ("the sky is blue" and "the sky is not blue"). This is the `coexist` strategy in action.

## 5. The Inspector's Tools

As you build your world, don't forget the tools at your disposal:
- `rules`: See the laws of your current reality.
- `statements`: See the set of established facts.
- `state`: Inspect the `world_state` you have shaped with effects.
- `forks`: See how many alternate realities you have spawned.
- `reset`: When your creation becomes too complex, wipe the slate clean and begin anew.
- `help`: Display the list of all available commands.

## 6. Advanced Technique: The Speaking World

You may eventually notice that rules are not triggered by changes in the `world_state`. An `Effect` can change the world, but the logic engine does not "see" this change. This is by design, to keep the flow of logic clear and traceable.

So, how do we make the world "speak" back to the logic engine? We use the **Dual Consequence Pattern**. A rule that needs to be observable should have two consequences: one `Effect` to change the world, and one `Statement` to announce that change to the logical world.

Let's demonstrate. `reset` the workbench, then:
```
>> rule if the bell rings then set the light to on
++ Fabricated Rule: Rule: IF (the bell rings) THEN (Effect: set world_state.light to on)

>> rule if the light is on then the people are awake
++ Fabricated Rule: Rule: IF (the light is on) THEN ((the people are awake))

>> sim the bell rings
--- Simulation Report ---
  >> No new facts were derived.
  >> World State Changes:
     - light: None -> on
```
Notice the `world_state` changed, but the fact `(the people are awake)` was not derived. The second rule never saw the change.

Now, let's add the "speaking" part of the pattern.
```
>> rule if the bell rings then the light is on
++ Fabricated Rule: Rule: IF (the bell rings) THEN ((the light is on))

>> sim the bell rings
--- Simulation Report ---
  >> Derived Facts:
     - (the light is on)
     - (the people are awake)
  >> World State Changes:
     - light: None -> on
```
Success! By adding a rule that created the `(the light is on)` statement, we made the change visible to the logic engine, which then allowed our second rule to fire. This pattern is key to building complex, reactive worlds.

---
You are now equipped. Go forth and fabricate. Create worlds, test their limits, and do not fear contradiction. It is merely the engine of creation.
