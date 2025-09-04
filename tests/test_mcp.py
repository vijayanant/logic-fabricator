
from logic_fabricator.fabric import (
    Statement,
    Rule,
    Condition,
    ContradictionEngine,
    BeliefSystem,
    ContradictionRecord,
    ForkingStrategy,
    Effect,
    SimulationRecord,
)


def test_belief_system_stores_simulation_record():
    rule1 = Rule(
        condition=Condition(verb="is", terms=["?x", "a man"]),
        consequences=[Statement(verb="is", terms=["?x", "mortal"])],
    )
    rule2 = Rule(
        condition=Condition(verb="is", terms=["?x", "mortal"]),
        consequences=[Statement(verb="needs", terms=["?x", "to eat"])],
    )
    belief_system = BeliefSystem(
        rules=[rule1, rule2], contradiction_engine=ContradictionEngine()
    )
    initial_statement = Statement(verb="is", terms=["Socrates", "a man"])
    simulation_result = belief_system.simulate([initial_statement])
    assert len(belief_system.mcp_records) == 1
    record = belief_system.mcp_records[0]
    assert record.initial_statements == [initial_statement]
    assert record.derived_facts == list(simulation_result.derived_facts)
    assert record.applied_rules == list(simulation_result.applied_rules)
    assert record.forked_belief_system is None


def test_belief_system_forks_on_contradiction():
    statement1 = Statement(verb="is", terms=["Socrates", "alive"])
    statement2 = Statement(verb="is", terms=["Socrates", "alive"], negated=True)
    engine = ContradictionEngine()
    belief_system = BeliefSystem(rules=[], contradiction_engine=engine)
    belief_system.simulate([statement1])
    simulation_result_fork = belief_system.simulate([statement2])
    assert statement2 not in belief_system.statements
    assert simulation_result_fork.forked_belief_system is not None
    forked_belief_system = simulation_result_fork.forked_belief_system
    assert isinstance(forked_belief_system, BeliefSystem)
    assert forked_belief_system is not belief_system
    assert statement2 in forked_belief_system.statements
    assert len(belief_system.mcp_records) == 2
    fork_record = belief_system.mcp_records[1]
    assert fork_record.initial_statements == [statement2]
    assert fork_record.forked_belief_system is not None
    assert fork_record.forked_belief_system is forked_belief_system


def test_fork_has_independent_and_empty_initial_mcp():
    parent_system = BeliefSystem(rules=[], contradiction_engine=ContradictionEngine())
    parent_system.simulate([Statement(verb="is", terms=["earth", "round"])])
    assert len(parent_system.mcp_records) == 1
    contradictory_statement = Statement(
        verb="is", terms=["earth", "round"], negated=True
    )
    sim_result_fork = parent_system.simulate([contradictory_statement])
    forked_system = sim_result_fork.forked_belief_system
    assert forked_system is not None
    assert len(forked_system.mcp_records) == 0
    forked_system.simulate([Statement(verb="is", terms=["mars", "red"])])
    assert len(forked_system.mcp_records) == 1
    assert len(parent_system.mcp_records) == 2


def test_belief_system_forks_when_rule_consequence_is_a_contradiction():
    existing_statement = Statement(verb="is", terms=["Socrates", "mortal"])
    belief_system = BeliefSystem(rules=[], contradiction_engine=ContradictionEngine())
    belief_system.add_statement(existing_statement)
    rule = Rule(
        condition=Condition(verb="is", terms=["?x", "a man"]),
        consequences=[Statement(verb="is", terms=["?x", "mortal"], negated=True)],
    )
    belief_system.rules.append(rule)
    trigger_statement = Statement(verb="is", terms=["Socrates", "a man"])
    sim_result = belief_system.simulate([trigger_statement])
    assert sim_result.forked_belief_system is not None, (
        "A fork should have been created"
    )
    forked_system = sim_result.forked_belief_system
    contradictory_statement = Rule._resolve_statement_from_template(
        rule.consequences[0], {"?x": "Socrates"}
    )
    assert contradictory_statement not in belief_system.statements
    assert len(belief_system.mcp_records) == 1
    assert existing_statement in forked_system.statements
    assert contradictory_statement in forked_system.statements


def test_belief_system_has_get_history_method():
    """Tests that a BeliefSystem can return its history via a method."""
    belief_system = BeliefSystem(rules=[], contradiction_engine=ContradictionEngine())
    initial_statement = Statement(verb="is", terms=["Socrates", "a man"])
    belief_system.simulate([initial_statement])

    # Act
    history = belief_system.get_history()

    # Assert
    assert isinstance(history, list)
    assert len(history) == 1
    assert isinstance(history[0], SimulationRecord)
    assert history[0].initial_statements == [initial_statement]
