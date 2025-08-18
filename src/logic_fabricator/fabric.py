import enum
from typing import Optional


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

    def __repr__(self):
        neg_str = "NOT " if self.negated else ""
        return f"Statement({neg_str}{self.verb} {' '.join(self.terms)})"

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


class Condition:
    def __init__(
        self,
        verb: str = None,
        terms: list[str] = None,
        and_conditions: list["Condition"] = None,
        verb_synonyms: list[str] = None,
    ):
        self.and_conditions = and_conditions  # Initialize here
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

    def __repr__(self):
        if self.and_conditions:
            return f"Condition(AND: {' & '.join(map(repr, self.and_conditions))})"
        else:
            return f"Condition({self.verb} {' '.join(self.terms)})"

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

    def _match_single_condition(self, statement: "Statement") -> dict | None:
        verb_matches = (
            self.verb == statement.verb or statement.verb in self.verb_synonyms
        )
        if not verb_matches:
            return None

        bindings = {}
        num_cond_terms = len(self.terms)
        num_stmt_terms = len(statement.terms)

        for i in range(num_cond_terms):
            cond_term = self.terms[i]

            # Handle wildcard on the last term
            if cond_term.startswith("*") and i == num_cond_terms - 1:
                if num_stmt_terms < i:  # Not enough terms to even reach the wildcard
                    return None
                binding_key = "?" + cond_term[1:]
                bindings[binding_key] = statement.terms[i:]
                return bindings  # Wildcard is always last, so we are done.

            # This part runs for non-wildcard terms
            if i >= num_stmt_terms:  # Not enough statement terms to match the condition
                return None

            stmt_term = statement.terms[i]
            if cond_term.startswith("?"):
                bindings[cond_term] = stmt_term
            elif cond_term != stmt_term:
                return None

        # If the loop completes, all condition terms matched. If the statement is longer,
        # that's permissible as per test_rule_applies_with_fewer_condition_terms.
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
            return (
                current_bindings  # All sub-conditions matched, return combined bindings
            )

        sub_condition = sub_conditions_to_match[0]
        remaining_sub_conditions = sub_conditions_to_match[1:]

        for i, stmt in enumerate(available_statements):
            sub_bindings = sub_condition._match_single_condition(
                stmt
            )  # Use the new helper
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

    def matches(self, statements: list["Statement"]) -> dict | None:
        if self.and_conditions is not None:
            return self._find_consistent_bindings(self.and_conditions, statements, {})
        else:
            for statement in statements:
                bindings = self._match_single_condition(statement)
                if bindings is not None:
                    return bindings
            return None  # No match found for any statement


class Effect:
    def __init__(self, target: str, attribute: str, operation: str, value: any):
        self.target = target
        self.attribute = attribute
        self.operation = operation
        self.value = value

    def __repr__(self):
        return (
            f"Effect({self.operation} {self.target}.{self.attribute} to {self.value})"
        )

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


class Rule:
    def __init__(self, condition: Condition, consequences: list):
        self.condition = condition
        self.consequences = consequences

    def __repr__(self):
        return (
            f"Rule(IF {self.condition} THEN {', '.join(map(repr, self.consequences))})"
        )

    def __eq__(self, other):
        if not isinstance(other, Rule):
            return NotImplemented
        return (
            self.condition == other.condition
            and self.consequences == other.consequences
        )

    def __hash__(self):
        return hash((self.condition, tuple(self.consequences)))

    def applies_to(self, statements: list["Statement"]) -> dict | None:
        return self.condition.matches(statements)

    @staticmethod
    def _resolve_statement_from_template(
        template_statement: Statement, bindings: dict
    ) -> Statement:
        new_terms = []
        for term in template_statement.terms:
            if isinstance(term, str) and term.startswith("?"):
                new_terms.append(bindings.get(term, term))
            else:
                new_terms.append(term)
        return Statement(
            verb=template_statement.verb,
            terms=new_terms,
            negated=template_statement.negated,
            priority=template_statement.priority,
        )


