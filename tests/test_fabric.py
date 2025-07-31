from logic_fabricator.fabric import (
    Statement,
    Rule,
    Condition,
    ContradictionEngine,
    BeliefSystem,
    ContradictionRecord
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

    assert rule.applies_to([statement]) is not None


def test_rule_applies_with_variable_binding():
    # This test proposes that Rule.applies_to should return bindings
    # when a variable in the condition matches a term in the statement.
    statement = Statement(verb="is", terms=["Socrates", "a man"])
    condition = Condition(verb="is", terms=["?x", "a man"])
    rule = Rule(condition=condition, consequence=Statement(verb="", terms=[]))

    bindings = rule.applies_to([statement])
    assert bindings == {"?x": "Socrates"}

    # Test a non-matching case
    statement_no_match = Statement(verb="is", terms=["Plato", "a philosopher"])
    bindings_no_match = rule.applies_to([statement_no_match])
    assert bindings_no_match is None


def test_rule_applies_with_fewer_condition_terms():
    # This test challenges the strict term count matching.
    # A rule with fewer terms should still match if its terms are present
    # at the beginning of the statement's terms.
    statement = Statement(verb="is", terms=["Socrates", "a man", "wise"])
    condition = Condition(verb="is", terms=["?x", "a man"])
    rule = Rule(condition=condition, consequence=Statement(verb="", terms=[]))

    bindings = rule.applies_to([statement])
    assert bindings == {"?x": "Socrates"}


def test_rule_generates_consequence_from_bindings():
    # This test verifies that a Rule can generate a new Statement
    # based on its consequence template and extracted bindings.
    statement = Statement(verb="is", terms=["Socrates", "a man"])
    condition = Condition(verb="is", terms=["?x", "a man"])
    consequence_template = Statement(verb="is", terms=["?x", "mortal"])
    rule = Rule(condition=condition, consequence=consequence_template)

    bindings = rule.applies_to([statement])
    assert bindings == {"?x": "Socrates"}

    generated_statement = rule.generate_consequence(bindings)
    expected_statement = Statement(verb="is", terms=["Socrates", "mortal"])
    assert generated_statement.verb == expected_statement.verb
    assert generated_statement.terms == expected_statement.terms


def test_contradiction_detection_simple():
    # This test proposes a simple contradiction detection mechanism.
    # It will fail because the ContradictionEngine and its logic do not yet exist.
    statement1 = Statement(verb="is", terms=["Socrates", "alive"])
    statement2 = Statement(verb="is", terms=["Socrates", "alive"], negated=True)

    engine = ContradictionEngine()

    assert engine.detect(statement1, statement2) is True


def test_belief_system_infers_statement():
    # This test verifies that the BeliefSystem can infer new statements
    # by applying rules to its existing statements.
    initial_statement = Statement(verb="is", terms=["Socrates", "a man"])
    rule_condition = Condition(verb="is", terms=["?x", "a man"])
    rule_consequence = Statement(verb="is", terms=["?x", "mortal"])
    rule = Rule(condition=rule_condition, consequence=rule_consequence)

    belief_system = BeliefSystem(rules=[rule], contradiction_engine=ContradictionEngine())
    belief_system.add_statement(initial_statement)

    # The system should process the statement and infer the consequence
    inferred_statement = Statement(verb="is", terms=["Socrates", "mortal"])
    assert inferred_statement in belief_system.statements


def test_belief_system_detects_contradiction():
    # This test verifies that the BeliefSystem detects contradictions
    # when new statements are added.
    statement1 = Statement(verb="is", terms=["Socrates", "alive"])
    statement2 = Statement(verb="is", terms=["Socrates", "alive"], negated=True)

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
    statement2 = Statement(verb="is", terms=["Socrates", "alive"], negated=True)

    engine = ContradictionEngine()
    belief_system = BeliefSystem(rules=[], contradiction_engine=engine)

    belief_system.add_statement(statement1)
    belief_system.add_statement(statement2)

    assert len(belief_system.contradictions) == 1
    contradiction_record = belief_system.contradictions[0]
    assert isinstance(contradiction_record, ContradictionRecord)
    assert contradiction_record.statement1 == statement2
    assert contradiction_record.statement2 == statement1


def test_belief_system_prevents_contradictory_statement_addition():
    # This test verifies that a contradictory statement is NOT added
    # to the main statements list, but IS recorded as a contradiction.
    statement1 = Statement(verb="is", terms=["Socrates", "alive"])
    statement2 = Statement(verb="is", terms=["Socrates", "alive"], negated=True)

    engine = ContradictionEngine()
    belief_system = BeliefSystem(rules=[], contradiction_engine=engine)

    belief_system.add_statement(statement1)
    belief_system.add_statement(statement2)

    # Assert that the contradictory statement is NOT in the main list
    assert statement2 not in belief_system.statements

    # Assert that the contradiction IS recorded
    assert len(belief_system.contradictions) == 1
    contradiction_record = belief_system.contradictions[0]
    assert contradiction_record.statement1 == statement2
    assert contradiction_record.statement2 == statement1


def test_contradiction_detection_negation():
    # This test verifies that the ContradictionEngine can detect contradictions
    # involving negation.
    statement1 = Statement(verb="is", terms=["Socrates", "alive"])
    statement2 = Statement(verb="is", terms=["Socrates", "alive"], negated=True)

    engine = ContradictionEngine()

    assert engine.detect(statement1, statement2) is True


def test_condition_stores_and_conditions():
    # This test verifies that the Condition class can store a list of sub-conditions
    # for conjunctive (AND) logic.
    sub_condition1 = Condition(verb="is", terms=["?x", "a man"])
    sub_condition2 = Condition(verb="is", terms=["?x", "wise"])

    conjunctive_condition = Condition(and_conditions=[sub_condition1, sub_condition2])

    assert conjunctive_condition.and_conditions == [sub_condition1, sub_condition2]
    assert conjunctive_condition.verb is None
    assert conjunctive_condition.terms is None


def test_rule_with_conjunctive_condition_infers_statement():
    # This test verifies that a Rule with multiple conditions (ANDed)
    # can infer a new statement when all conditions are met.

    # Initial statements in the belief system
    statement1 = Statement(verb="is", terms=["Socrates", "a man"])
    statement2 = Statement(verb="is", terms=["Socrates", "wise"])

    # Rule with a conjunctive condition
    # If ?x is a man AND ?x is wise, then ?x is mortal
    condition_man = Condition(verb="is", terms=["?x", "a man"])
    condition_wise = Condition(verb="is", terms=["?x", "wise"])
    
    # This is the new structure we're proposing for Condition
    conjunctive_condition = Condition(and_conditions=[condition_man, condition_wise])
    
    consequence_template = Statement(verb="is", terms=["?x", "mortal"])
    rule = Rule(condition=conjunctive_condition, consequence=consequence_template)

    belief_system = BeliefSystem(rules=[rule], contradiction_engine=ContradictionEngine())
    
    # Add statements one by one to simulate processing
    belief_system.add_statement(statement1)
    belief_system.add_statement(statement2) # This addition should trigger the rule

    inferred_statement = Statement(verb="is", terms=["Socrates", "mortal"])
    assert inferred_statement in belief_system.statements
