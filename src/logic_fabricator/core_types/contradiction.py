from typing import Optional

from .statement import Statement
from .rule import Rule


class ContradictionRecord:
    def __init__(
        self,
        statement1: Optional[Statement] = None,
        statement2: Optional[Statement] = None,
        rule_a: Optional[Rule] = None,
        rule_b: Optional[Rule] = None,
        resolution: str = "Undetermined",
        type: str = "statement",
    ):
        self.statement1 = statement1
        self.statement2 = statement2
        self.rule_a = rule_a
        self.rule_b = rule_b
        self.resolution = resolution
        self.type = type  # Assign new field

    def __str__(self):
        return (
            f"ContradictionRecord(type={self.type}, resolution={self.resolution}, "
            f"s1={self.statement1}, s2={self.statement2}, rA={self.rule_a}, rB={self.rule_b})"
        )

    def __repr__(self):
        return (
            f"ContradictionRecord(type={self.type}, res={self.resolution}, "
            f"s1={repr(self.statement1)}, s2={repr(self.statement2)}, "
            f"rA={repr(self.rule_a)}, rB={repr(self.rule_b)})"
        )

    def __eq__(self, other):
        if not isinstance(other, ContradictionRecord):
            return NotImplemented
        return (
            self.statement1 == other.statement1
            and self.statement2 == other.statement2
            and self.rule_a == other.rule_a
            and self.rule_b == other.rule_b
            and self.resolution == other.resolution
            and self.type == other.type
        )

    def __hash__(self):
        return hash(
            (
                self.statement1,
                self.statement2,
                self.rule_a,
                self.rule_b,
                self.resolution,
                self.type,
            )
        )


class InferredContradiction(Exception):
    def __init__(self, statement):
        self.statement = statement