class ContradictionEngine:
    def detect(self, s1: Statement, s2: Statement) -> bool:
        if s1.verb == s2.verb and s1.terms == s2.terms and s1.negated != s2.negated:
            return True

        return False

    def _check_one_way_conflict(
        self, rule_a: Rule, rule_b: Rule, context_rules: list[Rule]
    ) -> bool:
        """Checks if rule_b's condition can lead to a state that conflicts with rule_a."""
        # Use a hypothetical entity for the simulation
        hypothetical_entity = "_HYPOTHETICAL_ENTITY_"

        # Create a hypothetical statement from rule_b's condition
        if not rule_b.condition.terms or not rule_b.condition.terms[0].startswith("?"):
            return False  # Cannot create a hypothetical case without a variable subject

        var_name = rule_b.condition.terms[0]
        hypothetical_terms = [
            term if term != var_name else hypothetical_entity
            for term in rule_b.condition.terms
        ]
        hypothetical_statement = Statement(
            verb=rule_b.condition.verb, terms=hypothetical_terms
        )

        # Simulate the context rules with this hypothetical statement
        temp_belief_system = BeliefSystem(rules=context_rules, contradiction_engine=self)
        sim_result = temp_belief_system.simulate([hypothetical_statement])

        # Combine initial and derived facts for checking rule applicability
        all_facts = sim_result.derived_facts + [hypothetical_statement]

        # Check if both rules apply to the resulting state
        bindings_a = rule_a.applies_to(all_facts)
        bindings_b = rule_b.applies_to(all_facts)

        if bindings_a and bindings_b:
            # If both apply, check their consequences for contradictions
            for con_a in rule_a.consequences:
                if not isinstance(con_a, Statement):
                    continue
                resolved_a = Rule._resolve_statement_from_template(con_a, bindings_a)
                for con_b in rule_b.consequences:
                    if not isinstance(con_b, Statement):
                        continue
                    resolved_b = Rule._resolve_statement_from_template(con_b, bindings_b)
                    if self.detect(resolved_a, resolved_b):
                        return True
        return False

    def detect_rule_conflict(
        self, rule_a: Rule, rule_b: Rule, context_rules: list[Rule]
    ) -> bool:
        """Detects if two rules could conflict, given a set of context rules."""
        # A conflict exists if rule_a can lead to a contradiction with rule_b, or vice-versa.
        return self._check_one_way_conflict(
            rule_a, rule_b, context_rules
        ) or self._check_one_way_conflict(rule_b, rule_a, context_rules)


