# 🪵 Forking and Contradictions in Logic Fabricator

> *"When the truth splits, so can your logic."*

Forking is one of the core features that makes Logic Fabricator more than just a rules engine. It’s how we explore alternatives, embrace contradictions, and build belief systems that evolve over time.

This doc explains what forks are, when they happen, and how they shape your logic worlds.

---

## 🧠 What Is a Fork?

A **fork** is:

> A new version of a belief system that branches off from an existing one, usually because of a contradiction, uncertainty, or intentional variation in logic.

You can think of a fork as:

- A **Git branch** — but for logic instead of code
- A **parallel universe** — same history, different rules or outcomes
- A **narrative path** — “What if we believed something else instead?”

---

## 🧪 Why Forks Matter

Traditional logic systems treat contradictions as errors.

**Fabricator treats them as events.**

Contradictions don’t halt execution — they trigger *options*:

- Do we revise a rule?
- Do we split reality?
- Do we let the contradiction mutate the belief?

Forks are how we explore these possibilities — cleanly, creatively, and without losing our place.

---

## 🛠️ What a Fork Contains

Each fork is a full, independent logic world. It usually includes:

- A copy of the **rule set** (sometimes mutated)
- A versioned **belief state**
- A **history trace** (via MCP)
- Metadata about:
  - What caused the fork (e.g. contradiction)
  - Who or what triggered it (user? engine?)
  - What changed

Crucially, accepting a contradiction in a fork leads to **divergent inference paths** and subsequent different derived facts within that new logical reality.

Example metadata:

```json
{
  "fork_id": "soft-rationalism-v2",
  "parent_id": "soft-rationalism-v1",
  "diff": ["Rule #7 mutated", "Bob’s trust reduced"],
  "created_by": "contradiction @ t=3",
  "notes": "Bob’s reliability fractured trust chain"
}
```

---

## 🧬 When Forks Happen

Forks can be triggered:

### 🔁 Automatically

- When two rules or beliefs directly contradict
- When simulation hits a logic deadlock

### ✋ Manually

- When the user wants to try an alternate logic
- When LLM suggests a mutation to a rule

### 🤖 Programmatically

- Based on a rule’s own contradiction policy
  - `on_conflict: fork`
  - `on_conflict: revise`

---

## 🧩 Fork vs Mutation vs Version

| Term         | Description                                                |
| ------------ | ---------------------------------------------------------- |
| **Fork**     | A *branch* — creates a new logic world from a previous one |
| **Mutation** | A *change* — what happens inside or after a fork           |
| **Version**  | A *snapshot* — may include forks or just linear updates    |

You can think of versioning as your Git tags, and forking as your branches.

---

## 🎭 Example: Fork in Action

### User Rule:

> "Trusted people are believed automatically."

### Scenario:

```
Alice trusts Bob.
Bob says the moon is cheese.
Bob later says the moon is not cheese.
```

### Contradiction detected! The engine gives options:

🪵 **Fork 1**:

- Bob's trust score is reduced.
- Alice no longer believes him automatically.

🪵 **Fork 2**:

- Contradiction is ignored.
- Belief stays intact (rule is dominant).

🪵 **Fork 3**:

- Rule is mutated to: "Trusted people are believed *until they contradict themselves*."

Now the user can simulate **all three** forks, compare outcomes, and choose what to keep.

---

## 🚀 Why Forking Is Powerful

Forking turns your logic system into:

- A **sandbox** for belief experimentation
- A **versioned model of reasoning**
- A **tool for narrative simulation**

To fully leverage this, future development will include **fork management and navigation tools** for listing, comparing, and switching between different logical branches.

You’re not solving for truth — you’re fabricating meaning.

> *"Contradictions don’t kill logic. They help it evolve."*

Go ahead. Split your beliefs. Fork your world. And simulate the consequences.

