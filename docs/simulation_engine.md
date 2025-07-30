# Simulation Engine

> *"Let’s press play on logic space."*

---

## 🎯 Purpose

The Simulation Engine processes a sequence of natural-language statements within a BeliefSystem. It evaluates each statement against the active rules, determines consequences, detects contradictions, and records the evolution of logic.

Think of it as a turn-based logic interpreter — like running a story through a brain made of belief.

---

## 🧪 What It Simulates

- **Statements**: Inputs like "Ravi trusts Alice" or "Anyone who is trusted may speak."
- **Rules**: The belief system’s logic (structured by LLM or the user)
- **State**: Any persistent derived values (trust levels, access flags, outcomes)

---

## 🔄 Core Loop (MVP)

1. **Input Statement** (natural language)
2. **Structure Statement** (LLM or parser)
3. **Check Applicable Rules**
4. **Evaluate Statement**
   - Match against rules
   - Apply consequences
   - Record new derived facts (optional)
5. **Check for Contradictions**
   - If found: pause, fork, or escalate
6. **Record All Activity** in MCP

---

## 📦 Input Format (Eventually)

```python
Statement(
  text="Ravi trusts Alice",
  subject="Ravi",
  verb="trusts",
  object="Alice"
)
```

These are run sequentially through a `BeliefSystem.simulate()` method.

---

## 🧠 Output

Simulation returns a result object with:

```python
class SimulationResult:
    applied_rules: list[Rule]
    derived_facts: list[Statement]
    contradictions: list[Contradiction]
    forked_beliefs: list[BeliefSystem]  # if applicable
    trace_log: list[str]                # human-readable narrative
```

This lets us:

- Show the user what logic was triggered
- Let LLMs generate an explanation
- Persist outcomes for future branching

---

## 🛠️ MVP Behavior

For the MVP:

- One statement at a time
- Simple rule matching (verb == verb)
- One belief system only
- Contradictions result in immediate forks (or errors)

Later:

- Batch statements
- Run scenarios with different forks
- Visual traces or timelines

---

## 🤝 Integration Points

- **Rule Engine**: Uses `Rule.applies_to(statement)` to determine applicability.
- **Contradiction Engine**: Handles any conflict that emerges mid-simulation.
- **MCP**: Stores simulation results, versions, and forks.
- **LLM**: Parses statement, suggests rule interpretations, explains outcomes.

---

## 🧪 Example Flow

```text
Input: "Ravi trusts Alice"

✔️ Matches Rule 1: "If X trusts Y, then grant Y access"
→ Derived: "Alice has access"

✔️ Matches Rule 2: "Nobody unverified gets access"
→ Contradiction detected
→ Fork into: belief_grants_access / belief_denies_access
→ Both beliefs now diverge
```

---

## 🏗️ Next Steps

1. Implement a basic `simulate(statement)` method in BeliefSystem
2. Structure the return object with traceability in mind
3. Add contradiction detection
4. Later: batch simulation, branching scenarios, and user-facing visual logs

> *"The future doesn’t unfold. It’s simulated."*

