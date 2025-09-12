from typing import Protocol, TYPE_CHECKING
import structlog

from .statement import Statement

if TYPE_CHECKING:
    from .condition import Condition

logger = structlog.get_logger(__name__)

# #############################################################################
# Base Class for Evaluators (using Inheritance for shared helpers)
# #############################################################################

class BaseEvaluator:
    def _match_single_condition(self, condition: "Condition", statement: "Statement") -> dict | None:
        logger.debug(
            "Attempting to match single condition", condition=condition, statement=statement
        )
        verb_matches = (
            condition.verb == statement.verb or statement.verb in condition.verb_synonyms
        )
        if not verb_matches:
            return None

        bindings = {}
        num_cond_terms = len(condition.terms)
        num_stmt_terms = len(statement.terms)

        for i in range(num_cond_terms):
            cond_term = condition.terms[i]
            if cond_term.startswith("*") and i == num_cond_terms - 1:
                if num_stmt_terms < i:
                    return None
                binding_key = "?" + cond_term[1:]
                bindings[binding_key] = statement.terms[i:]
                return bindings

            if i >= num_stmt_terms:
                return None

            stmt_term = statement.terms[i]
            if cond_term.startswith("?"):
                bindings[cond_term] = stmt_term
            elif cond_term != stmt_term:
                return None

        if num_stmt_terms < num_cond_terms:
            return None

        return bindings

    def _find_consistent_bindings(
        self,
        sub_conditions_to_match: list["Condition"],
        available_statements: list["Statement"],
        current_bindings: dict,
    ) -> dict | None:
        if not sub_conditions_to_match:
            return current_bindings

        sub_condition = sub_conditions_to_match[0]
        remaining_sub_conditions = sub_conditions_to_match[1:]

        for i, stmt in enumerate(available_statements):
            sub_bindings = self._match_single_condition(sub_condition, stmt)
            if sub_bindings is not None:
                new_bindings = current_bindings.copy()
                conflict = False
                for key, value in sub_bindings.items():
                    if key in new_bindings and new_bindings[key] != value:
                        conflict = True
                        break
                    new_bindings[key] = value

                if not conflict:
                    next_available_statements = (
                        available_statements[:i] + available_statements[i + 1 :]
                    )
                    result = self._find_consistent_bindings(
                        remaining_sub_conditions,
                        next_available_statements,
                        new_bindings,
                    )
                    if result is not None:
                        return result
        return None

# #############################################################################
# Evaluator Protocol and Concrete Classes
# #############################################################################

class ConditionEvaluator(Protocol):
    """A protocol for classes that can evaluate a Condition."""

    def evaluate(self, condition: "Condition", known_facts: set["Statement"]) -> dict | None:
        """Evaluates the condition against a set of known facts."""
        ...

class SimpleConditionEvaluator(BaseEvaluator):
    """Evaluates a simple, single-statement condition."""

    def evaluate(self, condition: "Condition", known_facts: set["Statement"]) -> dict | None:
        for fact in known_facts:
            bindings = self._match_single_condition(condition, fact)
            if bindings is not None:
                return bindings
        return None

class ConjunctiveConditionEvaluator(BaseEvaluator):
    """Evaluates a condition with multiple AND sub-conditions."""

    def evaluate(self, condition: "Condition", known_facts: set["Statement"]) -> dict | None:
        return self._find_consistent_bindings(
            condition.and_conditions, list(known_facts), {}
        )

class ExistentialConditionEvaluator(BaseEvaluator):
    """Evaluates a condition that checks for the existence of a matching statement."""

    def evaluate(self, condition: "Condition", known_facts: set["Statement"]) -> dict | None:
        for fact in known_facts:
            if self._match_single_condition(condition.exists_condition, fact):
                return {}
        return None

import operator

class UniversalConditionEvaluator(BaseEvaluator):
    """Evaluates a condition that checks if all members of a domain have a property.""" 

    def evaluate(self, condition: "Condition", known_facts: set["Statement"]) -> dict | None:
        domain_cond, property_cond = condition.forall_condition
        domain_bindings = [
            b
            for b in (self._match_single_condition(domain_cond, fact) for fact in known_facts)
            if b is not None
        ]

        if not domain_bindings:
            return {}  # Vacuously true

        all_properties_match = True
        for db in domain_bindings:
            resolved_property_terms = [db.get(t, t) for t in property_cond.terms]
            property_statement_to_check = Statement(
                verb=property_cond.verb, terms=resolved_property_terms
            )
            if property_statement_to_check not in known_facts:
                all_properties_match = False
                break
        
        if all_properties_match:
            return {}
            
        return None


class CountConditionEvaluator(BaseEvaluator):
    """Evaluates a condition based on the count of matching statements."""

    def __init__(self):
        self.operators = {
            ">": operator.gt,
            "<": operator.lt,
            "==": operator.eq,
            ">=": operator.ge,
            "<=": operator.le,
            "!=": operator.ne,
        }

    def evaluate(self, condition: "Condition", known_facts: set["Statement"]) -> dict | None:
        sub_condition, op_str, value = condition.count_condition
        
        count = sum(
            1 for fact in known_facts if self._match_single_condition(sub_condition, fact) is not None
        )

        op_func = self.operators.get(op_str)
        if not op_func:
            logger.warning(f"Unsupported operator in count condition: {op_str}")
            return None

        if op_func(count, value):
            return {}
            
        return None


class NoneConditionEvaluator(BaseEvaluator):
    """Evaluates a condition that checks for the absence of a matching statement."""

    def evaluate(self, condition: "Condition", known_facts: set["Statement"]) -> dict | None:
        for fact in known_facts:
            if self._match_single_condition(condition.none_condition, fact):
                return None  # Found one, so the 'none' condition is false
        return {}  # Found no matches, so the 'none' condition is true
