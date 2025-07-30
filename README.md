# 🧠 Logic Fabricator

> *"Everything makes sense once you fabricate the rules."*

Logic Fabricator is a playground for inventing and simulating custom logic systems — rules you write in natural language that get parsed, interpreted, and evaluated like a little alternate universe.

You define belief systems. You simulate statements. You contradict yourself... *on purpose*. All powered by LLMs and a memory control layer.

---

## 🚧 Project Status

We’re just getting started. This repo is following **strict TDD**, so the codebase will evolve slowly and deliberately. Nothing exists unless a test demands it.

If you're reading this in the early stages: welcome. Expect minimal surface area and maximum weirdness.

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

### 🔨 Build + Test

```bash
make build
```

This builds the Docker image and runs all tests inside the container.

### ✨ Fast Dev (optional)

```bash
make dev
```

Runs the image with your current code mounted — great for quick iterations.

---

## 🦪 Philosophy

- **Tests drive design** — nothing exists until a test proves the need for it
- **Forks are first-class** — contradictions aren't errors, they're decision points
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

## 🧙‍♂️ What Is This Even?

Imagine Prolog had a baby with GPT and raised it on contradiction therapy. That’s what this is.

```python
fabricate("trust fractures when lies propagate")
simulate("Bob lied. Alice trusted Bob.")
```

Boom. A logic engine with a personality.

---

> *"Go forth and contradict yourself. Just make sure to version it."*
