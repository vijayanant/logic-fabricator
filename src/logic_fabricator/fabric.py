import enum
import json
import structlog
from typing import Optional
import uuid
from dataclasses import dataclass, field

logger = structlog.get_logger(__name__)


class ForkingStrategy(enum.Enum):
    COEXIST = "coexist"
    PRESERVE = "preserve"
    PRIORITIZE_NEW = "prioritize_new"
    PRIORITIZE_OLD = "prioritize_old"


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


class Condition:
    def __init__(
        self,
        verb: str = None,
        terms: list[str] = None,
        and_conditions: list["Condition"] = None,
        verb_synonyms: list[str] = None,
    ):
        self.and_conditions = and_conditions
        self.verb_synonyms = verb_synonyms or []
        if and_conditions is not None:
            self.verb = None  # Not applicable for conjunctive conditions
            self.terms = None  # Not applicable for conjunctive conditions
        else:
            if verb is None or terms is None:
                raise ValueError(
                    "Verb and terms must be provided for a single condition."
                )
            self.verb = verb
            self.terms = terms

    def __str__(self):
        if self.and_conditions:
            return f"({' & '.join(map(str, self.and_conditions))})"
        else:
            return f"({self.verb} {' '.join(self.terms)})"

    def __repr__(self):
        if self.and_conditions:
            return f"Condition(AND=[{', '.join(map(repr, self.and_conditions))}])"
        else:
            return f"Condition({self.verb} {self.terms})"

    def __eq__(self, other):
        if not isinstance(other, Condition):
            return NotImplemented
        return (
            self.verb == other.verb
            and self.terms == other.terms
            and self.and_conditions == other.and_conditions
            and self.verb_synonyms == other.verb_synonyms
        )

    def __hash__(self):
        # Note: and_conditions should be a tuple of conditions for hashing
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
                tuple(self.verb_synonyms),
            )
        )

    def to_dict(self):
        if self.and_conditions:
            # This assumes that sub-conditions also have a to_dict method.
            return {"and_conditions": [c.to_dict() for c in self.and_conditions]}
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
        else:
            return cls(verb=data["verb"], terms=data["terms"], verb_synonyms=data.get("verb_synonyms", []))

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


class Effect:
    def __init__(self, target: str, attribute: str, operation: str, value: any):
        self.target = target
        self.attribute = attribute
        self.operation = operation
        self.value = value

    def __str__(self):
        return (
            f"Effect: {self.operation} {self.target}.{self.attribute} to {self.value}"
        )

    def __repr__(self):
        return f"Effect(op={self.operation}, target={self.target}.{self.attribute}, val={self.value})"

    def __eq__(self, other):
        if not isinstance(other, Effect):
            return NotImplemented
        return (
            self.target == other.target
            and self.attribute == other.attribute
            and self.operation == other.operation
            and self.value == other.value
        )

    def __hash__(self):
        return hash((self.target, self.attribute, self.operation, self.value))

    def to_dict(self):
        return {
            "target": self.target,
            "attribute": self.attribute,
            "operation": self.operation,
            "value": self.value,
        }


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
        bindings = self.condition.matches(statements)
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


