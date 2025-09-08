import pytest
from neo4j import GraphDatabase

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
    assert existing_statement in forked_system.statements
    assert contradictory_statement in forked_system.statements





