import json
import structlog

from .statement import Statement

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

    def _match_single_condition(self, statement: "Statement") -> dict | None:
        logger.debug(
            "Attempting to match single condition", condition=self, statement=statement
        )
        verb_matches = (
            self.verb == statement.verb or statement.verb in self.verb_synonyms
        )
        if not verb_matches:
            logger.debug(
                "Verb mismatch",
                condition_verb=self.verb,
                statement_verb=statement.verb,
                synonyms=self.verb_synonyms,
            )
            return None

        bindings = {}
        num_cond_terms = len(self.terms)
        num_stmt_terms = len(statement.terms)

        for i in range(num_cond_terms):
            cond_term = self.terms[i]

            # Handle wildcard on the last term
            if cond_term.startswith("*") and i == num_cond_terms - 1:
                if num_stmt_terms < i:  # Not enough terms to even reach the wildcard
                    logger.debug(
                        "Wildcard match failed: not enough statement terms",
                        condition=self,
                        statement=statement,
                    )
                    return None
                binding_key = "?" + cond_term[1:]
                bindings[binding_key] = statement.terms[i:]
                logger.debug(
                    "Wildcard matched",
                    condition=self,
                    statement=statement,
                    bindings=bindings,
                )
                return bindings  # Wildcard is always last, so we are done.

            # This part runs for non-wildcard terms
            if i >= num_stmt_terms:  # Not enough statement terms to match the condition
                logger.debug(
                    "Term mismatch: not enough statement terms",
                    condition=self,
                    statement=statement,
                )
                return None

            stmt_term = statement.terms[i]
            if cond_term.startswith("?"):
                bindings[cond_term] = stmt_term
                logger.debug("Variable bound", var=cond_term, value=stmt_term)
            elif cond_term != stmt_term:
                logger.debug(
                    "Literal term mismatch", expected=cond_term, actual=stmt_term
                )
                return None

        # If the loop completes, all condition terms matched. If the statement is longer,
        # that's permissible as per test_rule_applies_with_fewer_condition_terms.
        if (
            num_stmt_terms < num_cond_terms
        ):  # This check seems redundant given the loop logic, but keeping for consistency
            logger.debug(
                "Statement shorter than condition terms after loop",
                condition=self,
                statement=statement,
            )
            return None

        logger.debug(
            "Single condition matched",
            condition=self,
            statement=statement,
            bindings=bindings,
        )
        return bindings

    def _find_consistent_bindings(
        self,
        sub_conditions_to_match: list["Condition"],
        available_statements: list["Statement"],
        current_bindings: dict,
    ) -> dict | None:
        logger.debug(
            "Attempting to find consistent bindings",
            sub_conditions_count=len(sub_conditions_to_match),
            available_statements_count=len(available_statements),
            current_bindings=current_bindings,
        )
        if not sub_conditions_to_match:
            logger.debug(
                "All sub-conditions matched, returning bindings",
                final_bindings=current_bindings,
            )
            return (
                current_bindings  # All sub-conditions matched, return combined bindings
            )

        sub_condition = sub_conditions_to_match[0]
        remaining_sub_conditions = sub_conditions_to_match[1:]

        for i, stmt in enumerate(available_statements):
            logger.debug(
                "Trying statement for sub-condition",
                sub_condition=sub_condition,
                statement=stmt,
            )
            sub_bindings = sub_condition._match_single_condition(stmt)
            if sub_bindings is not None:
                new_bindings = current_bindings.copy()
                conflict = False
                for key, value in sub_bindings.items():
                    if key in new_bindings and new_bindings[key] != value:
                        logger.debug(
                            "Binding conflict detected",
                            key=key,
                            existing_value=new_bindings[key],
                            new_value=value,
                        )
                        conflict = True
                        break
                    new_bindings[key] = value

                if not conflict:
                    logger.debug(
                        "No binding conflict, recursing", new_bindings=new_bindings
                    )
                    next_available_statements = (
                        available_statements[:i] + available_statements[i + 1 :]
                    )
                    result = self._find_consistent_bindings(
                        remaining_sub_conditions,
                        next_available_statements,
                        new_bindings,
                    )
                    if result is not None:
                        logger.debug(
                            "Consistent bindings found in recursion", result=result
                        )
                        return result
        logger.debug("No consistent bindings found for current path")
        return None

    def matches(self, statements: list["Statement"]) -> dict | None:
        logger.debug(
            "Attempting to match condition",
            condition=self,
            statements_count=len(statements),
        )
        if self.and_conditions is not None:
            logger.debug(
                "Matching conjunctive condition", and_conditions=self.and_conditions
            )
            result = self._find_consistent_bindings(self.and_conditions, statements, {})
            if result is not None:
                logger.debug(
                    "Conjunctive condition matched", condition=self, bindings=result
                )
            else:
                logger.debug("Conjunctive condition did not match", condition=self)
            return result
        else:
            logger.debug("Matching simple condition", condition=self)
            for statement in statements:
                bindings = self._match_single_condition(statement)
                if bindings is not None:
                    logger.debug(
                        "Simple condition matched",
                        condition=self,
                        statement=statement,
                        bindings=bindings,
                    )
                    return bindings
            logger.debug("Simple condition did not match any statement", condition=self)
            return None  # No match found for any statement
