class Statement:
    def __init__(self, verb: str, terms: list[str]):
        self.verb = verb
        self.terms = terms

class Condition:
    def __init__(self, verb: str):
        self.verb = verb

    def matches(self, statement: Statement) -> bool:
        return self.verb == statement.verb

class Rule:
    def __init__(self, condition: Condition):
        self.condition = condition

    def applies_to(self, statement: Statement) -> bool:
        return self.condition.matches(statement)
