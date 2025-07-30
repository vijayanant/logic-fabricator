# MCP (Memory Control Plane) Design

> *"Because your logic deserves a better memory than your brain can offer."*

---

## 🧠 What is MCP?

MCP is the memory system behind Logic Fabricator. It tracks every logic edit, contradiction, and simulation result. Think of it as a cognitive Git system for reasoning.

Where your brain forgets, MCP remembers — forks, revisions, deleted rules, and all.

---

## 📚 What MCP Stores

1. **Rules:**

   - Rule content and structure
   - Metadata (author, timestamp, belief system name, etc.)
   - Source text vs parsed object

2. **Statements:**

   - What was said, when, and by whom
   - Result of evaluation
   - Which belief system was active at the time

3. **Belief Systems:**

   - Named logic spaces (e.g., "TrustTest v1")
   - Rule sets and forks
   - Version history

4. **Contradictions:**

   - Detected clashes between rules
   - Rule versions involved
   - Resolution strategy chosen (fork, override, ignore)

5. **Simulations:**

   - Sequence of statements processed
   - Derived consequences
   - Logs of decision paths

6. **Users / Authors:**

   - Identity optional
   - Used to track intent or explain changes

---

## 🌳 Structure and Format

Internally, MCP is just structured data.

- Format: JSON, SQLite, or graph DB (depending on needs)
- Top-level concepts: `rule`, `statement`, `belief`, `fork`, `simulation`, `contradiction`
- Every entry has a UUID

### Example Entry: Rule

```json
{
  "id": "rule-94ac",
  "text": "Never trust a liar",
  "parsed": { "verb": "trust", "negate": true, "object": "liar" },
  "added_by": "user123",
  "timestamp": "2025-07-30T14:32:22Z",
  "belief_system": "TrustBase"
}
```

---

## 🧬 Versioning and Forking

Each belief system can:

- **Fork:** clone itself into a new name/version
- **Mutate:** add/remove/replace rules
- **Track Lineage:** remember who/what/why a version changed

Forks aren’t just copies — they’re creative divergences in logic-space.

---

## ⛓️ Linking Everything

All parts of MCP are interlinked:

- Rules reference statements they applied to
- Simulations list the rules they used
- Contradictions record both offending rules
- Belief systems store active and deprecated rules

---

## 🔧 MCP API Surface (Planned)

| Operation                 | Example                                   |
| ------------------------- | ----------------------------------------- |
| `add_rule()`              | Adds structured or raw rule text          |
| `record_statement()`      | Logs a user assertion + evaluation result |
| `create_belief_system()`  | Spawns a new empty belief space           |
| `fork_belief_system()`    | Clones a belief system                    |
| `log_simulation()`        | Records a full simulation run             |
| `resolve_contradiction()` | Marks a contradiction as resolved         |

---

## 🧠 Why Not a Simple Log?

We want traceability and interpretability. Not just “what happened” — but:

- Why did this rule win?
- What else could have happened?
- How did logic evolve over time?

This makes MCP essential for debugging logic, exploring alternate realities, and co-developing with LLMs.

---

## 🚧 Future Extensions

- GraphQL interface
- Visualization of belief forks and rule evolution
- Live commentary of simulations (AI-powered)
- Cross-belief comparisons

---

> *"MCP doesn’t just remember. It helps you forget responsibly."*

