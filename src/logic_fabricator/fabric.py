import enum
from typing import Optional


class ForkingStrategy(enum.Enum):
    COEXIST = "coexist"
    PRESERVE = "preserve"
    PRIORITIZE_NEW = "prioritize_new"


class Statement:
    def __init__(
        self, verb: str, terms: list[str], negated: bool = False, priority: float = 1.0
    ):
        self.verb = verb
        self.terms = terms
        self.negated = negated
        self.priority = priority

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
    ):
        self.and_conditions = and_conditions  # Initialize here
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

    def __eq__(self, other):
        if not isinstance(other, Condition):
            return NotImplemented
        return (
            self.verb == other.verb
            and self.terms == other.terms
            and self.and_conditions == other.and_conditions
        )

    def __hash__(self):
        # Note: and_conditions should be a tuple of conditions for hashing
        and_conditions_tuple = None
        if self.and_conditions is not None:
            and_conditions_tuple = tuple(
                sorted(self.and_conditions, key=lambda c: hash(c))
            )

        return hash(
            (self.verb, tuple(self.terms) if self.terms else None, and_conditions_tuple)
        )

    def _match_single_condition(self, statement: "Statement") -> dict | None:
        if self.verb != statement.verb:
            return None

        if len(statement.terms) < len(self.terms):
            return None

        bindings = {}
        for i in range(len(self.terms)):
            cond_term = self.terms[i]
            stmt_term = statement.terms[i]

            if cond_term.startswith("?"):  # It's a variable
                bindings[cond_term] = stmt_term
            elif cond_term != stmt_term:  # Mismatch for literal terms
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


class Rule:
    def __init__(self, condition: Condition, consequence: Statement):
        self.condition = condition
        self.consequence = consequence

    def __eq__(self, other):
        if not isinstance(other, Rule):
            return NotImplemented
        return (
            self.condition == other.condition and self.consequence == other.consequence
        )

    def __hash__(self):
        return hash((self.condition, self.consequence))

    def applies_to(self, statements: list["Statement"]) -> dict | None:
        return self.condition.matches(statements)

    def generate_consequence(self, bindings: dict) -> Statement:
        new_verb = self.consequence.verb
        new_terms = []
        for term in self.consequence.terms:
            if term.startswith("?"):
                new_terms.append(
                    bindings.get(term, term)
                )  # Use bound value, or original term if not found
            else:
                new_terms.append(term)
        return Statement(verb=new_verb, terms=new_terms, negated=self.consequence.negated)


class ContradictionEngine:
    def detect(self, s1: Statement, s2: Statement) -> bool:
        # Contradiction is defined as a statement and its direct negation.
        # e.g., "Socrates is alive" and "Socrates is not alive"
        if s1.verb == s2.verb and s1.terms == s2.terms and s1.negated != s2.negated:
            return True

        return False


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

    def fork(self, statements: set[Statement]) -> "BeliefSystem":
        forked_system = BeliefSystem(
            rules=list(self.rules),
            contradiction_engine=self.contradiction_engine,
            strategy=self.strategy,  # Forks inherit the parent's strategy
        )
        forked_system.statements = statements
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
            return None  # Do nothing

        # For both COEXIST and PRIORITIZE_NEW, we create a fork.
        # The difference is what we put inside it.
        new_statements = self.statements.copy()

        if self.strategy == ForkingStrategy.PRIORITIZE_NEW:
            old_statement = next(
                (s for s in self.statements if self.contradiction_engine.detect(contradictory_statement, s)),
                None,
            )
            if old_statement:
                # Create the new, prioritized statement and add it
                prioritized_statement = Statement(
                    verb=contradictory_statement.verb,
                    terms=contradictory_statement.terms,
                    negated=contradictory_statement.negated,
                    priority=old_statement.priority + 0.1,
                )
                new_statements.add(prioritized_statement)
            else:
                 new_statements.add(contradictory_statement) # Fallback
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

    def _perform_inference(self):
        applied_rules_set = set()
        derived_facts_in_this_run = set()
        while True:
            newly_inferred_this_pass = set()
            for rule in self.rules:
                bindings = rule.applies_to(list(self.statements))
                if bindings:
                    inferred_statement = rule.generate_consequence(bindings)
                    if inferred_statement not in self.statements:
                        if not self.add_statement(inferred_statement):
                            raise InferredContradiction(inferred_statement)
                        newly_inferred_this_pass.add(inferred_statement)
                        applied_rules_set.add(rule)
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
        # Convert lists to tuples for hashing
        return hash(
            (
                tuple(self.initial_statements),
                tuple(self.derived_facts),
                tuple(self.applied_rules),
                self.forked_belief_system,
            )
        )
