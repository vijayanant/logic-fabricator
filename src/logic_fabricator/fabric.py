class Statement:
    def __init__(self, verb: str, terms: list[str], negated: bool = False):
        self.verb = verb
        self.terms = terms
        self.negated = negated

    def __eq__(self, other):
        if not isinstance(other, Statement):
            return NotImplemented
        return (
            self.verb == other.verb
            and self.terms == other.terms
            and self.negated == other.negated
        )

    def __hash__(self):
        return hash((self.verb, tuple(self.terms), self.negated))


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

    def matches(self, statements: list["Statement"]) -> dict | None:
        if self.and_conditions is not None:
            # Handle conjunctive conditions
            # This is a recursive function to find consistent bindings across all sub-conditions
            def find_consistent_bindings(
                sub_conditions_to_match, available_statements, current_bindings
            ):
                if not sub_conditions_to_match:
                    return current_bindings  # All sub-conditions matched, return combined bindings

                sub_condition = sub_conditions_to_match[0]
                remaining_sub_conditions = sub_conditions_to_match[1:]

                for i, stmt in enumerate(available_statements):
                    sub_bindings = sub_condition.matches(
                        [stmt]
                    )  # Match sub-condition against a single statement
                    if sub_bindings is not None:
                        # Check for conflicting bindings
                        new_bindings = current_bindings.copy()
                        conflict = False
                        for key, value in sub_bindings.items():
                            if key in new_bindings and new_bindings[key] != value:
                                conflict = True
                                break
                            new_bindings[key] = value

                        if not conflict:
                            # Remove the current statement from available_statements for recursive call
                            next_available_statements = (
                                available_statements[:i] + available_statements[i + 1 :]
                            )
                            # Recursively try to match remaining sub-conditions with updated bindings
                            result = find_consistent_bindings(
                                remaining_sub_conditions,
                                next_available_statements,
                                new_bindings,
                            )
                            if result is not None:
                                return result
                return None  # No consistent match found for this sub-condition

            return find_consistent_bindings(self.and_conditions, statements, {})
        else:
            # Handle single condition
            for statement in statements:
                if self.verb != statement.verb:
                    continue

                # Ensure the statement has at least as many terms as the condition
                if len(statement.terms) < len(self.terms):
                    continue

                bindings = {}
                # Iterate only up to the length of the condition's terms
                for i in range(len(self.terms)):
                    cond_term = self.terms[i]
                    stmt_term = statement.terms[i]

                    if cond_term.startswith("?"):  # It's a variable
                        bindings[cond_term] = stmt_term
                    elif cond_term != stmt_term:  # Mismatch for literal terms
                        bindings = None  # Indicate no match for this statement
                        break

                if bindings is not None:  # If a match was found for this statement
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
        return Statement(verb=new_verb, terms=new_terms)


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


class BeliefSystem:
    def __init__(self, rules: list[Rule], contradiction_engine: ContradictionEngine):
        self.rules = rules
        self.statements = set()
        self.contradiction_engine = contradiction_engine
        self.contradictions = []
        self.mcp_records = [] # Initialize MCP records

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

    def simulate(self, initial_statements: list["Statement"]):
        # Clear statements for a fresh simulation run
        self.statements = set()
        for statement in initial_statements:
            self.add_statement(statement)

        applied_rules = set()
        while True:
            newly_inferred_this_pass = set()
            for rule in self.rules:
                bindings = rule.applies_to(list(self.statements))
                if bindings:
                    inferred_statement = rule.generate_consequence(bindings)
                    if inferred_statement not in self.statements:
                        if self.add_statement(inferred_statement):
                            newly_inferred_this_pass.add(inferred_statement)
                            applied_rules.add(rule)

            if not newly_inferred_this_pass:
                break

        derived_facts = list(self.statements - set(initial_statements))
        simulation_result = SimulationResult(
            derived_facts=derived_facts,
            applied_rules=list(applied_rules),
        )
        
        # Store the simulation record in MCP
        self.mcp_records.append(SimulationRecord(
            initial_statements=initial_statements,
            derived_facts=derived_facts,
            applied_rules=list(applied_rules)
        ))

        return simulation_result


class SimulationResult:
    def __init__(self, derived_facts: list[Statement], applied_rules: list[Rule]):
        self.derived_facts = derived_facts
        self.applied_rules = applied_rules


class SimulationRecord:
    def __init__(self, initial_statements: list[Statement], derived_facts: list[Statement], applied_rules: list[Rule]):
        self.initial_statements = initial_statements
        self.derived_facts = derived_facts
        self.applied_rules = applied_rules

    def __eq__(self, other):
        if not isinstance(other, SimulationRecord):
            return NotImplemented
        return (
            self.initial_statements == other.initial_statements
            and self.derived_facts == other.derived_facts
            and self.applied_rules == other.applied_rules
        )

    def __hash__(self):
        # Convert lists to tuples for hashing
        return hash((
            tuple(self.initial_statements),
            tuple(self.derived_facts),
            tuple(self.applied_rules)
        ))