class ContradictionRecord:
    def __init__(self, statement1: Statement, statement2: Statement):
        self.statement1 = statement1
        self.statement2 = statement2

    def __eq__(self, other):
        if not isinstance(other, ContradictionRecord):
            return NotImplemented
        return (
            self.statement1 == other.statement1 and self.statement2 == other.statement2
        )

    def __hash__(self):
        return hash((self.statement1, self.statement2))


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
    def __init__(
        self,
        rules: list[Rule],
        contradiction_engine: ContradictionEngine,
        strategy: ForkingStrategy = ForkingStrategy.COEXIST,
    ):
        self.rules = rules
        self.contradiction_engine = contradiction_engine
        self.strategy = strategy
        self.statements = set()
        self.contradictions = []
        self.mcp_records = []
        self.forks = []
        self.world_state = {}
        self.effects_applied = set()  # Permanent memory for applied effects
        self.world_state_operations = {
            "set": op_set,
            "increment": op_increment,
            "decrement": op_decrement,
            "append": op_append,
        }

    def fork(self, statements: set[Statement]) -> "BeliefSystem":
        forked_system = BeliefSystem(
            rules=list(self.rules),
            contradiction_engine=self.contradiction_engine,
            strategy=self.strategy,
        )
        forked_system.statements = statements
        forked_system.world_state = {k: v for k, v in self.world_state.items()}
        self.forks.append(forked_system)
        return forked_system

    def add_statement(self, new_statement: Statement) -> bool:
        is_contradictory = False
        for existing_statement in self.statements:
            if self.contradiction_engine.detect(new_statement, existing_statement):
                self.contradictions.append(
                    ContradictionRecord(new_statement, existing_statement)
                )
                is_contradictory = True
                break
        if not is_contradictory:
            self.statements.add(new_statement)
        return not is_contradictory

    def _handle_contradiction(
        self, contradictory_statement: Statement
    ) -> Optional["BeliefSystem"]:
        if self.strategy == ForkingStrategy.PRESERVE:
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
            else:
                new_statements.add(contradictory_statement)
        else:  # COEXIST
            new_statements.add(contradictory_statement)

        return self.fork(new_statements)

    def _process_initial_statements(
        self, new_statements_to_process: list["Statement"]
    ) -> Optional["BeliefSystem"]:
        forked_belief_system = None
        for statement_to_add in new_statements_to_process:
            if not self.add_statement(statement_to_add):
                forked_belief_system = self._handle_contradiction(statement_to_add)
                break
        return forked_belief_system

    def _execute_effect(self, effect: Effect, bindings: dict):
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
                self.world_state[key] = operation_func(current_value, value)

    def _perform_inference(self):
        applied_rules_set = set()
        derived_facts_in_this_run = set()
        while True:
            newly_inferred_this_pass = set()
            for rule in self.rules:
                bindings = rule.applies_to(list(self.statements))
                if bindings is not None:
                    for consequence in rule.consequences:
                        if isinstance(consequence, Statement):
                            inferred_statement = Rule._resolve_statement_from_template(
                                consequence, bindings
                            )
                            if inferred_statement not in self.statements:
                                if not self.add_statement(inferred_statement):
                                    raise InferredContradiction(inferred_statement)
                                newly_inferred_this_pass.add(inferred_statement)
                                applied_rules_set.add(rule)
                        elif isinstance(consequence, Effect):
                            effect_key = (rule, frozenset(bindings.items()))
                            if effect_key not in self.effects_applied:
                                self._execute_effect(consequence, bindings)
                                applied_rules_set.add(rule)
                                self.effects_applied.add(effect_key)

            if not newly_inferred_this_pass:
                break
            derived_facts_in_this_run.update(newly_inferred_this_pass)
        return list(derived_facts_in_this_run), list(applied_rules_set)

    def simulate(self, new_statements_to_process: list["Statement"]):
        for fork in self.forks:
            fork.simulate(new_statements_to_process)

        forked_belief_system = self._process_initial_statements(
            new_statements_to_process
        )

        derived_facts = []
        applied_rules = []

        if not forked_belief_system:
            try:
                derived_facts, applied_rules = self._perform_inference()
            except InferredContradiction as e:
                forked_belief_system = self._handle_contradiction(e.statement)
                derived_facts = []
                applied_rules = []

        simulation_result = SimulationResult(
            derived_facts=derived_facts,
            applied_rules=applied_rules,
            forked_belief_system=forked_belief_system,
        )

        self.mcp_records.append(
            SimulationRecord(
                initial_statements=new_statements_to_process,
                derived_facts=derived_facts,
                applied_rules=applied_rules,
                forked_belief_system=forked_belief_system,
            )
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


class SimulationRecord:
    def __init__(
        self,
        initial_statements: list[Statement],
        derived_facts: list[Statement],
        applied_rules: list[Rule],
        forked_belief_system: "BeliefSystem" = None,
    ):
        self.initial_statements = initial_statements
        self.derived_facts = derived_facts
        self.applied_rules = applied_rules
        self.forked_belief_system = forked_belief_system

    def __eq__(self, other):
        if not isinstance(other, SimulationRecord):
            return NotImplemented
        return (
            self.initial_statements == other.initial_statements
            and self.derived_facts == other.derived_facts
            and self.applied_rules == other.applied_rules
            and self.forked_belief_system == other.forked_belief_system
        )

    def __hash__(self):
        return hash(
            (
                tuple(self.initial_statements),
                tuple(self.derived_facts),
                tuple(self.applied_rules),
                self.forked_belief_system,
            )
        )

