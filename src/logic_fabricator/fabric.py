class Statement:
    def __init__(self, verb: str, terms: list[str]):
        self.verb = verb
        self.terms = terms


class Condition:
    def __init__(self, verb: str, terms: list[str]):
        self.verb = verb
        self.terms = terms

    def matches(self, statement: Statement) -> dict | None:
        if self.verb != statement.verb:
            return None

        if len(self.terms) != len(statement.terms):
            return None

        bindings = {}
        for cond_term, stmt_term in zip(self.terms, statement.terms):
            if cond_term.startswith("?"):  # It's a variable
                bindings[cond_term] = stmt_term
            elif cond_term != stmt_term:  # Mismatch for literal terms
                return None

        return bindings


class Rule:
    def __init__(self, condition: Condition):
        self.condition = condition

    def applies_to(self, statement: Statement) -> dict | None:
        return self.condition.matches(statement)
