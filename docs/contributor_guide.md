# Contributor Guide

> *“Welcome to the logic factory. Rules are made up. Points do matter.”*

This guide is for human developers, curious agents, and future fabricators. It covers how to contribute to Logic Fabricator, how our dev setup works, and how we evolve the system — strictly via tests.

---

## 🛠 Dev Setup (Quick Summary)

- **Language:** Python 3.11+
- **Dependency Manager:** Poetry
- **Environment:** Docker (Poetry + Python inside container)
- **Editor:** Your choice — but code runs/tests inside Docker
- **Tests:** `pytest`

### 🧪 Running It

```bash
make build          # Builds the Docker image
make test-unit      # Runs unit tests inside the container (excluding LLM and DB tests)
make test-integration # Runs integration tests inside the container (excluding LLM tests)
```

**Note on Database:** This project utilizes Neo4j. The `docker-compose.yml` sets up separate Neo4j instances for development and testing environments, which are automatically managed when using `docker compose` commands.

Thanks to volume mounts in `docker-compose.yml`, there's no need to rebuild after every code change. The container always sees your latest files.

---

## 🧪 Test-Driven Design (TDD) Rules

- Write a **test first** to express what you expect.
- Add just enough code to make it pass.
- Refactor **only after** the test is green.
- Commit after every red → green → refactor cycle.
- Use **descriptive test names** and keep tests small.

> *“The test should ask for what doesn’t exist. Your code politely obliges.”*

---

## 🧱 Project Structure

```
logic-fabricator/
├── src/
│   └── logic_fabricator/
│       └── fabric.py  # All core logic classes (Rule, Statement, BeliefSystem, etc.)
├── tests/
│   └── test_fabric.py # All unit and integration tests
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml
└── Makefile
```

---

## 🚥 Commit Guidelines

We follow a commit style that’s:

- On-brand and fun (fabricated flavor encouraged)
- Informative (what was added/tested/fixed)
- Multi-line messages (for anything non-trivial)

Example:

```
feat(rules): Fabricate wildcard matching in conditions

This commit teaches the rule matching engine to understand wildcards,
allowing a rule to capture a variable number of terms from a statement.

A condition term prefixed with `*` (e.g., `*speech`) will now match
all remaining terms in a statement, binding them as a list to the
corresponding variable (e.g., `?speech`).
```

---

## 🧠 Contributing Logic (Not Just Code)

This isn’t a CRUD app — it’s a logic engine. So when adding functionality, ask:

- What kind of rules should this support?
- How should contradictions be handled?
- Should this evolve the belief system or fork it?
- Does this need LLM help later?

> *“You’re not just writing code. You’re constructing logic space. Be kind to future fabricators.”*

---

## 🧾 Related Docs

If you’re new to the project, check these out first:

- [`docs/logic_fabricator_brief.md`](./docs/logic_fabricator_brief.md)
- [`docs/architecture.md`](./docs/architecture.md)
- [`docs/engine_features.md`](./docs/engine_features.md) # New: Comprehensive list of engine capabilities
- [`docs/mcp_philosophy.md`](./docs/mcp_philosophy.md)
- [`docs/mcp_implementation.md`](./docs/mcp_implementation.md)
- [`docs/simulation_engine.md`](./docs/simulation_engine.md)

Then branch out from there. Like the belief systems, this doc world is forkable.

---

Happy fabricating!