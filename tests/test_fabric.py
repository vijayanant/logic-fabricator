from logic_fabricator.fabric import (
    Statement,
    Rule,
    Condition,
    ContradictionEngine,
    BeliefSystem,
    ContradictionRecord,
    SimulationResult,
    SimulationRecord,
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

    belief_system = BeliefSystem(
        rules=[rule], contradiction_engine=ContradictionEngine()
    )
    simulation_result = belief_system.simulate([initial_statement])

    # The system should process the statement and infer the consequence
    inferred_statement = Statement(verb="is", terms=["Socrates", "mortal"])
    assert inferred_statement in simulation_result.derived_facts


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

    belief_system = BeliefSystem(
        rules=[rule], contradiction_engine=ContradictionEngine()
    )

    # Simulate with both initial statements
    simulation_result = belief_system.simulate([statement1, statement2])

    inferred_statement = Statement(verb="is", terms=["Socrates", "mortal"])
    assert inferred_statement in simulation_result.derived_facts


def test_simulation_engine_chains_inferences():
    # This test asserts that the simulation engine can chain inferences:
    # The consequence of one rule becomes the condition for another.
    rule1 = Rule(
        condition=Condition(verb="is", terms=["?x", "a man"]),
        consequence=Statement(verb="is", terms=["?x", "mortal"]),
    )
    rule2 = Rule(
        condition=Condition(verb="is", terms=["?x", "mortal"]),
        consequence=Statement(verb="needs", terms=["?x", "to eat"]),
    )

    belief_system = BeliefSystem(
        rules=[rule1, rule2], contradiction_engine=ContradictionEngine()
    )

    initial_statement = Statement(verb="is", terms=["Socrates", "a man"])

    # This is the new method we are proposing.
    # It should run the simulation to its logical conclusion.
    simulation_result = belief_system.simulate([initial_statement])

    final_statement = Statement(verb="needs", terms=["Socrates", "to eat"])
    assert final_statement in simulation_result.derived_facts


def test_simulation_result_captures_applied_rules():
    # This test asserts that the SimulationResult captures which rules were fired.
    rule1 = Rule(
        condition=Condition(verb="is", terms=["?x", "a man"]),
        consequence=Statement(verb="is", terms=["?x", "mortal"]),
    )
    # This rule will not be applied
    rule2 = Rule(
        condition=Condition(verb="is", terms=["?x", "a god"]),
        consequence=Statement(verb="is", terms=["?x", "immortal"]),
    )

    belief_system = BeliefSystem(
        rules=[rule1, rule2], contradiction_engine=ContradictionEngine()
    )

    initial_statement = Statement(verb="is", terms=["Socrates", "a man"])
    simulation_result = belief_system.simulate([initial_statement])

    assert rule1 in simulation_result.applied_rules
    assert rule2 not in simulation_result.applied_rules


def test_belief_system_stores_simulation_record():
    # This test asserts that the BeliefSystem stores a SimulationRecord
    # after a simulation, capturing key details.
    rule1 = Rule(
        condition=Condition(verb="is", terms=["?x", "a man"]),
        consequence=Statement(verb="is", terms=["?x", "mortal"]),
    )
    rule2 = Rule(
        condition=Condition(verb="is", terms=["?x", "mortal"]),
        consequence=Statement(verb="needs", terms=["?x", "to eat"]),
    )

    belief_system = BeliefSystem(
        rules=[rule1, rule2], contradiction_engine=ContradictionEngine()
    )

    initial_statement = Statement(verb="is", terms=["Socrates", "a man"])
    simulation_result = belief_system.simulate([initial_statement])

    # Assert that a SimulationRecord was stored
    assert len(belief_system.mcp_records) == 1
    record = belief_system.mcp_records[0]

    # Assert the content of the SimulationRecord
    assert record.initial_statements == [initial_statement]
    assert record.derived_facts == list(simulation_result.derived_facts)
    assert record.applied_rules == list(simulation_result.applied_rules)
    assert record.forked_belief_system is None


def test_belief_system_forks_on_contradiction():
    # This test asserts that when a contradiction is detected during add_statement,
    # the BeliefSystem creates a new, forked BeliefSystem instance.
    statement1 = Statement(verb="is", terms=["Socrates", "alive"])
    statement2 = Statement(verb="is", terms=["Socrates", "alive"], negated=True)

    engine = ContradictionEngine()
    belief_system = BeliefSystem(rules=[], contradiction_engine=engine)

    # Simulate adding the first statement
    simulation_result_initial = belief_system.simulate([statement1])

    # Now, introduce the contradictory statement. This should trigger a fork.
    simulation_result_fork = belief_system.simulate([statement2])

    # Assert that the original belief system does NOT contain the contradictory statement
    assert statement2 not in belief_system.statements

    # Assert that the forked belief system is returned in the SimulationResult
    assert simulation_result_fork.forked_belief_system is not None
    forked_belief_system = simulation_result_fork.forked_belief_system

    # Assert that the forked belief system contains the contradictory statement
    # and that it is a new instance.
    assert isinstance(forked_belief_system, BeliefSystem)
    assert forked_belief_system is not belief_system
    assert statement2 in forked_belief_system.statements

    # Assert that a SimulationRecord was stored for the fork
    assert len(belief_system.mcp_records) == 2  # One for initial, one for fork
    fork_record = belief_system.mcp_records[1]
    assert fork_record.initial_statements == [statement2]
    assert fork_record.forked_belief_system is not None
    assert fork_record.forked_belief_system is forked_belief_system


def test_forked_system_is_independently_simulatable():
    # This test asserts that a forked BeliefSystem is a fully independent entity
    # that can be simulated on its own.
    rule = Rule(
        condition=Condition(verb="is", terms=["?x", "a god"]),
        consequence=Statement(verb="is", terms=["?x", "immortal"]),
    )
    belief_system = BeliefSystem(
        rules=[rule], contradiction_engine=ContradictionEngine()
    )

    # 1. Add a statement to the parent system.
    original_statement = Statement(verb="is", terms=["Socrates", "alive"])
    belief_system.simulate([original_statement])

    # 2. Create a fork by introducing a contradiction.
    contradictory_statement = Statement(
        verb="is", terms=["Socrates", "alive"], negated=True
    )
    sim_result_fork = belief_system.simulate([contradictory_statement])
    forked_system = sim_result_fork.forked_belief_system
    assert forked_system is not None

    # 3. Now, run a *new* simulation on the forked system.
    new_statement_for_fork = Statement(verb="is", terms=["Zeus", "a god"])
    fork_sim_result = forked_system.simulate([new_statement_for_fork])

    # 4. Assert that the forked system evolved, but the original did not.
    expected_derived_fact = Statement(verb="is", terms=["Zeus", "immortal"])
    assert expected_derived_fact in fork_sim_result.derived_facts
    assert expected_derived_fact in forked_system.statements
    assert expected_derived_fact not in belief_system.statements

    # 5. Verify the original system's state is unchanged by the fork's simulation.
    assert new_statement_for_fork not in belief_system.statements


def test_fork_coexistence_principle():
    # This test codifies the "Coexistence Principle" from our documentation.
    # A fork must contain both the original statement and the new one that contradicts it.
    original_statement = Statement(verb="is", terms=["Socrates", "alive"])
    contradictory_statement = Statement(
        verb="is", terms=["Socrates", "alive"], negated=True
    )

    belief_system = BeliefSystem(rules=[], contradiction_engine=ContradictionEngine())

    # 1. Add the original statement.
    belief_system.simulate([original_statement])
    assert original_statement in belief_system.statements

    # 2. Introduce the contradiction, which should cause a fork.
    sim_result = belief_system.simulate([contradictory_statement])

    # 3. Get the forked system.
    assert sim_result.forked_belief_system is not None
    forked_system = sim_result.forked_belief_system

    # 4. Assert that the forked system contains BOTH statements.
    assert original_statement in forked_system.statements
    assert contradictory_statement in forked_system.statements

    # 5. Assert the original system was NOT changed.
    assert contradictory_statement not in belief_system.statements


def test_simulation_propagates_to_forks():
    """
    Tests that simulating the parent BeliefSystem also simulates its forks.
    This is a core principle of the "Fork Evolution and Simulation" design.
    """
    # 1. Create a parent system
    parent_system = BeliefSystem(rules=[], contradiction_engine=ContradictionEngine())

    # 2. Create a fork by introducing a contradiction
    original_statement = Statement(verb="is", terms=["sky", "blue"])
    contradictory_statement = Statement(verb="is", terms=["sky", "blue"], negated=True)
    parent_system.simulate([original_statement])
    sim_result_fork = parent_system.simulate([contradictory_statement])
    forked_system = sim_result_fork.forked_belief_system
    assert forked_system is not None

    # 3. Add a unique rule to the FORKED system
    fork_only_rule = Rule(
        condition=Condition(verb="is", terms=["?x", "bright"]),
        consequence=Statement(verb="emits", terms=["?x", "light"]),
    )
    forked_system.rules.append(fork_only_rule)

    # 4. Simulate a NEW statement on the PARENT system
    new_statement = Statement(verb="is", terms=["sun", "bright"])
    parent_system.simulate([new_statement])

    # 5. Assert that the fork ALSO simulated the new statement and applied its unique rule
    expected_derived_fact = Statement(verb="emits", terms=["sun", "light"])
    assert expected_derived_fact in forked_system.statements


def test_fork_has_independent_and_empty_initial_mcp():
    """
    Tests that a forked BeliefSystem starts with its own empty MCP history,
    independent of the parent's history.
    """
    # 1. Create a parent system and give it a history
    parent_system = BeliefSystem(rules=[], contradiction_engine=ContradictionEngine())
    parent_system.simulate([Statement(verb="is", terms=["earth", "round"])])
    assert len(parent_system.mcp_records) == 1

    # 2. Create a fork
    contradictory_statement = Statement(
        verb="is", terms=["earth", "round"], negated=True
    )
    sim_result_fork = parent_system.simulate([contradictory_statement])
    forked_system = sim_result_fork.forked_belief_system
    assert forked_system is not None

    # 3. Assert the fork's MCP is empty to start
    assert len(forked_system.mcp_records) == 0

    # 4. Simulate on the fork and assert it creates its own history
    forked_system.simulate([Statement(verb="is", terms=["mars", "red"])])
    assert len(forked_system.mcp_records) == 1

    # 5. Assert the parent's history remains unchanged
    assert len(parent_system.mcp_records) == 2 # Initial sim + the fork event


def test_fork_can_itself_be_forked():
    """
    Tests that a forked belief system can, in turn, create its own forks,
    establishing a multi-level "logic multiverse".
    """
    # 1. Setup parent and first-level fork
    parent_system = BeliefSystem(rules=[], contradiction_engine=ContradictionEngine())
    parent_system.simulate([Statement(verb="is", terms=["A", "B"])])
    sim_result_fork1 = parent_system.simulate(
        [Statement(verb="is", terms=["A", "B"], negated=True)]
    )
    fork1 = sim_result_fork1.forked_belief_system
    assert fork1 is not None

    # 2. Introduce a new, different contradiction into the *first fork*
    fork1.simulate([Statement(verb="is", terms=["C", "D"])])
    sim_result_fork2 = fork1.simulate(
        [Statement(verb="is", terms=["C", "D"], negated=True)]
    )
    fork2 = sim_result_fork2.forked_belief_system
    assert fork2 is not None

    # 3. Assert that fork2 is a child of fork1, not the parent
    assert fork2 in fork1.forks
    assert fork2 not in parent_system.forks

    # 4. Assert that fork2 contains the state from fork1
    assert Statement(verb="is", terms=["A", "B"]) in fork2.statements
    assert Statement(verb="is", terms=["A", "B"], negated=True) in fork2.statements
    assert Statement(verb="is", terms=["C", "D"]) in fork2.statements
    assert Statement(verb="is", terms=["C", "D"], negated=True) in fork2.statements


def test_belief_system_forks_when_rule_consequence_is_a_contradiction():
    """
    Tests the final piece of the MVP: the system must fork when a rule's
    consequence contradicts an existing statement during the inference phase.
    """
    # 1. Setup a belief system with an established fact.
    existing_statement = Statement(verb="is", terms=["Socrates", "mortal"])
    belief_system = BeliefSystem(
        rules=[], contradiction_engine=ContradictionEngine()
    )
    belief_system.add_statement(existing_statement)

    # 2. Add a rule that, when triggered, will contradict the established fact.
    rule = Rule(
        condition=Condition(verb="is", terms=["?x", "a man"]),
        consequence=Statement(verb="is", terms=["?x", "mortal"], negated=True),
    )
    belief_system.rules.append(rule)

    # 3. Simulate with a statement that triggers the rule.
    trigger_statement = Statement(verb="is", terms=["Socrates", "a man"])
    sim_result = belief_system.simulate([trigger_statement])

    # 4. Assert that a fork was created.
    assert sim_result.forked_belief_system is not None, "A fork should have been created"
    forked_system = sim_result.forked_belief_system

    # 5. Assert the original system is unchanged and contains no new contradictory facts.
    contradictory_statement = Statement(verb="is", terms=["Socrates", "mortal"], negated=True)
    assert contradictory_statement not in belief_system.statements
    assert len(belief_system.mcp_records) == 1 # Should only contain the fork record

    # 6. Assert the forked system contains the full paradox.
    assert existing_statement in forked_system.statements
    assert contradictory_statement in forked_system.statements