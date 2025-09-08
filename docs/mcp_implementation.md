# MCP Implementation: A Technical Reference

> *"The ghost in the machine needs a physical brain. This document is its blueprint."*

---

## 1. Core Responsibility

The MCP (Memory Control Plane) is the component responsible for managing the lifecycle and persistence of all logical entities in the Fabricator. It acts as an orchestrator and a repository, providing a single, authoritative interface for all state-changing operations.

It is responsible for:
- Creating and managing `BeliefSystem` objects in memory.
- Persisting the state of the logic-space to a Neo4j graph database.
- Ensuring that the relationships between entities (e.g., which simulation used which rule) are correctly stored.

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

Our persistence layer is a graph. We model our world in terms of nodes (the "nouns") and relationships (the "verbs").

### 2.1. Node Labels

*   `(:BeliefSystem)`: A specific, versioned instance of a logic world.
    *   **Properties:** `id`, `name`, `strategy`, `created_at`
*   `(:Rule)`: A single, immutable rule of logic.
    *   **Properties:** `id`, `text_summary`, `condition_json`, `consequences_json`
*   `(:Statement)`: A single, immutable fact, either user-provided or derived.
    *   **Properties:** `id`, `text_summary`, `verb`, `terms_json`, `negated`, `priority`
*   `(:Simulation)`: A record of a single simulation run.
    *   **Properties:** `id`, `timestamp`
*   `(:User)`: An agent (human or otherwise) who authors changes.
    *   **Properties:** `id`, `name`

### 2.2. Relationship Types

*   `(BeliefSystem)-[:CONTAINS]->(Rule)`: Connects a belief system to the rules it includes.
*   `(BeliefSystem)-[:FORKED_FROM]->(BeliefSystem)`: The critical relationship for tracking lineage.
*   `(Simulation)-[:USED]->(BeliefSystem)`: Shows which belief system was used for a simulation.
*   `(Simulation)-[:INTRODUCED]->(Statement)`: Connects a simulation to the initial statements that triggered it.
*   `(Simulation)-[:APPLIED_RULE]->(Rule)`: Records which rules were fired during a simulation.
*   `(Simulation)-[:DERIVED_FACT]->(Statement)`: Connects a simulation to the new facts it produced.
*   `(User)-[:CREATED]->(Rule)`: Tracks authorship.

---

## 4. The MCP API Surface

The `MCP` class provides the primary interface for interacting with the logic-space.

| Operation                               | Description                                                                                                 |
| --------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| `MCP(db_adapter)`                       | Initializes the MCP with a database adapter that conforms to the `DatabaseAdapter` protocol.                |
| `create_belief_system(name, strategy)`  | Spawns a new, empty belief system in memory and persists its node to the graph. Returns the `belief_system_id`. |
| `fork_belief_system(parent_id, name)`   | Clones an existing belief system, creating a new `BeliefSystem` node with a `FORKED_FROM` relationship.         |
| `add_rule(belief_system_id, rule)`      | Adds a `Rule` to a belief system and creates the `CONTAINS` relationship in the graph.                        |
| `simulate(belief_system_id, statements)`| Orchestrates a simulation and records the complete event as a `Simulation` node with all its relationships. |

---

## 5. Implementation Details & Hints

*   **Central Class:** The orchestration logic is encapsulated in the `logic_fabricator.mcp.MCP` class.
*   **Persistence Layer:** All database interaction is handled by classes that implement the `DatabaseAdapter` protocol, such as the `Neo4jAdapter`.
*   **In-Memory Cache:** The `MCP` maintains a dictionary of active `BeliefSystem` objects to avoid unnecessary database lookups.
*   **Stateless Core:** The `BeliefSystem` object itself is a pure, in-memory logic engine. It contains no database connection or persistence logic, making it easy to serialize, copy, and test.
*   **Transactions:** All persistence operations related to a single event (like a simulation) should be wrapped in a single transaction within the database adapter.
*   **UUIDs:** All primary entities (`BeliefSystem`, `Rule`, `Statement`, `Simulation`) must have a unique ID (e.g., UUID) to serve as their primary key in the graph.
