# LLM Integration Plan for Logic Fabricator

> *"When your logic starts speaking a little too much like a human... that's probably the AI translator at work."*

---

## 🧠 Why LLMs?

Humans don’t think in rigid logical syntax. They say things like:

> "If someone always lies, don’t trust them."

This isn’t parseable by your average `if-else` clause. But an LLM can help turn such squishy phrasing into structured, executable logic.

Our plan isn’t to make LLMs *run* logic — but to make them *understand* and *translate* it into forms the simulation engine can execute.

---

## 🪄 What LLMs Will Do

1. **Rule Parsing:**

   - Convert user-written natural language rules into structured objects: `{subject, verb, object, conditions, modifiers}`
   - Normalize verb tense, synonyms, ambiguous modifiers
   - Annotate with likely logic type (e.g., binary, scalar, fuzzy, temporal)

2. **Contradiction Explanation:**

   - Given a conflict in two rules or derived conclusions, generate a human-readable explanation
   - Offer soft fixes (e.g., relaxing conditions, scope)

3. **Statement Disambiguation:**

   - Interpret vague or poorly-formed assertions and request clarification if needed

4. **Rule Suggestion (Advanced):**

   - Suggest potential follow-up rules or missing constraints
   - Help users grow belief systems with semantically consistent logic

5. **Simulation Narration:**

   - Summarize what happened during a simulation run
   - Explain consequences in plain terms

---

## 🛠️ Implementation Plan

### Phase 1: Offline, Assistive

- LLM is called manually via dev tools (e.g. CLI command or playground interface)
- Returns JSON-compatible structured rule object
- Devs or power users review before injecting into belief system

### Phase 2: Interactive, Semi-Automated (✅ Completed)

- User pastes rules; LLM auto-parses and shows preview
- User accepts or tweaks parsed version
- Simulation explanations show up post-run

### Phase 3: Embedded Co-Pilot

- LLM operates behind-the-scenes:
  - auto-parsing rules
  - warning of contradictions
  - generating explainer blurbs
- Power users can still override or edit

---

## 🧩 Format Output Example

User Rule:

> "Never trust a liar unless they've saved your life."

LLM Output:

```json
{
  "verb": "trust",
  "subject": "*",  
  "object": "liar",
  "condition": {
    "unless": "object.saved(subject.life) == true"
  },
  "negate": true
}
```

---

## 🚧 Challenges

- Ambiguity in phrasing
- Context loss when evaluating standalone rules
- Hallucination or overly rigid interpretations
- Over-dependence on LLM’s framing of logic

We plan to mitigate these by:

- Keeping LLMs out of simulation core
- Keeping all structured output editable and auditable
- Logging transformations in MCP

---

## 🤹 Playground Ideas

- Side-by-side rule + parsed view
- Toggle between raw vs interpreted statement
- Sandbox for tweaking how rules affect beliefs

---

## 🤖 LLM Tech Stack (TBD)

- Initial prototyping with OpenAI GPT (via `openai` package)
- Later support Anthropic Claude, Gemini Pro, etc.
- Possibly host local models for offline, privacy-conscious users

---

> *"Let the LLM do the talking. Just make sure you do the thinking."*

