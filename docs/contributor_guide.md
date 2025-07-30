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
make build     # Builds the Docker image
make test      # Runs tests inside the container
```

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
│       ├── rule.py
│       ├── statement.py
│       ├── belief_system.py
│       └── ...
├── tests/
│   └── test_rule.py
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
Add first test for Rule.match()

- Introduced a test for checking verb matching
- Added minimal logic to pass test (hardcoded verb)
- All green, no refactor needed yet
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

- `docs/logic_fabricator_brief.md`
- `docs/architecture.md`
- `docs/mcp_design.md`
- `docs/simulation_engine.md`

Then branch out from there. Like the belief systems, this doc world is forkable.

---

Happy fabricating!

