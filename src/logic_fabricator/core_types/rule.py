import json
import structlog

from .condition import Condition
from .statement import Statement

logger = structlog.get_logger(__name__)


class Rule:
    def __init__(self, condition: Condition, consequences: list):
        self.condition = condition
        self.consequences = consequences

    def __str__(self):
        return (
            f"Rule: IF {self.condition} THEN {', '.join(map(str, self.consequences))}"
        )

    def __repr__(self):
        consequences_repr = ", ".join([repr(c) for c in self.consequences])
        return f"Rule(IF {repr(self.condition)} THEN [{consequences_repr}])"

    def __eq__(self, other):
        if not isinstance(other, Rule):
            return NotImplemented
        return (
            self.condition == other.condition
            and self.consequences == other.consequences
        )

    def __hash__(self):
        return hash((self.condition, tuple(self.consequences)))

    def to_dict(self):
        return {
            "condition": self.condition.to_dict(),
            "consequences": [c.to_dict() for c in self.consequences],
        }

    def consequences_to_dict_json(self):
        return json.dumps([c.to_dict() for c in self.consequences])

    @classmethod
    def from_dict(cls, data: dict):
        condition = Condition.from_dict(data["condition"])
        consequences = [Statement.from_dict(s_dict) for s_dict in data["consequences"]]
        return cls(condition=condition, consequences=consequences)

    def applies_to(self, statements: list["Statement"]) -> dict | None:
        logger.debug(
            "Checking if rule applies", rule=self, statements_count=len(statements)
        )
        bindings = self.condition.evaluate(set(statements))
        if bindings is not None:
            logger.debug("Rule applies", rule=self, bindings=bindings)
        else:
            logger.debug("Rule does not apply", rule=self)
        return bindings

    @staticmethod
    def _resolve_statement_from_template(
        template_statement: Statement, bindings: dict
    ) -> Statement:
        logger.debug(
            "Resolving statement from template",
            template=template_statement,
            bindings=bindings,
        )
        new_terms = []
        for term in template_statement.terms:
            if isinstance(term, str) and term.startswith("?"):
                resolved_term = bindings.get(term, term)
                new_terms.append(resolved_term)
                logger.debug(
                    "Resolved variable in statement template",
                    var=term,
                    resolved_value=resolved_term,
                )
            else:
                new_terms.append(term)
        resolved_statement = Statement(
            verb=template_statement.verb,
            terms=new_terms,
            negated=template_statement.negated,
            priority=template_statement.priority,
        )
        logger.debug(
            "Statement resolved from template", resolved_statement=resolved_statement
        )
        return resolved_statement
