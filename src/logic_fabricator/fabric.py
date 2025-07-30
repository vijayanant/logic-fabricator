class Statement:
    def __init__(self, verb: str, terms: list[str]):
        self.verb = verb
        self.terms = terms

    def __eq__(self, other):
        if not isinstance(other, Statement):
            return NotImplemented
        return self.verb == other.verb and self.terms == other.terms

    def __hash__(self):
        return hash((self.verb, tuple(self.terms)))


class Condition:
    def __init__(self, verb: str, terms: list[str]):
        self.verb = verb
        self.terms = terms

    def matches(self, statement: Statement) -> dict | None:
        if self.verb != statement.verb:
            return None

        # Ensure the statement has at least as many terms as the condition
        if len(statement.terms) < len(self.terms):
            return None

        bindings = {}
        # Iterate only up to the length of the condition's terms
        for i in range(len(self.terms)):
            cond_term = self.terms[i]
            stmt_term = statement.terms[i]

            if cond_term.startswith("?"):  # It's a variable
                bindings[cond_term] = stmt_term
            elif cond_term != stmt_term:  # Mismatch for literal terms
                return None

        return bindings


class Rule:
    def __init__(self, condition: Condition, consequence: Statement):
        self.condition = condition
        self.consequence = consequence

    def applies_to(self, statement: Statement) -> dict | None:
        return self.condition.matches(statement)

    def generate_consequence(self, bindings: dict) -> Statement:
        new_verb = self.consequence.verb
        new_terms = []
        for term in self.consequence.terms:
            if term.startswith("?"):
                new_terms.append(
                    bindings.get(term, term)
                )  # Use bound value, or original term if not found
            else:
                new_terms.append(term)
        return Statement(verb=new_verb, terms=new_terms)


class ContradictionEngine:
    def detect(self, s1: Statement, s2: Statement) -> bool:
        # Simple contradiction: same verb, same first term (subject), different second term (object)
        if (
            s1.verb == s2.verb
            and s1.terms[0] == s2.terms[0]
            and s1.terms[1] != s2.terms[1]
        ):
            return True
        return False


class BeliefSystem:
    def __init__(self, rules: list[Rule]):
        self.rules = rules
        self.statements = []

    def add_statement(self, new_statement: Statement):
        self.statements.append(new_statement)
        # Apply rules to infer new statements
        for rule in self.rules:
            bindings = rule.applies_to(new_statement)
            if bindings is not None:
                inferred_statement = rule.generate_consequence(bindings)
                # For now, just add it. Contradiction detection will come later.
                self.statements.append(inferred_statement)
