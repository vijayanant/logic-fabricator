# LLM Parser

> *"The humans speak. The LLM listens. And then fabricates structure out of the mess."*

---

## 🧠 Role of the LLM Parser

The LLM Parser is our bridge between natural language and structured logic. It takes:

- User-defined rules (e.g. "Trust is lost if someone lies.")
- Narrative statements (e.g. "Ravi lied to Alice.")

...and turns them into structured, evaluatable logic objects.

Unlike traditional parsers, this one embraces ambiguity, negotiates meaning, and gives us back structured forms — sometimes with a shrug.

---

## 🔄 Input/Output Examples

### Input Rule:

```text
"Alice always trusts Ravi unless he lies."
```

### Parsed Output:

```python
{
  'subject': 'Alice',
  'verb': 'trusts',
  'object': 'Ravi',
  'modifiers': ['always'],
  'exceptions': ['if Ravi lies']
}
```

### Input Statement:

```text
"Ravi lied to Alice."
```

### Parsed Output:

```python
{
  'subject': 'Ravi',
  'verb': 'lied_to',
  'object': 'Alice'
}
```

### Current Capabilities of Structured Logic

Our internal `Statement` and `Condition` objects are more expressive than these simple examples. They support:

- **Statement Negation:** Statements can be explicitly negated (e.g., `is sky blue not`).
- **Statement Priority:** Statements can carry a priority value, used in contradiction resolution.
- **Conjunctive Conditions:** Rule conditions can be composed of multiple sub-conditions that must all be met (`AND` logic).
- **Advanced Pattern Matching:** Rule conditions support multi-variable binding and wildcard matching (as described in `docs/engine_features.md`).

---

## ⚙️ Functional Goals

1. **Extract Triples**: Subject / Verb / Object from statements.
2. **Decompose Rules**: Pull out qualifiers, conditions, frequency, exceptions.
3. **Normalize Language**: Map "lies", "lied", "tells untruths" to a normalized form.
4. **Link Rules to Statements**: Ensure statements can be matched to applicable rules.

---

## 🛠️ Under the Hood (Planned)

- Uses OpenAI/Anthropic LLMs or local alternatives (via API).
- Prompting templates based on the type of input.
- Caching responses for deterministic development cycles.
- Add "explanation mode" to help debug parsing output.

---

## 🤹 Edge Cases and Judgment Calls

- Some rules are vague. LLM may return partial or fuzzy structure.
- When unsure, LLM flags a confidence level.
- User can accept, override, or mutate the structure.
- Future: train on our own data for better consistency.

---

## 📌 Why We Use LLMs (Instead of Writing a Grammar)

- Natural language is messy.
- Traditional parsing can’t handle ambiguity or context.
- LLMs give us a high-level understanding, not just syntax trees.
- Users write rules how *they* think, not how we want them to.

> *"It’s not just parsing. It’s interpretive dance with tokens."*