class ContradictionEngine:
    _HYPOTHETICAL_ENTITY_ = "_HYPOTHETICAL_ENTITY_"
    def detect(self, s1: Statement, s2: Statement) -> bool:
        logger.debug(
            "Detecting contradiction between statements", statement1=s1, statement2=s2
        )
        if s1.verb == s2.verb and s1.terms == s2.terms and s1.negated != s2.negated:
            logger.info("Contradiction detected", statement1=s1, statement2=s2)
            return True

        logger.debug(
            "No contradiction detected between statements", statement1=s1, statement2=s2
        )
        return False

    def _check_one_way_conflict(
        self, rule_a: Rule, rule_b: Rule, context_rules: list[Rule]
    ) -> bool:
        logger.debug("Checking one-way conflict", rule_a=rule_a, rule_b=rule_b)
        """Checks if rule_b's condition can lead to a state that conflicts with rule_a."""
        # Use a hypothetical entity for the simulation
        hypothetical_entity = self._HYPOTHETICAL_ENTITY_

        # Create a hypothetical statement from rule_b's condition
        if not rule_b.condition.terms or not rule_b.condition.terms[0].startswith("?"):
            logger.debug("Cannot create hypothetical case for rule_b", rule_b=rule_b)
            return False  # Cannot create a hypothetical case without a variable subject

        var_name = rule_b.condition.terms[0]
        hypothetical_terms = [
            term if term != var_name else hypothetical_entity
            for term in rule_b.condition.terms
        ]
        hypothetical_statement = Statement(
            verb=rule_b.condition.verb, terms=hypothetical_terms
        )
        logger.debug("Created hypothetical statement", statement=hypothetical_statement)

        # Run the pure inference chain to see what can be derived from the hypothetical statement.
        derived_facts, _ = BeliefSystem._run_inference_chain(
            {hypothetical_statement}, context_rules
        )
        logger.debug(
            "Derived facts from hypothetical statement", derived_facts=derived_facts
        )

        # Combine initial and derived facts for checking rule applicability
        all_facts = derived_facts + [hypothetical_statement]
        logger.debug("All facts for conflict check", all_facts=all_facts)

        # Check if both rules apply to the resulting state
        bindings_a = rule_a.applies_to(all_facts)
        bindings_b = rule_b.applies_to(all_facts)
        logger.debug(
            "Rule applicability check results",
            rule_a_applies=bool(bindings_a),
            rule_b_applies=bool(bindings_b),
        )

        if bindings_a and bindings_b:
            logger.debug(
                "Both rules apply, checking consequences for contradictions",
                rule_a=rule_a,
                rule_b=rule_b,
            )
            # If both apply, check their consequences for contradictions
            for con_a in rule_a.consequences:
                if not isinstance(con_a, Statement):
                    logger.debug(
                        "Consequence A is not a Statement, skipping", consequence=con_a
                    )
                    continue
                resolved_a = Rule._resolve_statement_from_template(con_a, bindings_a)
                for con_b in rule_b.consequences:
                    if not isinstance(con_b, Statement):
                        logger.debug(
                            "Consequence B is not a Statement, skipping",
                            consequence=con_b,
                        )
                        continue
                    resolved_b = Rule._resolve_statement_from_template(
                        con_b, bindings_b
                    )
                    logger.debug(
                        "Checking for contradiction between resolved consequences",
                        resolved_a=resolved_a,
                        resolved_b=resolved_b,
                    )
                    if self.detect(resolved_a, resolved_b):
                        logger.info(
                            "One-way conflict detected between rules",
                            rule_a=rule_a,
                            rule_b=rule_b,
                            conflicting_statements=[resolved_a, resolved_b],
                        )
                        return True
        logger.debug(
            "No one-way conflict detected for this path", rule_a=rule_a, rule_b=rule_b
        )
        return False

    def detect_rule_conflict(
        self, rule_a: Rule, rule_b: Rule, context_rules: list[Rule]
    ) -> bool:
        logger.debug("Detecting rule conflict", rule_a=rule_a, rule_b=rule_b)
        """Detects if two rules could conflict, given a set of context rules."""
        # A conflict exists if rule_a can lead to a contradiction with rule_b, or vice-versa.
        conflict_found = self._check_one_way_conflict(
            rule_a, rule_b, context_rules
        ) or self._check_one_way_conflict(rule_b, rule_a, context_rules)
        if conflict_found:
            logger.info("Rule conflict detected", rule_a=rule_a, rule_b=rule_b)
        else:
            logger.debug("No rule conflict detected", rule_a=rule_a, rule_b=rule_b)
        return conflict_found


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


def op_set(current_value, new_value):
    return new_value


def op_increment(current_value, new_value):
    return (current_value or 0) + new_value


def op_decrement(current_value, new_value):
    return (current_value or 0) - new_value


def op_append(current_value, new_value):
    current_list = list(current_value or [])
    current_list.append(new_value)
    return current_list


