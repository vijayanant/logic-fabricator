# Memory Control Plane (MCP)

> *"Imagine if Git and your brain had a baby. That’s the MCP."*

---

## 🧠 What is MCP?

The Memory Control Plane (MCP) is the history and versioning brain of the Logic Fabricator. It keeps track of:

- When rules were added or changed
- How belief systems diverged
- What simulations were run, and with what outcomes
- What contradictions were encountered and how they were resolved

Where the logic engine runs simulations, the MCP remembers why and how those simulations changed over time.

---

## 📚 Core Responsibilities

1. **Rule History**

   - Timestamped log of every rule addition, modification, or removal.
   - Tracks origin of rule (user, LLM, simulation).

2. **Belief Lineage**

   - Every belief system gets a unique ID.
   - Forks are tracked — child belief knows its parent.
   - Contradiction points are explicitly logged.

3. **Simulation Records**

   - For every run: what belief system was used, what statements were evaluated, what the outcome was.

4. **Contradiction Metadata**

   - Tied to the belief system and rules involved.
   - Includes resolution path (fork, mutation, override).

---

## 🧾 Data Model Sketch

### `BeliefSystemRecord`

```python
{
  'id': 'belief_main',
  'parent': None,
  'created_at': timestamp,
  'rules': [rule_id_1, rule_id_2],
  'desc': 'Initial logic world',
}
```

### `RuleHistoryEntry`

```python
{
  'rule_id': 'r13',
  'text': 'Alice always trusts Ravi',
  'added_by': 'user',
  'added_at': timestamp,
  'origin_belief': 'belief_main',
  'status': 'active'  # or 'deprecated', 'mutated'
}
```

### `SimulationRecord`

```python
{
  'id': 'sim_001',
  'belief_id': 'belief_main',
  'statements': [...],
  'results': [...],
  'run_at': timestamp
}
```

---

## 🔁 Interaction Points

- Logic Engine logs into MCP during each simulation or rule eval.
- Contradiction Engine updates MCP when forks occur.
- UI or CLI can query MCP to show:
  - All belief branches
  - Recent rule changes
  - Replay of past simulations

---

## 🕹️ Why It Matters

MCP gives our logic world memory, accountability, and structure. Without it, we’re just improvising.

With it, we get:

- Forkable, versioned belief systems
- Replayable simulations
- Debuggable logic trails
- Auditable histories of how and why a belief system evolved

> *"The MCP doesn’t forget. Which is great, because humans do."*

