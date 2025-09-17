import json
import structlog
from typing import Optional, Tuple

from .statement import Statement
from .evaluators import (
    SimpleConditionEvaluator,
    ConjunctiveConditionEvaluator,
    ExistentialConditionEvaluator,
    UniversalConditionEvaluator,
    CountConditionEvaluator,
    NoneConditionEvaluator,
)

logger = structlog.get_logger(__name__)


class Condition:
    def __init__(
        self,
        type: str,
        children: list["Condition"] = None,
        verb: str = None,
        terms: list[str] = None,
        verb_synonyms: list[str] = None,
        operator: str = None, # For COUNT
        value: int = None, # For COUNT
    ):
        self.type = type
        self.children = children or []
        self.verb = verb
        self.terms = terms
        self.verb_synonyms = verb_synonyms or []
        self.operator = operator
        self.value = value

        # Determine the evaluator based on the type
        if self.type == "LEAF":
            self.evaluator = SimpleConditionEvaluator()
        elif self.type == "AND":
            self.evaluator = ConjunctiveConditionEvaluator()
        elif self.type == "EXISTS":
            self.evaluator = ExistentialConditionEvaluator()
        elif self.type == "FORALL":
            self.evaluator = UniversalConditionEvaluator()
        elif self.type == "COUNT":
            self.evaluator = CountConditionEvaluator()
        elif self.type == "NONE":
            self.evaluator = NoneConditionEvaluator()
        else:
            # OR is not directly evaluated, it's decomposed by the translator
            self.evaluator = None

    def evaluate(self, known_facts: set["Statement"]) -> dict | None:
        if self.evaluator:
            return self.evaluator.evaluate(self, known_facts)
        return None

    def __str__(self):
        if self.type in ["AND", "OR"]:
            return f"({' & '.join(map(str, self.children))})"
        elif self.type in ["EXISTS", "NONE"]:
            return f"({self.type.lower()} {str(self.children[0])})"
        elif self.type == "FORALL":
            return f"(forall {str(self.children[0])}, {str(self.children[1])})"
        elif self.type == "COUNT":
            return f"(count {str(self.children[0])} {self.operator} {self.value})"
        else:  # LEAF
            return f"({self.verb} {' '.join(self.terms)})"

    def __repr__(self):
        if self.type in ["AND", "OR"]:
            return f"Condition({self.type}=[{{', '.join(map(repr, self.children))}}])"
        elif self.type in ["EXISTS", "NONE"]:
            return f"Condition({self.type}={repr(self.children[0])})"
        elif self.type == "FORALL":
            return f"Condition(FORALL=({repr(self.children[0])}, {repr(self.children[1])}))"
        elif self.type == "COUNT":
            return f"Condition(COUNT=({repr(self.children[0])}, '{self.operator}', {self.value}))"
        else:  # LEAF
            return f"Condition({self.verb} {self.terms})"

    def __eq__(self, other):
        if not isinstance(other, Condition):
            return NotImplemented
        return (
            self.type == other.type
            and self.children == other.children
            and self.verb == other.verb
            and self.terms == other.terms
            and self.operator == other.operator
            and self.value == other.value
            and self.verb_synonyms == other.verb_synonyms
        )

    def __hash__(self):
        # Note: children list is mutable, so we convert to a tuple of hashes for hashing
        children_hash = tuple(sorted(hash(c) for c in self.children))
        return hash(
            (
                self.type,
                children_hash,
                self.verb,
                tuple(self.terms) if self.terms else None,
                self.operator,
                self.value,
                tuple(self.verb_synonyms),
            )
        )

    def to_dict(self):
        data = {"type": self.type}
        if self.children:
            data["children"] = [c.to_dict() for c in self.children]
        if self.verb:
            data["verb"] = self.verb
        if self.terms:
            data["terms"] = self.terms
        if self.type == "LEAF":
            data["verb_synonyms"] = self.verb_synonyms
        if self.operator:
            data["operator"] = self.operator
        if self.value is not None:
            data["value"] = self.value
        return data

    def to_dict_json(self):
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: dict):
        # Recursively build children from their dict representations
        children = [cls.from_dict(d) for d in data.get("children", [])]
        return cls(
            type=data["type"],
            children=children,
            verb=data.get("verb"),
            terms=data.get("terms"),
            verb_synonyms=data.get("verb_synonyms", []),
            operator=data.get("operator"),
            value=data.get("value"),
        )

    

    
