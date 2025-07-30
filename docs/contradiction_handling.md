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

## 🧭 Contradiction Resolution Options

### 🧵 1. **Fork Belief System** (default)

- Clone the current belief system into two branches:
  - One where Rule A wins
  - One where Rule B wins
- Both realities now evolve independently.

```text
belief_main
├── belief_access_granted
└── belief_access_denied
```

### 🙋 2. **User Override**

- Prompt the user to manually resolve the contradiction
- Choose one rule to suppress or discard

### 🔄 3. **Rule Mutation**

- User modifies a rule to narrow its scope or fix the ambiguity
- Example: Add a qualifier to Rule A like "only if verified"

### 🧠 4. **LLM Explanation**

- LLM explains what the contradiction is, and how rules are clashing
- May suggest rewrite candidates or rule grouping

---

## 🏗️ Data Representation

```python
class Contradiction:
    statement: Statement
    conflicting_rules: list[Rule]
    belief_version: str
    suggested_resolutions: list[str]  # Optional, LLM filled
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