class BeliefSystem:
    _id_counter = 0  # Class-level counter for unique IDs

    def __init__(
        self,
        rules: list[Rule],
        contradiction_engine: ContradictionEngine,
        strategy: ForkingStrategy = ForkingStrategy.COEXIST,
    ):
        BeliefSystem._id_counter += 1
        self.id = BeliefSystem._id_counter
        logger.info(
            "Initializing BeliefSystem",
            belief_system_id=self.id,
            strategy=strategy,
            initial_rules_count=len(rules),
        )
        self.rules = rules
        self.contradiction_engine = contradiction_engine
        self.strategy = strategy
        self.statements = set()
        self.contradictions = []
        
        self.forks = []
        self.world_state = {}
        self.effects_applied = set()  # Permanent memory for applied effects
        self.world_state_operations = {
            "set": op_set,
            "increment": op_increment,
            "decrement": op_decrement,
            "append": op_append,
        }
        self._latent_contradictions = self._detect_initial_latent_conflicts()
        logger.debug(
            "BeliefSystem initialized",
            belief_system_id=self.id,
            latent_contradictions_count=len(self._latent_contradictions),
        )

    def __repr__(self):
        return (
            f"BeliefSystem(id={self.id}, rules_count={len(self.rules)}, "
            f"statements_count={len(self.statements)}, forks_count={len(self.forks)}, "
            f"strategy={self.strategy.name})"
        )

    def _detect_initial_latent_conflicts(self) -> list[ContradictionRecord]:
        logger.info("Detecting initial latent conflicts among rules.")
        latent_contradictions = []
        for i, rule_a in enumerate(self.rules):
            for j, rule_b in enumerate(self.rules):
                if i >= j:  # Avoid duplicate checks and self-comparison
                    continue
                if self.contradiction_engine.detect_rule_conflict(
                    rule_a, rule_b, self.rules
                ):
                    record = ContradictionRecord(
                        rule_a=rule_a,
                        rule_b=rule_b,
                        resolution="Latent conflict detected on initialization",
                        type="rule_latent",
                    )
                    latent_contradictions.append(record)
                    logger.warning("Latent conflict detected", record=record)
        logger.info(
            "Finished detecting initial latent conflicts.",
            count=len(latent_contradictions),
        )
        return latent_contradictions

    @staticmethod
    def _run_inference_chain(initial_statements: set, rules: list[Rule]):
        logger.info(
            "Running inference chain",
            initial_statements_count=len(initial_statements),
            rules_count=len(rules),
        )
        """Runs the inference loop in a pure, stateless way, returning all successful applications."""
        known_facts = set(initial_statements)
        final_applications = []
        processed_application_keys = set()
        inference_pass = 0

        while True:
            inference_pass += 1
            newly_inferred_this_pass = set()
            logger.debug(
                "Inference pass",
                pass_number=inference_pass,
                known_facts_count=len(known_facts),
            )
            for rule in rules:
                bindings = rule.applies_to(list(known_facts))
                if bindings is not None:
                    application_key = (rule, frozenset(bindings.items()))
                    if application_key not in processed_application_keys:
                        processed_application_keys.add(application_key)
                        final_applications.append((rule, bindings))
                        logger.debug(
                            "Rule applied in inference chain",
                            rule=rule,
                            bindings=bindings,
                        )
                        for consequence in rule.consequences:
                            if isinstance(consequence, Statement):
                                inferred_statement = (
                                    Rule._resolve_statement_from_template(
                                        consequence, bindings
                                    )
                                )
                                if inferred_statement not in known_facts:
                                    newly_inferred_this_pass.add(inferred_statement)
                                    logger.debug(
                                        "Newly inferred statement",
                                        statement=inferred_statement,
                                    )

            if not newly_inferred_this_pass:
                logger.debug(
                    "No new facts inferred in this pass, breaking inference chain."
                )
                break
            known_facts.update(newly_inferred_this_pass)
            logger.debug(
                "Facts updated after pass",
                newly_inferred_count=len(newly_inferred_this_pass),
                total_known_facts=len(known_facts),
            )

        derived_facts = known_facts - initial_statements
        logger.info(
            "Inference chain completed",
            total_derived_facts=len(derived_facts),
            total_applications=len(final_applications),
            total_passes=inference_pass,
        )
        return list(derived_facts), final_applications

    def fork(self, statements: set[Statement]) -> "BeliefSystem":
        logger.info(
            "Forking BeliefSystem",
            parent_statements_count=len(self.statements),
            new_statements_count=len(statements),
        )
        forked_system = BeliefSystem(
            rules=list(self.rules),
            contradiction_engine=self.contradiction_engine,
            strategy=self.strategy,
        )
        forked_system.statements = statements
        forked_system.world_state = {k: v for k, v in self.world_state.items()}
        self.forks.append(forked_system)
        logger.debug("BeliefSystem forked successfully", forked_system=forked_system)
        return forked_system

    def add_statement(self, new_statement: Statement) -> bool:
        logger.info("Attempting to add statement", statement=new_statement)
        is_contradictory = False
        for existing_statement in self.statements:
            if self.contradiction_engine.detect(new_statement, existing_statement):
                record = ContradictionRecord(
                    statement1=new_statement,
                    statement2=existing_statement,
                    type="statement",
                )
                self.contradictions.append(record)
                logger.warning(
                    "Contradiction detected when adding statement", record=record
                )
                is_contradictory = True
                break
        if not is_contradictory:
            self.statements.add(new_statement)
            logger.info("Statement added successfully", statement=new_statement)
        else:
            logger.info(
                "Statement not added due to contradiction", statement=new_statement
            )
        return not is_contradictory

    def _handle_contradiction(
        self, contradictory_statement: Statement
    ) -> Optional["BeliefSystem"]:
        logger.info(
            "Handling contradiction",
            contradictory_statement=contradictory_statement,
            strategy=self.strategy,
        )
        if self.strategy == ForkingStrategy.PRESERVE:
            logger.info("Contradiction strategy is PRESERVE, not forking.")
            return None

        new_statements = self.statements.copy()

        if self.strategy in [
            ForkingStrategy.PRIORITIZE_NEW,
            ForkingStrategy.PRIORITIZE_OLD,
        ]:
            old_statement = next(
                (
                    s
                    for s in self.statements
                    if self.contradiction_engine.detect(contradictory_statement, s)
                ),
                None,
            )
            if old_statement:
                priority_adjustment = (
                    0.1 if self.strategy == ForkingStrategy.PRIORITIZE_NEW else -0.1
                )
                modified_statement = Statement(
                    verb=contradictory_statement.verb,
                    terms=contradictory_statement.terms,
                    negated=contradictory_statement.negated,
                    priority=old_statement.priority + priority_adjustment,
                )
                new_statements.add(modified_statement)
                logger.debug(
                    "Modified statement priority due to strategy",
                    strategy=self.strategy,
                    old_statement=old_statement,
                    modified_statement=modified_statement,
                )
            else:
                new_statements.add(contradictory_statement)
                logger.debug(
                    "Added contradictory statement with no old statement to prioritize",
                    statement=contradictory_statement,
                )
        else:  # COEXIST
            new_statements.add(contradictory_statement)
            logger.debug(
                "Added contradictory statement using COEXIST strategy",
                statement=contradictory_statement,
            )

        forked_system = self.fork(new_statements)
        logger.info(
            "BeliefSystem forked due to contradiction", forked_system=forked_system
        )
        return forked_system

    def _process_initial_statements(
        self, new_statements_to_process: list["Statement"]
    ) -> Optional["BeliefSystem"]:
        logger.info(
            "Processing initial statements",
            statements_count=len(new_statements_to_process),
        )
        forked_belief_system = None
        for statement_to_add in new_statements_to_process:
            if not self.add_statement(statement_to_add):
                logger.info(
                    "Statement led to contradiction, handling contradiction.",
                    statement=statement_to_add,
                )
                forked_belief_system = self._handle_contradiction(statement_to_add)
                if forked_belief_system:
                    logger.info(
                        "BeliefSystem forked during initial statement processing.",
                        forked_system=forked_belief_system,
                    )
                else:
                    logger.info(
                        "Contradiction handled without forking (e.g., PRESERVE strategy).",
                        statement=statement_to_add,
                    )
                break  # Stop processing further statements if a fork occurs
        logger.info(
            "Finished processing initial statements.",
            forked_system_created=bool(forked_belief_system),
        )
        return forked_belief_system

    def _execute_effect(self, effect: Effect, bindings: dict):
        logger.info("Executing effect", effect=effect, bindings=bindings)
        if effect.target == "world_state":
            operation_func = self.world_state_operations.get(effect.operation)
            if operation_func:
                key_template = effect.attribute
                value_template = effect.value

                key = bindings.get(key_template, key_template)
                if isinstance(value_template, str) and value_template.startswith("?"):
                    value = bindings.get(value_template, value_template)
                else:
                    value = value_template

                current_value = self.world_state.get(key)
                new_value = operation_func(current_value, value)
                logger.info(
                    "World state change",
                    key=key,
                    old_value=current_value,
                    new_value=new_value,
                    operation=effect.operation,
                )
                self.world_state[key] = new_value
            else:
                logger.warning("Unknown effect operation", operation=effect.operation)
        else:
            logger.warning("Unsupported effect target", target=effect.target)

    def _perform_inference(self):
        logger.info("Performing inference on current belief system.")
        derived_facts, applications = BeliefSystem._run_inference_chain(
            self.statements, self.rules
        )
        logger.debug(
            "Inference chain returned",
            derived_facts_count=len(derived_facts),
            applications_count=len(applications),
        )

        for inferred_statement in derived_facts:
            logger.debug("Adding inferred statement", statement=inferred_statement)
            if not self.add_statement(inferred_statement):
                logger.warning(
                    "Inferred statement led to contradiction",
                    statement=inferred_statement,
                )
                raise InferredContradiction(inferred_statement)

        applied_rules_set = set()
        for rule, bindings in applications:
            applied_rules_set.add(rule)
            for consequence in rule.consequences:
                if isinstance(consequence, Effect):
                    effect_key = (rule, frozenset(bindings.items()))
                    if effect_key not in self.effects_applied:
                        logger.debug(
                            "Executing effect from applied rule",
                            rule=rule,
                            effect=consequence,
                            bindings=bindings,
                        )
                        self._execute_effect(consequence, bindings)
                        self.effects_applied.add(effect_key)
                    else:
                        logger.debug(
                            "Effect already applied for this rule and bindings, skipping.",
                            rule=rule,
                            effect=consequence,
                            bindings=bindings,
                        )

        logger.info(
            "Inference completed.",
            total_derived_facts=len(derived_facts),
            total_applied_rules=len(applied_rules_set),
        )
        return derived_facts, list(applied_rules_set)

    

    def simulate(self, new_statements_to_process: list["Statement"]):
        logger.info(
            "Starting simulation", new_statements_count=len(new_statements_to_process)
        )
        for fork in self.forks:
            logger.debug("Simulating in forked system", fork=fork)
            fork.simulate(new_statements_to_process)

        forked_belief_system = self._process_initial_statements(
            new_statements_to_process
        )

        derived_facts = []
        applied_rules = []

        if not forked_belief_system:
            try:
                derived_facts, applied_rules = self._perform_inference()
                logger.info(
                    "Inference completed without contradiction during simulation."
                )
            except InferredContradiction as e:
                logger.warning(
                    "Inferred contradiction during simulation, handling.",
                    statement=e.statement,
                )
                forked_belief_system = self._handle_contradiction(e.statement)
                derived_facts = []
                applied_rules = []
                if forked_belief_system:
                    logger.info(
                        "BeliefSystem forked due to inferred contradiction.",
                        forked_system=forked_belief_system,
                    )
                else:
                    logger.info(
                        "Inferred contradiction handled without forking (e.g., PRESERVE strategy).",
                        statement=e.statement,
                    )
            except Exception as e:
                logger.error(
                    "Unexpected error during inference in simulation", exc_info=True
                )
                raise  # Re-raise the exception after logging

        simulation_result = SimulationResult(
            derived_facts=derived_facts,
            applied_rules=applied_rules,
            forked_belief_system=forked_belief_system,
        )

        record = SimulationRecord(
            initial_statements=new_statements_to_process,
            derived_facts=derived_facts,
            applied_rules=applied_rules,
            forked_belief_system=forked_belief_system,
        )
        
        logger.info(
            "Simulation completed.",
            derived_facts_count=len(derived_facts),
            applied_rules_count=len(applied_rules),
            forked_system_created=bool(forked_belief_system),
        )
        return simulation_result


