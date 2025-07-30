# Logic Fabricator: MCP Design Notes

> *"Logic without memory is just noise. MCP is the brain that remembers why we believed what we did."*

---

## 🧠 What is MCP?

MCP (Memory Control Plane) is the component responsible for **tracking belief system history**, including:

- Which rules exist in which belief system.
- What happened when a contradiction was encountered.
- How belief systems evolved via forks or mutations.
- What simulation results were produced under each version.

In essence, it’s Git for fabricated logic.

---

## 🔍 Why Do We Need MCP?

Without MCP:
- Users wouldn’t know which rule led to a simulation result.
- Contradictions would just overwrite prior assumptions.
- Evolution of belief systems would be ad hoc and lossy.

With MCP:
- Every belief system has a version.
- Contradictions become forks, not bugs.
- Users can roll back, compare branches, and trace logic ancestry.

---

## 🧱 Core Concepts

### 📄 Belief System
A named set of rules.
- Has a unique ID.
- Points to a parent (if forked).
- May have metadata like user, purpose, tags.

### 🔄 Fork
When a contradiction or intentional mutation happens:
- A new belief system is created.
- It inherits rules from the parent.
- The change is tracked as a diff.

### 📚 Rule History
Each rule tracks:
- Who added it
- When
- Whether it was mutated or removed in any fork

### 📜 Simulation Log
Every time a scenario is run:
- MCP stores:
  - Input statements
  - Belief system used
  - Derived consequences
  - Contradictions encountered

---

## 🧭 MCP Operations

### `create_belief_system(name, parent_id=None)`
- Starts a new belief system.
- Optionally forks from an existing one.

### `add_rule(belief_id, rule)`
- Adds a rule to a belief system.
- Records timestamp and author.

### `fork_belief_system(base_id, mutation)`
- Forks a belief system due to contradiction or user choice.
- Applies mutation (e.g. altered rule or resolution strategy).

### `record_simulation(belief_id, input_statements, output)`
- Logs the simulation under a specific belief version.

---

## 🧠 Visual Metaphor
Imagine a branching tree:
- Each node = belief system
- Each edge = rule change or contradiction
- Each leaf = snapshot of what someone once believed

MCP is the map of that forest.

---

## 🛠️ Implementation Hints
- Likely a central `BeliefGraph` class
- Underlying storage can be in-memory (for now), with future support for:
  - JSON export
  - Git-backed storage
  - Time-travel queries
- Use UUIDs for belief system identity
- Allow tagging, naming, and notes on forks

---

## 🧪 Test Philosophy
- All fork behavior must be test-driven
- Simulations must produce auditable logs
- Forks should preserve ancestry
- Deleting a rule in a fork should not affect the parent

---

> *"You don’t have to remember why everything happened. That’s MCP’s job."*

