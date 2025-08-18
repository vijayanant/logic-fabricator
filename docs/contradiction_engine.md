# Contradiction Engine

> *"A contradiction isn’t a bug. It’s a fork in the road — and every fork is a feature."*

---

## 🧠 Purpose

The Contradiction Engine is the part of the Logic Fabricator that detects and responds to logical inconsistencies. Rather than halting execution or throwing errors, we embrace contradictions as creative moments — opportunities to branch logic, mutate rules, or question assumptions.

It enables belief systems to diverge, version, and evolve based on conflicting interpretations or outcomes.

---

## 🤹‍♀️ When Contradictions Occur

A contradiction arises when:

- A new rule conflicts with an existing rule.
- A statement evaluated under current rules produces a result that violates an existing belief.
- Two different belief systems produce incompatible outcomes for the same statement.

Contradictions are not failures — they’re moments to fabricate new realities.

---

## 🔍 Detection

The detection of contradictions can be performed at several levels:

### 1. **Rule Conflict Check**

The engine now has the capability to proactively detect latent conflicts between rules, even when their conditions are not identical. This allows the system to identify "Logical Tension" before a specific statement ever triggers a direct contradiction.

-   **Context-Aware Detection:** The engine can be given a set of context rules to find implied conflicts. For example, it can detect a conflict between `is ?x a bird -> can ?x fly` and `is ?x a penguin -> can ?x fly not` if it is also given a third rule, `is ?x a penguin -> is ?x a bird`, which provides the necessary link.
-   **On Insertion (Future):** The next step is to integrate this capability into the `BeliefSystem` itself, so that these checks can be performed automatically when a new rule is added.
-   **Conflict Records:** Detected rule conflicts can be stored as records, allowing the system to be aware of its own internal tensions.

### 2. **Evaluation Mismatch**

- During simulation, a rule may produce a derived statement that directly opposes a previously accepted fact.
- For example: Sim1 concludes "X distrusts Y" based on new rules, but Sim0 had "X trusts Y".

### 3. **Fork Watchdog**

- Each BeliefSystem tracks its rule lineage.
- Contradiction = signal to branch, not break.

---

## 🛠️ Handling Strategy

When a contradiction is detected, the system can:

### Option 1: **Fork**

- Create a new BeliefSystem branching from the current one.
- Label the fork (e.g., `after_ravi_was_betrayed`).
- Apply the conflicting rule or statement only to the new branch.

### Option 2: **Mutate**

- Prompt the user to rephrase or refine the contradicting rule.
- Optionally involve LLMs to suggest resolutions.

### Option 3: **Override**

- Let the user choose which rule takes precedence.
- The older rule may be deprecated or marked as superseded.

---

## 📦 Data Structures

### ContradictionRecord

```python
{
  'rule_a': Rule,
  'rule_b': Rule,
  'detected_at': timestamp,
  'belief_id': str,
  'resolution': Optional[str]  # 'forked', 'mutated', 'overridden', etc.
}
```

---

## 🤖 Role of LLM

- Detect semantic contradictions not easily catchable by rule text alone.
- Propose explanations or fork names.
- Assist in auto-mutation or rewriting rules to soften or qualify.

---

## 🌀 Why It Matters

Contradictions reflect the complexity of human logic and belief. By treating them as branching points instead of bugs, we unlock:

- Multiple perspectives
- Versioned logic spaces
- Narrative-driven reasoning

> *"Contradiction is not a failure of logic. It's a reminder that the world isn’t flat."*