class SimulationResult:
    def __init__(
        self,
        derived_facts: list[Statement],
        applied_rules: list[Rule],
        forked_belief_system: "BeliefSystem" = None,
    ):
        self.derived_facts = derived_facts
        self.applied_rules = applied_rules
        self.forked_belief_system = forked_belief_system

    def __str__(self):
        fork_str = (
            f", forked={self.forked_belief_system.id}"
            if self.forked_belief_system
            else ""
        )
        return (
            f"SimulationResult(derived={len(self.derived_facts)}, "
            f"applied={len(self.applied_rules)}{fork_str})"
        )

    def __repr__(self):
        fork_repr = (
            repr(self.forked_belief_system) if self.forked_belief_system else "None"
        )
        return (
            f"SimulationResult(derived_facts={repr(self.derived_facts)}, "
            f"applied_rules={repr(self.applied_rules)}, "
            f"forked_belief_system={fork_repr})"
        )


@dataclass
class SimulationRecord:
    initial_statements: list[Statement]
    derived_facts: list[Statement]
    applied_rules: list[Rule]
    forked_belief_system: Optional["BeliefSystem"] = None
    id: uuid.UUID = field(default_factory=uuid.uuid4)

    def __str__(self):
        fork_str = (
            f", forked={self.forked_belief_system.id}"
            if self.forked_belief_system
            else ""
        )
        return (
            f"SimulationRecord(initial={len(self.initial_statements)}, "
            f"derived={len(self.derived_facts)}, applied={len(self.applied_rules)}{fork_str})"
        )

    def __repr__(self):
        fork_repr = (
            repr(self.forked_belief_system) if self.forked_belief_system else "None"
        )
        return (
            f"SimulationRecord(initial_statements={repr(self.initial_statements)}, "
            f"derived_facts={repr(self.derived_facts)}, "
            f"applied_rules={repr(self.applied_rules)}, "
            f"forked_belief_system={fork_repr})"
        )
