# Fork Evolution and Simulation

> *"Logic may fork, but it never forgets."*

This document explains how forked belief systems behave during simulation inside Logic Fabricator.

---

## 🔁 What Happens When You Simulate a Belief System?

When you call `belief_system.simulate(input)`:

1. The **main belief system** processes the input.
2. The engine checks if this belief system has **forks**.
3. If forks exist, the **same input** is sent to each fork.
4. Each fork **processes the input independently**, based on its own state.
5. New forks may be created if new contradictions arise.

---

## 🌱 Forks Are Living Timelines

Forks are not dead ends or snapshots. They are alternate logical realities that continue to evolve.

- Every fork has the full simulation capability.
- Forks can diverge further.
- Forks can fork. (Yes, forks fork. It's the logic multiverse.)

---

## 📦 Example Structure (Before and After)

Initial Belief System:

```
BeliefSystem A
```

After contradiction:

```
BeliefSystem A
├── Fork A1
└── Fork A2
```

After simulating a new input:

```
BeliefSystem A
├── Fork A1
│   └── Fork A1a (if contradiction)
└── Fork A2
    └── Fork A2a (if contradiction)
```

---

## 🧠 Why Simulate All Forks?

Simulating all forks ensures:

- No reality is left behind.
- Every belief path is logically complete.
- You can compare how different contexts handle the same input.

This also supports higher-order reasoning:

- Which fork is more consistent?
- Which belief path leads to contradictions sooner?
- What does this say about the original assumptions?

---

## 👤 What Does the User Control?

- You can **inspect forks** and compare them.
- You can **abandon** forks you don’t care about.
- You can **promote** a fork to become the new mainline.
- You can **ignore them all** and keep simulating the original.

---

## 🧭 Summary

- Simulation always applies to all active forks.
- Forks evolve independently from the point they split.
- The user decides what forks matter.
- The engine just makes sure nothing is lost.

> *"It’s not a bug. It’s an alternate belief system."*

