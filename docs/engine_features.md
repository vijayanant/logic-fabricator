# ⚙️ Logic Fabricator: Engine Features

> *"This document is the blueprint for the engine of reason. It describes what our creation is capable of."

---

This document provides a canonical list of the features and capabilities of the core logic engine (`fabric.py`). It is the source of truth for what the fabricator can do, independent of any specific user interface.

## 1. Statements: The Units of Fact

A `Statement` is the basic unit of fact within a belief system. It is a simple structure with several key properties.

- **Structure:** A statement is composed of a `verb` (e.g., "is") and a list of `terms` (e.g., `["Socrates", "a man"]`).
- **Negation:** A statement can be `negated`, representing the opposite of its assertion (e.g., `NOT is Socrates immortal`).
- **Priority:** A statement has a `priority` value, which is used by certain forking strategies to resolve contradictions.

---

## 2. Rule Conditions: How Rules Match

The engine's ability to match a `Rule` to a `Statement` is flexible and powerful, allowing for complex pattern recognition.

### Simple Matching
- **By Verb:** The simplest match, where the verb in a statement matches the verb in a rule's condition.
- **By Synonym:** A rule's condition can define a list of `verb_synonyms`, allowing it to be triggered by a wider range of statements.

### Advanced Pattern Matching
- **Multi-Variable Binding:** The engine can parse and bind multiple variables from a single, structured statement. 
  - *Example:* A rule with the condition `?x gives ?y to ?z` will correctly match the statement `alice gives the_book to bob` and bind all three variables.
- **Wildcard Matching:** A rule can define a "greedy" variable that consumes all remaining terms in a statement. This is useful for capturing quotes or lists.
  - *Example:* A condition term prefixed with `*` (e.g., `?speaker says *speech`) will match `ravi says hello world` and bind `?speech` to the list `["hello", "world"]`.

### Conjunctive Conditions (`AND`)
- A rule's condition can be composed of a list of sub-conditions. For the rule to apply, the `BeliefSystem` must contain statements that match **all** of the sub-conditions. This allows for the creation of more specific and demanding rules.
  - *Example:* A rule can be defined to only trigger if `?x is a man` AND `?x is wise` are both true facts in the belief system.

---

## 3. Rule Consequences: What Rules Do

When a rule's condition is met, it produces one or more consequences.

- **Generating Statements:** The most common consequence is the creation of a new `Statement`, which is added to the belief system as a derived fact.
- **Applying Effects:** A rule can also have an `Effect` as a consequence. Effects directly modify the `world_state` dictionary, allowing a belief system to maintain and change state over time (e.g., incrementing a counter, setting a status flag).

---

## 4. The Simulation Engine: Bringing Logic to Life

The engine simulates the consequences of introducing new facts into a belief system.

### Inference Chaining
- The engine does not stop after one step. A fact derived from one rule can serve as the trigger for another rule within the same simulation cycle. This allows for complex chains of reasoning.

### Idempotent Effects
- The engine has a persistent memory of which `Effect`s it has already applied for a specific causal reason (i.e., a specific rule with specific bindings). It will not apply the same effect for the same reason again in subsequent, unrelated simulations, preventing issues like a counter being decremented multiple times for a single death.

### The Dual Consequence Pattern
- The engine maintains a strict separation between logic (`Statements`) and state (`world_state`). Changes to the `world_state` do not trigger rules.
- To make a state change visible to the logic engine, a rule must have two consequences: an `Effect` to change the world, and a `Statement` to announce the change to the logical world.

---

## 5. Contradiction Handling

Contradictions are treated as first-class events, not errors.

### Statement-Level Detection
- The engine detects direct contradictions between statements (e.g., `is sky blue` and `is sky blue not`).

### Proactive Rule-Conflict Detection
- The engine has a "tension detector" that can find latent conflicts between the *rules* themselves, even before a contradictory statement is simulated.
- This detection is context-aware. It can be given a set of helper rules to find implied conflicts. For example, it can detect a conflict between a rule for "birds" and a rule for "penguins" if it is also given the rule "a penguin is a bird."

### Forking Strategies
- When a contradiction occurs, the `BeliefSystem` can employ several strategies:
  - `COEXIST` (Default): Fork reality. The new reality contains both contradictory facts.
  - `PRESERVE`: Reject the new, contradictory fact and do not fork.
  - `PRIORITIZE_NEW`: Fork, but give the new fact a higher priority in the new reality.
  - `PRIORITIZE_OLD`: Fork, but give the original fact a higher priority in the new reality.
