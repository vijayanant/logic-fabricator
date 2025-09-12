import json
import structlog

from .statement import Statement
from .evaluators import (
    SimpleConditionEvaluator,
    ConjunctiveConditionEvaluator,
    ExistentialConditionEvaluator,
    UniversalConditionEvaluator,
)

logger = structlog.get_logger(__name__)


class Condition:
    def __init__(
        self,
        verb: str = None,
        terms: list[str] = None,
        and_conditions: list["Condition"] = None,
        exists_condition: "Condition" = None,
        forall_condition: tuple["Condition", "Condition"] = None,
        verb_synonyms: list[str] = None,
    ):
        self.verb = verb
        self.terms = terms
        self.and_conditions = and_conditions
        self.exists_condition = exists_condition
        self.forall_condition = forall_condition
        self.verb_synonyms = verb_synonyms or []

        is_simple = verb is not None and terms is not None
        is_conjunctive = and_conditions is not None
        is_existential = exists_condition is not None
        is_universal = forall_condition is not None

        if not (is_simple ^ is_conjunctive ^ is_existential ^ is_universal):
            raise ValueError(
                "Condition must be one of simple (verb/terms), conjunctive (and_conditions), "
                "existential (exists_condition), or universal (forall_condition)."
            )
        
        self.evaluator = None
        if is_simple:
            self.evaluator = SimpleConditionEvaluator()
        elif is_conjunctive:
            self.evaluator = ConjunctiveConditionEvaluator()
        elif is_existential:
            self.evaluator = ExistentialConditionEvaluator()
        elif is_universal:
            self.evaluator = UniversalConditionEvaluator()

    def evaluate(self, known_facts: set["Statement"]) -> dict | None:
        if self.evaluator:
            return self.evaluator.evaluate(self, known_facts)
        return None


    def __str__(self):
        if self.and_conditions:
            return f"({' & '.join(map(str, self.and_conditions))})"
        elif self.exists_condition:
            return f"(exists {str(self.exists_condition)})"
        elif self.forall_condition:
            return f"(forall {str(self.forall_condition[0])}, {str(self.forall_condition[1])})"
        else:
            return f"({self.verb} {' '.join(self.terms)})"

    def __repr__(self):
        if self.and_conditions:
            return f"Condition(AND=[{', '.join(map(repr, self.and_conditions))}])"
        elif self.exists_condition:
            return f"Condition(EXISTS={repr(self.exists_condition)})"
        elif self.forall_condition:
            return f"Condition(FORALL=({repr(self.forall_condition[0])}, {repr(self.forall_condition[1])}))"
        else:
            return f"Condition({self.verb} {self.terms})"

    def __eq__(self, other):
        if not isinstance(other, Condition):
            return NotImplemented
        return (
            self.verb == other.verb
            and self.terms == other.terms
            and self.and_conditions == other.and_conditions
            and self.exists_condition == other.exists_condition
            and self.forall_condition == other.forall_condition
            and self.verb_synonyms == other.verb_synonyms
        )

    def __hash__(self):
        and_conditions_tuple = None
        if self.and_conditions is not None:
            and_conditions_tuple = tuple(
                sorted(self.and_conditions, key=lambda c: hash(c))
            )

        return hash(
            (
                self.verb,
                tuple(self.terms) if self.terms else None,
                and_conditions_tuple,
                self.exists_condition,
                self.forall_condition,
                tuple(self.verb_synonyms),
            )
        )

    def to_dict(self):
        if self.and_conditions:
            return {"and_conditions": [c.to_dict() for c in self.and_conditions]}
        elif self.exists_condition:
            return {"exists_condition": self.exists_condition.to_dict()}
        elif self.forall_condition:
            return {
                "forall_condition": [
                    self.forall_condition[0].to_dict(),
                    self.forall_condition[1].to_dict(),
                ]
            }
        else:
            return {
                "verb": self.verb,
                "terms": self.terms,
                "verb_synonyms": self.verb_synonyms,
            }

    def to_dict_json(self):
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: dict):
        if "and_conditions" in data:
            and_conditions = [cls.from_dict(d) for d in data["and_conditions"]]
            return cls(and_conditions=and_conditions)
        elif "exists_condition" in data:
            exists_condition = cls.from_dict(data["exists_condition"])
            return cls(exists_condition=exists_condition)
        elif "forall_condition" in data:
            domain = cls.from_dict(data["forall_condition"][0])
            property = cls.from_dict(data["forall_condition"][1])
            return cls(forall_condition=(domain, property))
        else:
            return cls(
                verb=data["verb"],
                terms=data["terms"],
                verb_synonyms=data.get("verb_synonyms", []),
            )

    

    
