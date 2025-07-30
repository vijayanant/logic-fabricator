from logic_fabricator.fabric import (
    Statement,
    Rule,
    Condition,
    ContradictionEngine,
    BeliefSystem,
    ContradictionRecord,
)


def test_statement_has_structure():
    # This test proposes the initial structure of our Statement object.
    s = Statement(verb="is", terms=["Socrates", "a man"])
    assert s.verb == "is"
    assert s.terms == ["Socrates", "a man"]


def test_rule_applies_to_statement_by_verb():
    # This test proposes the initial structure of our Rule object
    # and its basic application logic based on verb matching.
    # It will fail because the Rule class does not yet exist,
    # and the applies_to method is not implemented.
    statement = Statement(verb="is", terms=[])
    rule = Rule(
        condition=Condition(verb="is", terms=[]),
        consequence=Statement(verb="", terms=[]),  # Placeholder consequence
    )  # Use Condition object with empty terms

    assert rule.applies_to(statement) is not None


def test_rule_applies_with_variable_binding():
    # This test proposes that Rule.applies_to should return bindings
    # when a variable in the condition matches a term in the statement.
    statement = Statement(verb="is", terms=["Socrates", "a man"])
    condition = Condition(verb="is", terms=["?x", "a man"])
    rule = Rule(condition=condition, consequence=Statement(verb="", terms=[]))

    bindings = rule.applies_to(statement)
    assert bindings == {"?x": "Socrates"}

    # Test a non-matching case
    statement_no_match = Statement(verb="is", terms=["Plato", "a philosopher"])
    bindings_no_match = rule.applies_to(statement_no_match)
    assert bindings_no_match is None


def test_rule_applies_with_fewer_condition_terms():
    # This test challenges the strict term count matching.
    # A rule with fewer terms should still match if its terms are present
    # at the beginning of the statement's terms.
    statement = Statement(verb="is", terms=["Socrates", "a man", "wise"])
    condition = Condition(verb="is", terms=["?x", "a man"])
    rule = Rule(condition=condition, consequence=Statement(verb="", terms=[]))

    bindings = rule.applies_to(statement)
    assert bindings == {"?x": "Socrates"}


def test_rule_generates_consequence_from_bindings():
    # This test verifies that a Rule can generate a new Statement
    # based on its consequence template and extracted bindings.
    statement = Statement(verb="is", terms=["Socrates", "a man"])
    condition = Condition(verb="is", terms=["?x", "a man"])
    consequence_template = Statement(verb="is", terms=["?x", "mortal"])
    rule = Rule(condition=condition, consequence=consequence_template)

    bindings = rule.applies_to(statement)
    assert bindings == {"?x": "Socrates"}

    generated_statement = rule.generate_consequence(bindings)
    expected_statement = Statement(verb="is", terms=["Socrates", "mortal"])
    assert generated_statement.verb == expected_statement.verb
    assert generated_statement.terms == expected_statement.terms


def test_contradiction_detection_simple():
    # This test proposes a simple contradiction detection mechanism.
    # It will fail because the ContradictionEngine and its logic do not yet exist.
    statement1 = Statement(verb="is", terms=["Socrates", "alive"])
    statement2 = Statement(verb="is", terms=["Socrates", "dead"])

    engine = ContradictionEngine()

    assert engine.detect(statement1, statement2) is True


def test_belief_system_infers_statement():
    # This test verifies that the BeliefSystem can infer new statements
    # by applying rules to its existing statements.
    initial_statement = Statement(verb="is", terms=["Socrates", "a man"])
    rule_condition = Condition(verb="is", terms=["?x", "a man"])
    rule_consequence = Statement(verb="is", terms=["?x", "mortal"])
    rule = Rule(condition=rule_condition, consequence=rule_consequence)

    belief_system = BeliefSystem(
        rules=[rule], contradiction_engine=ContradictionEngine()
    )
    belief_system.add_statement(initial_statement)

    # The system should process the statement and infer the consequence
    inferred_statement = Statement(verb="is", terms=["Socrates", "mortal"])
    assert inferred_statement in belief_system.statements


def test_belief_system_detects_contradiction():
    # This test verifies that the BeliefSystem detects contradictions
    # when new statements are added.
    statement1 = Statement(verb="is", terms=["Socrates", "alive"])
    statement2 = Statement(verb="is", terms=["Socrates", "dead"])

    engine = ContradictionEngine()
    belief_system = BeliefSystem(rules=[], contradiction_engine=engine)

    belief_system.add_statement(statement1)
    belief_system.add_statement(statement2)

    # Assert that the contradiction was detected and stored
    assert len(belief_system.contradictions) == 1
    # For now, we'll just check the count. Later, we can assert the content of the contradiction.


def test_belief_system_stores_contradiction_record():
    # This test verifies that the BeliefSystem stores a ContradictionRecord
    # when a contradiction is detected.
    statement1 = Statement(verb="is", terms=["Socrates", "alive"])
    statement2 = Statement(verb="is", terms=["Socrates", "dead"])

    engine = ContradictionEngine()
    belief_system = BeliefSystem(rules=[], contradiction_engine=engine)

    belief_system.add_statement(statement1)
    belief_system.add_statement(statement2)

    assert len(belief_system.contradictions) == 1
    contradiction_record = belief_system.contradictions[0]
    assert isinstance(contradiction_record, ContradictionRecord)
    assert contradiction_record.statement1 == statement2
    assert contradiction_record.statement2 == statement1
