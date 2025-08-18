# Logic Fabricator: Simulation Engine Plan

> *"When logic meets story, simulation begins."*

---

## 🎮 What Is the Simulation Engine?

The Simulation Engine is the component that **runs scenarios** using a belief system and a sequence of narrative statements. It applies rules, tracks state, and produces consequences.

Imagine:

```text
Ravi lies to Meera.
Meera trusts Ravi.
```

Under a belief system where “lying reduces trust,” this should produce an outcome like:

```text
Meera's trust in Ravi drops.
```

Or — if the rule doesn’t apply — no effect at all.

---

## 🔁 What Does It Actually Do?

1. **Receives input:**

   - A BeliefSystem (set of rules)
   - A sequence of Statements (narrative events)

2. **Evaluates rules:**

   - For each statement, checks if any rule applies.
   - If yes, executes its consequence logic.

3. **Tracks state:**

   - Modifies internal world state (e.g. trust levels)
   - Persists effects for subsequent statements

4. **Handles contradictions:**

   - If multiple rules contradict, simulation pauses
   - MCP is notified: fork or override?

5. **Produces result:**

   - New world state
   - A causal trace
   - Any contradictions encountered

---

## ⚙️ Example Flow

Given:

```text
Rule: "If someone lies to you, your trust decreases."
Statement: "Ravi lies to Meera."
```

→ Parse → Match → Evaluate → Modify State

→ Outcome:

```json
{
  "Meera": {
    "trust_in": {
      "Ravi": -0.3
    }
  }
}
```

---

## 🧠 World State Model

Internally, simulation maintains a data structure like:

```json
{
  "Meera": {
    "trust_in": {
      "Ravi": 0.7
    },
    "anger_towards": {}
  },
  "Ravi": {} 
}
```

- Only what’s needed is stored
- Trust/anger/loyalty/etc are dynamic properties
- The world is minimal by design — fabricated as needed

---

## 🤹 Rule Effects

Each rule, once parsed, may contain:

- **Trigger**: what statement types it applies to
- **Effect**: what state change it causes
- **Modifiers**: qualifiers or conditions

We’ll support a growing set of effect types:

- Adjust trust
- Transfer belief
- Trigger emotion
- Fork on conflict

---

## 🧬 Contradictions in Simulation

Contradictions aren’t bugs — they’re branch points.

When rules pull in opposite directions:

```text
Rule 1: If Ravi lies, trust drops.
Rule 2: If Meera is forgiving, trust increases.
```

Simulation notes the tension.

User decides:

- Which rule to trust more?
- Fork into two belief systems?

All this is recorded by MCP.

---

## 🛠️ Engine Internals

- Stateless per run, stateful across a scenario
- The core inference logic is now encapsulated in a pure function (`BeliefSystem._run_inference_chain`).
- Exposes:
  - `step(statement)`
  - `rewind()`
  - `snapshot()`

Later, we can allow interactive stepping, visual flows, and live “what if?” editing.

---

## 🧪 TDD Strategy

- Test rule matching and effect triggering
- Test cumulative world state changes
- Test fork detection and resolution prompts
- Test serialization of simulation log

---

## 🎯 Future Features

- Probabilistic outcomes
- Confidence scores
- Timelines and delayed effects
- Undo/branch history navigation

---

> *"Simulations aren’t just for games. They're for beliefs, too."*