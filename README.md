[![Build and Test](https://github.com/vijayanant/logic-fabricator/actions/workflows/ci.yml/badge.svg?branch=master)](https://github.com/vijayanant/logic-fabricator/actions/workflows/ci.yml)

# 🧠 Logic Fabricator

> *"Everything makes sense once you fabricate the rules."*

Logic Fabricator is a playground for inventing and simulating custom logic systems — rules you define in natural language that are parsed, interpreted, and evaluated by a **deterministic logic engine**, like a little alternate universe.

You define belief systems. You simulate statements. You embrace contradictions... *on purpose*. All underpinned by a **symbolic reasoning core** and a memory control layer.

---

## 🚧 Project Status

The core logic engine is now functional and taking shape. While we are still in the early stages of fabrication, the foundational components are in place.

This repo follows **strict TDD**, so the codebase evolves slowly and deliberately. Nothing exists unless a test demands it.

### ✨ Current Capabilities

The core logic engine is now functional. It currently supports:

- **Natural Language Workbench:** An interactive REPL where rules and statements are provided in plain English, parsed by an LLM into structured logic.
- **Advanced Rule Matching:** Defining `Rules` with complex patterns. The engine can match statements based on their structure, including multiple variables (`?x gives ?y to ?z`), wildcards (`?speaker says *speech`), and now supports **recursive conditions** with `AND` and `OR` logic.
- **Multi-Level Contradiction Detection:** The system identifies and handles direct contradictions between statements, and can also proactively detect latent conflicts between the rules themselves based on their logical implications.
- **Inference Chaining:** A `SimulationEngine` that can process a sequence of statements and chain multiple rules together to derive new facts.
- **World State Effects:** The ability for rules to have `Effects` that directly modify a key-value `world_state`, allowing simulations to track and change state over time.
- **Persistent & Queryable History:** The full causal chain of every simulation is recorded in a graph database. This includes the specific `BeliefSystem` (identified by its unique ID) used, the initial statements, the rules that were applied, and all derived facts, creating a complete, auditable history of logical events.
- **Contradiction Forking:** When a contradiction is detected, the system can create a new, divergent belief system (a "fork") to explore alternative logical realities.

---

## 🛠️ Dev Setup

We use:

- 🐍 Python (managed via [Poetry](https://python-poetry.org/))
- 🐳 Docker for isolated builds and testing
- 🧪 Pytest for test-driven development
- 🛠️ Makefile for common workflows

### 🔧 Requirements

- [Docker](https://docs.docker.com/get-docker/)
- [Poetry](https://python-poetry.org/docs/#installation)
- [Neo4j](https://neo4j.com/download/) (Community Edition is sufficient)

---

## 🚀 Usage

Getting started involves four steps. The first step is the most important, as the application will not start without a valid configuration.

### 1. Configure Your Environment

The project requires you to configure your LLM provider settings. All configuration is handled via environment variables, which are loaded from `.env.dev` for development and `.env.test` for testing.

First, copy the example templates for both development and testing environments:

```bash
cp .env.dev.example .env.dev
cp .env.test.example .env.test
```

Next, edit both `.env.dev` and `.env.test` to provide the values for your specific LLM and database setup. The example files contain configurations for local Ollama, OpenAI, and Neo4j.
(Note: The test environment is configured to clear the database on each run.)
Don't worry, these `.env` files are already in `.gitignore`.


### 2. Build the Docker Environment

This command builds the Docker image that contains the full environment and all dependencies. You only need to run this once after the initial setup or when dependencies change.

```bash
make build
```

### 3. Run the Tests (Optional but Recommended)

To ensure the logical integrity of the engine and verify your configuration, run the test suite.

```bash
make test-unit      # Runs unit tests (fast, isolated, uses mock database)
make test-integration # Runs integration tests (slower, uses real Neo4j database)
```

### 4. Launch the Workbench

This is the main event. This command starts the interactive REPL, allowing you to fabricate and explore your own belief systems.

```bash
make run
```

### Example Workbench Session

Once inside the workbench (`make run`), you can fabricate your own reality. Here's an example that shows inference chaining (a derived fact) and a world state effect.

```
>> rule if ?x is a man then ?x is mortal

++ Fabricated Rule: Rule: IF (?x is a man) THEN ((is ?x mortal))

>> rule if ?x is mortal then increment mortal_count by 1

++ Fabricated Rule: Rule: IF (?x is mortal) THEN (Effect: increment world_state.mortal_count to 1)

>> sim socrates is a man

... Simulating: is socrates a man

--- Simulation Report ---
  >> Derived Facts:
     - (is socrates mortal)
  >> World State Changes:
     - mortal_count: None -> 1

>> state
--- World State ---
  mortal_count: 1
```

### Example: Embracing Disjunction (OR Logic)

The Fabricator now understands complex conditions with 'OR' logic. It automatically decomposes such rules into simpler ones for the core engine.

```
>> rule if ?x is a king and (?x is wise or ?x is brave), then ?x is a good_ruler

++ Fabricated Rule: Rule: IF ((is ?x king) & (is ?x wise)) THEN ((is ?x good_ruler))
++ Fabricated Rule: Rule: IF ((is ?x king) & (is ?x brave)) THEN ((is ?x good_ruler))

>> sim Chandragupta is a king
>> sim Chandragupta is wise

... Simulating: is Chandragupta king
... Simulating: is Chandragupta wise

--- Simulation Report ---
  >> Derived Facts:
     - (is Chandragupta good_ruler)
      >> World state is unchanged.

>> reset

>> rule if ?x is a king and (?x is wise or ?x is brave), then ?x is a good_ruler

++ Fabricated Rule: Rule: IF ((is ?x king) & (is ?x wise)) THEN ((is ?x good_ruler))
++ Fabricated Rule: Rule: IF ((is ?x king) & (is ?x brave)) THEN ((is ?x good_ruler))

>> sim Chandragupta is a king
>> sim Chandragupta is brave

... Simulating: is Chandragupta king
... Simulating: is Chandragupta brave

--- Simulation Report ---
  >> Derived Facts:
     - (is Chandragupta good_ruler)
      >> World state is unchanged.
```

---

## ✨ Ideas for Fabrication

> **Note:** The ideas below represent the *vision* and *potential* of the Logic Fabricator. While the core engine is functional, not all advanced scenarios are fully implemented yet. These are meant to inspire your experimentation and highlight where the project is headed!

The Logic Fabricator is a creative playground. Here are some ideas for how you can use it to explore logic, build worlds, or just have fun:

*   **Simulate Fictional Universes:** Define the core rules of a fantasy world, a sci-fi society, or a magical system. Then, introduce statements and see how your fabricated logic dictates events.
*   **Explore Ethical Dilemmas:** Fabricate rules based on different ethical frameworks (e.g., utilitarianism, deontology). Simulate scenarios to see how each framework resolves conflicts or makes decisions.
*   **Model Social Dynamics:** Define rules for trust, reputation, or influence within a group. Simulate interactions to observe how relationships evolve or conflicts arise.
*   **Design Game Mechanics:** Use the system to prototype rule sets for board games, role-playing games, or even video games. Test how different rules interact and affect gameplay outcomes.
*   **Debate and Argumentation:** Define the logical premises of a debate. Introduce arguments as statements and see where contradictions emerge, forcing a fork in the logical reality.
*   **Personal Belief Systems:** Explore your own internal logic. What happens when two of your deeply held beliefs contradict? Use the forking mechanism to understand the implications.

The possibilities are as boundless as your imagination. Go forth and fabricate!

---

## 🦪 Philosophy

A useful metaphor for this project comes from *Tron: Legacy*. The ISOs were emergent, unpredictable beings in a perfectly structured grid. The system's rigid administrator, CLU, saw them as imperfections and sought to purge them.

**Logic Fabricator is an attempt to build a system that does the opposite.**

We believe the most interesting, creative, and powerful logic often comes from ambiguity and contradiction—the very things a "perfect" system would reject. Our goal is not to build a flawless grid, but to create a playground that embraces its ISOs, treating them as features, not bugs.

This leads to a few core tenets:

- **Tests drive design** — nothing exists until a test proves the need for it
- **Forks are first-class** — contradictions aren't errors, they're creative events
- **Logic is clay** — mutable, forkable, explorable
- **Belief systems are software** — and you're the reasoner-in-chief

---

## 🤝 Contributing

If you're curious about the internals, read the following first:

- [`logic_fabricator_brief.md`](./docs/logic_fabricator_brief.md)
- [`fabricator_overview.md`](./docs/fabricator_overview.md)
- [`forking_and_contradictions.md`](./docs/forking_and_contradictions.md)

Contributions welcome! But keep it chill, weird, and test-driven.

---

> *"Go forth and contradict yourself. Just make sure to version it."*