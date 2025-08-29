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
- **Advanced Rule Matching:** Defining `Rules` with complex patterns. The engine can match statements based on their structure, including multiple variables (`?x gives ?y to ?z`) and wildcards (`?speaker says *speech`).
- **Multi-Level Contradiction Detection:** The system identifies and handles direct contradictions between statements, and can also proactively detect latent conflicts between the rules themselves based on their logical implications.
- **Inference Chaining:** A `SimulationEngine` that can process a sequence of statements and chain multiple rules together to derive new facts.
- **World State Effects:** The ability for rules to have `Effects` that directly modify a key-value `world_state`, allowing simulations to track and change state over time.
- **Traceability:** The results of a simulation include a record of which rules were applied to reach the conclusion.
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

---

## 🚀 Usage

Getting started involves four steps. The first step is the most important, as the application will not start without a valid configuration.

### 1. Configure Your Environment

The project requires you to configure your LLM provider settings. All configuration is handled via environment variables, which are loaded from a `.env` file for local development.

First, copy the example template:

```bash
cp .env.example .env
```

Next, edit the `.env` to provide the values for your specific LLM setup. The file contains examples for both local Ollama and OpenAI.
Don't worry, the .env file is already in `.gitignore`.

### 2. Build the Docker Environment

This command builds the Docker image that contains the full environment and all dependencies. You only need to run this once after the initial setup or when dependencies change.

```bash
make build
```

### 3. Run the Tests (Optional but Recommended)

To ensure the logical integrity of the engine and verify your configuration, run the test suite.

```bash
make test
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