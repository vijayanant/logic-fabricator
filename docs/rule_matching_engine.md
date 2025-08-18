# Rule Matching Engine

> \_"How do we know if a rule applies to a statement? Easy — we make it seem easy, but under the hood, it’s gloriously messy."

---

## 🎯 Purpose

The Rule Matching Engine determines whether a given `Statement` falls under the scope of a given `Rule` in a `BeliefSystem`. This is the backbone of evaluating logic in the Logic Fabricator.

---

## 📌 Problem

Rules and statements are written in natural language and must be interpreted flexibly. A rule like:

> "A person trusted by another should be careful."

...should ideally match:

> "Ravi trusts Alice."

But also:

> "Ravi really, really trusts Alice." "Alice is someone Ravi places a lot of faith in."

We can’t rely on strict string equality. Matching must be approximate, contextual, and semantic.

---

## 🧱 Input Structures

```python
class Rule:
    text: str
    verb: str  # Parsed verb (e.g., "trusts")
    modifiers: dict[str, Any]  # Optional qualifiers like confidence, severity

class Statement:
    subject: str
    verb: str
    object: str
    intensity: float | None  # Optional measure of strength (e.g., 0.8)
```

---

## ⚙️ Matching Strategies

### ✅ Phase 1: Exact and Prototype Matching (MVP)

- Match if `statement.verb == rule.verb`
- Optionally: check modifier overlap

Use case:

```python
Rule(verb="trusts")
Statement(subject="Alice", verb="trusts", object="Ravi")
✅ Match
```

### ✅ Phase 2: Advanced Pattern Matching

The engine can match rules based on the entire structure of a statement, including multiple variables and wildcards that consume the rest of the statement.

- **Multi-variable:** A condition like `?x gives ?y to ?z` will correctly bind the three variables.
- **Wildcard:** A condition like `?speaker says *speech` will bind `?speaker` to the first term and `?speech` to a list of all remaining terms.

### 🔜 Phase 3: Synonym & Semantic Matching

- Use LLM or WordNet to allow near-match of verbs
- Map "respects", "has faith in", "believes" to "trusts"

```python
Rule(verb="trusts")
Statement(verb="respects")
✅ Match (via synonym set)
```

### 🔮 Phase 4: Modifier Weighting

- Statement modifiers (like intensity) are checked against rule modifiers
- Allows rules like "If someone strongly trusts someone..."

### 🧠 Phase 5: Embedding Distance (LLM Assisted)

- Generate sentence embeddings for both Rule and Statement
- Match if cosine similarity > threshold
- Useful for highly flexible or creative expressions

---

## 🔁 Output

A match evaluation should return a structure:

```python
RuleMatchResult(
    matched: bool,
    confidence: float,
    explanation: str  # For debugging or user UI
)
```

---

## 🤖 LLM Involvement

Eventually, LLMs will help:

- Normalize rules/verbs into canonical forms
- Explain why a match occurred (or didn’t)
- Suggest refinements to user rules when they’re too vague

But for early development, we’ll stub this logic.

---

## 🧪 TDD Hooks

- Start with `rule.applies_to(statement)` method
- Begin with exact matches only
- Grow complexity one test at a time

> *"If a rule fires in a belief system, and nobody explains why... did it really apply?"*