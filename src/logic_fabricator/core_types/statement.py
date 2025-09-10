import json


class Statement:
    def __init__(
        self, verb: str, terms: list[str], negated: bool = False, priority: float = 1.0
    ):
        self.verb = verb
        self.terms = terms
        self.negated = negated
        self.priority = priority

    def __str__(self):
        neg_str = "NOT " if self.negated else ""
        return f"({neg_str}{self.verb} {' '.join(self.terms)})"

    def __repr__(self):
        neg_str = "NOT " if self.negated else ""
        return f"Statement({neg_str}{self.verb} {self.terms}, neg={self.negated}, prio={self.priority})"

    def __eq__(self, other):
        if not isinstance(other, Statement):
            return NotImplemented
        return (
            self.verb == other.verb
            and self.terms == other.terms
            and self.negated == other.negated
            and self.priority == other.priority
        )

    def __hash__(self):
        return hash((self.verb, tuple(self.terms), self.negated, self.priority))

    def to_dict(self):
        return {
            "verb": self.verb,
            "terms": self.terms,
            "negated": self.negated,
            "priority": self.priority,
        }

    def to_dict_json(self):
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)
