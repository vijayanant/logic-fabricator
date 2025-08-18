# Contradiction Handling

> \_"When two rules disagree, don’t fight. Fork reality."

---

## 🎯 Purpose

Contradictions aren’t bugs — they’re forks in the logic multiverse. This system lets users decide what to do when two or more rules yield conflicting outcomes for a given statement or simulation.

---

## 🤯 What is a Contradiction?

A contradiction arises when:

- Two rules that match a statement suggest incompatible outcomes.
- A rule and a prior belief contradict.
- A belief system already contains a fact that is logically inconsistent with a new one.

Example:

```python
Statement: "Ravi trusts Alice."

Rule A: "If someone trusts another, they should be given access."
Rule B: "Nobody should be given access unless verified."
```

Both rules match. One grants access, one denies. ⚔️

---

## 🧭 The Metaphysics of a Fabricated World: Forking Strategies

> *"When a belief splits, you must decide what kind of ghost it leaves behind."*

A contradiction is not an error; it is a conception event. The `BeliefSystem` calls upon its configured **Forking Strategy** to determine the nature of the new reality it will spawn. This is the most fundamental rule of your logic-space: not what is true, but how your world decides what to do when truth itself is in conflict.

The act of forking is an acknowledgment of a deep conflict that cannot be resolved by a simple override. Its purpose is to contain and carry the logical tension of a contradiction forward. This is not a simple replacement; it preserves the conflict, enabling richer simulations where future rules or statements may operate on this tension, potentially leading to resolution, deeper paradox, or entirely new emergent logic.

All strategies, save for the most dogmatic, result in a new, explorable multiverse. They differ in how they treat the original conflict—the beautiful wound that gave birth to the new world.

### Strategy 1: `coexist` (The Default)

*   **Philosophy:** The "Schrödinger's Cat" model. The fork exists to hold the paradox.
*   **Behavior:** A new reality is born that contains the complete state of the parent *plus* the new, contradictory statement. Both the original belief and the new one are held with equal weight, their tension becoming the defining feature of this new universe.
*   **Example:** The parent believes `"Ravi is trustworthy."` A contradiction is introduced with `"Ravi is a liar."` The forked system will now contain *both* statements, preserving the conflict.

### Strategy 2: `prioritize_new`

*   **Philosophy:** The "Recency Bias" model. Acknowledges that the past has a vote, but the present has a veto.
*   **Behavior:** The fork is born containing both contradictory beliefs. However, the new statement is given a higher **priority** or **weight**, while the ghost of the old belief lingers with diminished influence. It is not forgotten, merely... quieted.
*   **Outcome:** A reality that leans into new information, perfect for modeling systems that learn or adapt, while still carrying the memory of what they once believed.

### Strategy 3: `prioritize_old`

*   **Philosophy:** The "Logical Inertia" model. An established belief has gravity. New ideas must struggle to be heard.
*   **Behavior:** The fork is born containing both beliefs, but the original, established statement retains its high priority. The new, conflicting idea is acknowledged and recorded, but it is treated as a whisper of dissent rather than a roar of revolution.
*   **Outcome:** A conservative reality that resists change, ideal for modeling dogmatic systems or beliefs that are deeply entrenched.

### Strategy 4: `preserve`

*   **Philosophy:** The "Dogmatic Rejection" model. There is only one truth, and it has already been established.
*   **Behavior:** The forking process is invoked, but it is a formality. It returns nothing. The new, contradictory statement is utterly rejected, leaving no trace on the belief system's state.
*   **Outcome:** The original reality remains pristine and unchanged. The MCP will note that a heresy was attempted and denied, but the belief system itself remains pure.

---

## 🏗️ Data Representation

```python
class ContradictionRecord:
    statement1: Statement
    statement2: Statement
```

These are stored by the MCP for historical tracking.

---

## 🔁 Engine Behavior

- When a contradiction is detected during simulation:
  - Stop evaluation in current belief
  - Record contradiction in MCP
  - Create forks or await resolution

---

## 📚 MCP’s Role

- Tracks where forks occurred
- Stores user decisions and resolutions
- Allows going back to see alternate logic histories

---

## 🔮 Future Features

- Visual diff of forked belief systems
- Conflict heatmaps (areas of high contradiction density)
- LLM-based contradiction clustering

> \_"Contradictions don’t break the system. They *are* the system."