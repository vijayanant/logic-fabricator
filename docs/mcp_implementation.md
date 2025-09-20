# MCP Implementation: A Technical Reference

> *"The ghost in the machine needs a physical brain. This document is its blueprint."*

---

## 1. Core Responsibility

The MCP (Memory Control Plane) is the component responsible for managing the lifecycle and persistence of all logical entities in the Fabricator. It acts as an orchestrator and a repository, providing a single, authoritative interface for all state-changing operations.

It is responsible for:
- Creating and managing `BeliefSystem` objects in memory.
- Persisting the state of the logic-space to a Neo4j graph database.
- Recording the full causal chain of every simulation event.

---

## 2. The Database Adapter: A Decoupled Persistence Layer

The MCP does not talk directly to a database. Instead, it communicates through the `DatabaseAdapter` protocol, a formal interface that defines a set of methods for persisting and retrieving logical entities.

This design decouples the MCP's core orchestration logic from the specific details of any one database. The primary implementation is the `Neo4jAdapter`, which translates the adapter's methods into Cypher queries for the Neo4j graph database. For testing, a `MockAdapter` is used, which simulates the database in memory.

This approach provides several key benefits:
- **Testability:** The MCP can be unit tested without a live database connection.
- **Flexibility:** The system could be adapted to use a different database in the future by creating a new class that implements the `DatabaseAdapter` protocol.
- **Separation of Concerns:** The MCP focuses on high-level orchestration, while the adapters handle the low-level details of database interaction.

--- 

## 3. The Neo4j Graph Schema: Nouns and Verbs of Memory

Our persistence layer is a graph that models our world in terms of nodes (the "nouns") and relationships (the "verbs"). A core principle of this schema is the **canonical representation of logic**: every unique `Statement` and `Rule` exists as only one node in the database, identified by its content.

### 3.1. Node Labels

*   `(:BeliefSystem)`: A specific, versioned instance of a logic world. A "branch" in our logic-space.
    *   **Properties:** `id`, `name`, `strategy`, `created_at`
*   `(:Rule)`: A single, canonical, and immutable rule of logic.
    *   **Properties:** `id`, `condition_json`, `consequences_json`. The node is uniquely identified by its JSON content properties.
*   `(:Statement)`: A single, canonical, and immutable fact, either user-provided or derived.
    *   **Properties:** `id`, `verb`, `terms_json`, `negated`, `priority`. The node is uniquely identified by its content properties (verb, terms, negation).
*   `(:Simulation)`: A record of a single simulation run, capturing the entire event.
    *   **Properties:** `id`, `timestamp`
*   `(:User)`: An agent (human or otherwise) who authors changes. (Future implementation)
    *   **Properties:** `id`, `name`

### 3.2. Relationship Types

*   `(BeliefSystem)-[:CONTAINS]->(Rule)`: Connects a belief system to the canonical rules it includes.
*   `(BeliefSystem)-[:CONTAINS]->(Statement)`: Connects a belief system to the canonical facts it holds true. (Note: This is part of the `BeliefSystem` state, persisted via simulation results).
*   `(BeliefSystem)-[:FORKED_FROM]->(BeliefSystem)`: The critical relationship for tracking lineage.
*   `(Simulation)-[:USED]->(BeliefSystem)`: Shows which belief system was used for a simulation.
*   `(Simulation)-[:INTRODUCED]->(Statement)`: Connects a simulation to the initial, canonical statements that triggered it.
*   `(Simulation)-[:APPLIED_RULE]->(Rule)`: Records which canonical rules were fired during a simulation.
*   `(Simulation)-[:DERIVED_FACT]->(Statement)`: Connects a simulation to the new, canonical facts it produced.

---

## 4. The MCP API Surface

The `MCP` class provides the primary interface for interacting with the logic-space.

| Operation                               | Description                                                                                                 | Status |
| --------------------------------------- | ----------------------------------------------------------------------------------------------------------- | :---: |
| `MCP(db_adapter)`                       | Initializes the MCP with a database adapter.                | ✅ |
| `create_belief_system(name, strategy)`  | Spawns a new, empty belief system and persists its node. | ✅ |
| `fork_belief_system(parent_id, name)`   | Clones an existing belief system, creating a `FORKED_FROM` relationship.         | ✅ |
| `add_rule(belief_system_id, rule)`      | Adds a `Rule` to a belief system, creating the node and relationship.                        | ✅ |
| `simulate(belief_system_id, statements)`| Orchestrates a simulation and **persists the complete event** as a `Simulation` node with all its causal relationships. | ✅ |
| `get_simulation_history(...)` | Retrieves the history of simulation events for a belief system. | ✅ |

---

## 5. Implementation Details & Hints

*   **Canonical Nodes:** The `Neo4jAdapter` uses `MERGE` on the content of `Statement` and `Rule` objects (`verb`, `terms_json`, `condition_json`, etc.) to ensure that only one node ever exists for each unique piece of logic. The `id` property is set `ON CREATE`.
*   **Stateless Core:** The `BeliefSystem` object itself is a pure, in-memory logic engine. It contains no database connection or persistence logic, making it easy to serialize, copy, and test.
*   **Transactions:** All persistence operations related to a single event (like a simulation or adding a rule) are wrapped in a single transaction within the database adapter, ensuring atomicity.
*   **UUIDs:** All primary entities (`BeliefSystem`, `Rule`, `Statement`, `Simulation`) have a unique `id` property that is assigned on creation in Python and then persisted to the graph.