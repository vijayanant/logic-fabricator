# Logic Fabricator — Overview

> *"Everything makes sense once you fabricate the rules."*

Welcome to the Logic Fabricator. This is your quick-start, low-stress, low-formality intro to how everything fits together.

This doc answers the classic question: **"Wait, what exactly *****is***** this thing and how does it work?"**

---

## 🧱 Core Building Blocks

Let’s start with the raw ingredients of fabricated logic:

### 1. **Rules**

Think: statements that define how your logic world works. Written in natural language like:

- "If someone is trusted, their statements gain credibility."
- "Doubt fractures belief."
- "Contradictions don’t invalidate, they mutate."

These get turned into structured logic objects. (Internally: JSON, ASTs, or logic graphs.)

### 2. **Statements**

These are inputs like:

- "Alice trusts Bob."
- "Bob contradicts himself."
- "Alice believes the opposite of what Bob said."

The system checks what happens when you run these *under* your fabricated rules.

### 3. **Belief Systems**

A named set of rules = a logic world. You can fork, mutate, or remix them. Think of it like Git for reasoning.

### 4. **Contradictions**

Not failure! Contradictions are *events*. When a contradiction is detected, you decide:

- Should the belief system fork?
- Should one rule override another?
- Should the contradiction become a story event?

### 5. **Scenarios (Simulations)**

Run a little story under your logic system.

- "Alice trusts Bob."
- "Bob lies."
- "What happens next?"

The system simulates it using your rules.

---

## 🧠 How AI + MCP Fit In

This wouldn’t be possible without some help from our silicon friends:

### 🤖 LLM (AI Language Model)

Used for:

- Turning natural language rules into structured logic
- Explaining what a rule means ("Why did that contradiction occur?")
- Simulating stories and consequences
- Offering suggestions: "Would you like to reframe this rule?"

### 🧠 MCP (Memory Control Plane)

Used for:

- Tracking your belief system over time
- Storing forks and mutations
- Recalling which logic version created which outcome
- Comparing different logic systems ("This belief came from fork A, this one from fork B")

MCP gives us history, context, and continuity. LLM gives us language, creativity, and interpretation.

---

## 🛠️ High-Level Architecture

Here’s how the pieces talk to each other:

```
User Input (natural language rule or scenario)
   ↓
LLM Parser → Structured Logic Object
   ↓
Logic Engine (inference, contradiction check, reasoning)
   ↓
Simulation Engine (run scenario or answer question)
   ↓
LLM Interpreter (explain result)
   ↓
User
```

Meanwhile, MCP tracks the entire session:

- Rules added, removed, or mutated
- Forks and their metadata
- Contradictions and how they were handled

---

## 🔁 Example Flow

Let’s say the user writes:

> "If trust increases, belief becomes stronger."

1. **LLM** parses this into a rule: `trust ↑ → belief confidence ↑`
2. User enters: "Alice trusts Bob. Bob lies."
3. Logic engine applies rules
4. Contradiction is detected: trusted person lied
5. Simulation engine generates: "Alice's belief fractures."
6. LLM explains: "This happened because your logic says trust strengthens belief, but Bob's lie triggered a contradiction."
7. MCP stores this as part of logic version v1.1

The user can now:

- Fork the logic and try a different trust rule
- Modify how contradictions behave
- Simulate again under the new system

---

## 🧭 Mental Models

Here are a few helpful ways to think about the system:

- **Logic is clay.** You mold it, test it, mutate it.
- **Contradictions are plot points.** Not bugs.
- **Simulation is your mirror.** It reflects what your logic *actually* does.
- **Belief systems are software.** And you just became a logic dev.

---

## 🧪 Where This Goes

This doc is your compass, not a spec. It helps you (and future contributors) understand the *shape* of the system.

If you're building the backend: treat this as your intuition layer. If you're writing docs, UIs, or onboarding: this is your tone. If you're a user... congratulations. You're now a logic fabricator.

> *Go forth and contradict yourself. Just make sure to version it.*

