from logic_fabricator.fabric import (
    Statement,
    Rule,
    Condition,
    ContradictionEngine,
    BeliefSystem,
    ContradictionRecord,
    ForkingStrategy,
    Effect,
)
import json


def test_statement_has_structure():
    s = Statement(verb="is", terms=["Socrates", "a man"])
    assert s.verb == "is"
    assert s.terms == ["Socrates", "a man"]


def test_rule_applies_to_statement_by_verb():
    statement = Statement(verb="is", terms=[])
    rule = Rule(
        condition=Condition(verb="is", terms=[]),
        consequences=[Statement(verb="", terms=[])],
    )
    assert rule.applies_to([statement]) is not None


def test_rule_applies_to_statement_with_synonym():
    statement = Statement(verb="relies on", terms=["Alice", "Bob"])
    condition = Condition(
        verb="trusts",
        terms=["?x", "?y"],
        verb_synonyms=["relies on", "has faith in"],
    )
    rule = Rule(condition=condition, consequences=[])
    bindings = rule.applies_to([statement])
    assert bindings == {"?x": "Alice", "?y": "Bob"}


def test_rule_applies_with_variable_binding():
    statement = Statement(verb="is", terms=["Socrates", "a man"])
    condition = Condition(verb="is", terms=["?x", "a man"])
    rule = Rule(condition=condition, consequences=[])
    bindings = rule.applies_to([statement])
    assert bindings == {"?x": "Socrates"}
    statement_no_match = Statement(verb="is", terms=["Plato", "a philosopher"])
    bindings_no_match = rule.applies_to([statement_no_match])
    assert bindings_no_match is None


def test_rule_applies_with_fewer_condition_terms():
    statement = Statement(verb="is", terms=["Socrates", "a man", "wise"])
    condition = Condition(verb="is", terms=["?x", "a man"])
    rule = Rule(condition=condition, consequences=[])
    bindings = rule.applies_to([statement])
    assert bindings == {"?x": "Socrates"}


def test_rule_generates_consequence_from_bindings():
    condition = Condition(verb="is", terms=["?x", "a man"])
    consequence_template = Statement(verb="is", terms=["?x", "mortal"])
    rule = Rule(condition=condition, consequences=[consequence_template])
    bindings = {"?x": "Socrates"}
    generated_statement = Rule._resolve_statement_from_template(
        rule.consequences[0], bindings
    )
    expected_statement = Statement(verb="is", terms=["Socrates", "mortal"])
    assert generated_statement == expected_statement


def test_rule_generates_negated_consequence():
    condition = Condition(verb="is", terms=["?x", "a man"])
    consequence_template = Statement(verb="is", terms=["?x", "immortal"], negated=True)
    rule = Rule(condition=condition, consequences=[consequence_template])
    bindings = {"?x": "Socrates"}
    generated_statement = Rule._resolve_statement_from_template(
        rule.consequences[0], bindings
    )
    assert generated_statement.negated is True


def test_contradiction_detection_simple():
    statement1 = Statement(verb="is", terms=["Socrates", "alive"])
    statement2 = Statement(verb="is", terms=["Socrates", "alive"], negated=True)
    engine = ContradictionEngine()
    assert engine.detect(statement1, statement2) is True


def test_belief_system_infers_statement():
    initial_statement = Statement(verb="is", terms=["Socrates", "a man"])
    rule_condition = Condition(verb="is", terms=["?x", "a man"])
    rule_consequence = Statement(verb="is", terms=["?x", "mortal"])
    rule = Rule(condition=rule_condition, consequences=[rule_consequence])
    belief_system = BeliefSystem(
        rules=[rule], contradiction_engine=ContradictionEngine()
    )
    simulation_result = belief_system.simulate([initial_statement])
    inferred_statement = Statement(verb="is", terms=["Socrates", "mortal"])
    assert inferred_statement in simulation_result.derived_facts


def test_belief_system_detects_contradiction():
    statement1 = Statement(verb="is", terms=["Socrates", "alive"])
    statement2 = Statement(verb="is", terms=["Socrates", "alive"], negated=True)
    engine = ContradictionEngine()
    belief_system = BeliefSystem(rules=[], contradiction_engine=engine)
    belief_system.add_statement(statement1)
    belief_system.add_statement(statement2)
    assert len(belief_system.contradictions) == 1


def test_belief_system_stores_contradiction_record():
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
    statement1 = Statement(verb="is", terms=["Socrates", "alive"])
    statement2 = Statement(verb="is", terms=["Socrates", "alive"], negated=True)
    engine = ContradictionEngine()
    belief_system = BeliefSystem(rules=[], contradiction_engine=engine)
    belief_system.add_statement(statement1)
    belief_system.add_statement(statement2)
    assert statement2 not in belief_system.statements
    assert len(belief_system.contradictions) == 1
    contradiction_record = belief_system.contradictions[0]
    assert contradiction_record.statement1 == statement2
    assert contradiction_record.statement2 == statement1


def test_contradiction_detection_negation():
    statement1 = Statement(verb="is", terms=["Socrates", "alive"])
    statement2 = Statement(verb="is", terms=["Socrates", "alive"], negated=True)
    engine = ContradictionEngine()
    assert engine.detect(statement1, statement2) is True


def test_condition_stores_and_conditions():
    sub_condition1 = Condition(verb="is", terms=["?x", "a man"])
    sub_condition2 = Condition(verb="is", terms=["?x", "wise"])
    conjunctive_condition = Condition(and_conditions=[sub_condition1, sub_condition2])
    assert conjunctive_condition.and_conditions == [sub_condition1, sub_condition2]
    assert conjunctive_condition.verb is None
    assert conjunctive_condition.terms is None


def test_rule_with_conjunctive_condition_infers_statement():
    statement1 = Statement(verb="is", terms=["Socrates", "a man"])
    statement2 = Statement(verb="is", terms=["Socrates", "wise"])
    condition_man = Condition(verb="is", terms=["?x", "a man"])
    condition_wise = Condition(verb="is", terms=["?x", "wise"])
    conjunctive_condition = Condition(and_conditions=[condition_man, condition_wise])
    consequence_template = Statement(verb="is", terms=["?x", "mortal"])
    rule = Rule(condition=conjunctive_condition, consequences=[consequence_template])
    belief_system = BeliefSystem(
        rules=[rule], contradiction_engine=ContradictionEngine()
    )
    simulation_result = belief_system.simulate([statement1, statement2])
    inferred_statement = Statement(verb="is", terms=["Socrates", "mortal"])
    assert inferred_statement in simulation_result.derived_facts


def test_simulation_engine_chains_inferences():
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
    final_statement = Statement(verb="needs", terms=["Socrates", "to eat"])
    assert final_statement in simulation_result.derived_facts


def test_simulation_result_captures_applied_rules():
    rule1 = Rule(
        condition=Condition(verb="is", terms=["?x", "a man"]),
        consequences=[Statement(verb="is", terms=["?x", "mortal"])],
    )
    rule2 = Rule(
        condition=Condition(verb="is", terms=["?x", "a god"]),
        consequences=[Statement(verb="is", terms=["?x", "immortal"])],
    )
    belief_system = BeliefSystem(
        rules=[rule1, rule2], contradiction_engine=ContradictionEngine()
    )
    initial_statement = Statement(verb="is", terms=["Socrates", "a man"])
    simulation_result = belief_system.simulate([initial_statement])
    assert rule1 in simulation_result.applied_rules
    assert rule2 not in simulation_result.applied_rules


def test_forked_system_is_independently_simulatable():
    rule = Rule(
        condition=Condition(verb="is", terms=["?x", "a god"]),
        consequences=[Statement(verb="is", terms=["?x", "immortal"])],
    )
    belief_system = BeliefSystem(
        rules=[rule], contradiction_engine=ContradictionEngine()
    )
    original_statement = Statement(verb="is", terms=["Socrates", "alive"])
    belief_system.simulate([original_statement])
    contradictory_statement = Statement(
        verb="is", terms=["Socrates", "alive"], negated=True
    )
    sim_result_fork = belief_system.simulate([contradictory_statement])
    forked_system = sim_result_fork.forked_belief_system
    assert forked_system is not None
    new_statement_for_fork = Statement(verb="is", terms=["Zeus", "a god"])
    fork_sim_result = forked_system.simulate([new_statement_for_fork])
    expected_derived_fact = Statement(verb="is", terms=["Zeus", "immortal"])
    assert expected_derived_fact in fork_sim_result.derived_facts
    assert expected_derived_fact in forked_system.statements
    assert expected_derived_fact not in belief_system.statements
    assert new_statement_for_fork not in belief_system.statements


def test_fork_coexistence_principle():
    original_statement = Statement(verb="is", terms=["Socrates", "alive"])
    contradictory_statement = Statement(
        verb="is", terms=["Socrates", "alive"], negated=True
    )
    belief_system = BeliefSystem(rules=[], contradiction_engine=ContradictionEngine())
    belief_system.simulate([original_statement])
    assert original_statement in belief_system.statements
    sim_result = belief_system.simulate([contradictory_statement])
    assert sim_result.forked_belief_system is not None
    forked_system = sim_result.forked_belief_system
    assert original_statement in forked_system.statements
    assert contradictory_statement in forked_system.statements
    assert contradictory_statement not in belief_system.statements


def test_simulation_propagates_to_forks():
    parent_system = BeliefSystem(rules=[], contradiction_engine=ContradictionEngine())
    original_statement = Statement(verb="is", terms=["sky", "blue"])
    contradictory_statement = Statement(verb="is", terms=["sky", "blue"], negated=True)
    parent_system.simulate([original_statement])
    sim_result_fork = parent_system.simulate([contradictory_statement])
    forked_system = sim_result_fork.forked_belief_system
    assert forked_system is not None
    fork_only_rule = Rule(
        condition=Condition(verb="is", terms=["?x", "bright"]),
        consequences=[Statement(verb="emits", terms=["?x", "light"])],
    )
    forked_system.rules.append(fork_only_rule)
    new_statement = Statement(verb="is", terms=["sun", "bright"])
    parent_system.simulate([new_statement])
    expected_derived_fact = Statement(verb="emits", terms=["sun", "light"])
    assert expected_derived_fact in forked_system.statements


def test_fork_can_itself_be_forked():
    parent_system = BeliefSystem(rules=[], contradiction_engine=ContradictionEngine())
    parent_system.simulate([Statement(verb="is", terms=["A", "B"])])
    sim_result_fork1 = parent_system.simulate(
        [Statement(verb="is", terms=["A", "B"], negated=True)]
    )
    fork1 = sim_result_fork1.forked_belief_system
    assert fork1 is not None
    fork1.simulate([Statement(verb="is", terms=["C", "D"])])
    sim_result_fork2 = fork1.simulate(
        [Statement(verb="is", terms=["C", "D"], negated=True)]
    )
    fork2 = sim_result_fork2.forked_belief_system
    assert fork2 is not None
    assert fork2 in fork1.forks
    assert fork2 not in parent_system.forks
    assert Statement(verb="is", terms=["A", "B"]) in fork2.statements
    assert Statement(verb="is", terms=["A", "B"], negated=True) in fork2.statements
    assert Statement(verb="is", terms=["C", "D"]) in fork2.statements
    assert Statement(verb="is", terms=["C", "D"], negated=True) in fork2.statements


def test_belief_system_with_preserve_strategy_rejects_contradiction():
    initial_statement = Statement(verb="is", terms=["sky", "blue"])
    belief_system = BeliefSystem(
        rules=[],
        contradiction_engine=ContradictionEngine(),
        strategy=ForkingStrategy.PRESERVE,
    )
    belief_system.add_statement(initial_statement)
    contradictory_statement = Statement(verb="is", terms=["sky", "blue"], negated=True)
    sim_result = belief_system.simulate([contradictory_statement])
    assert sim_result.forked_belief_system is None, (
        "No fork should be created with PRESERVE strategy"
    )
    assert contradictory_statement not in belief_system.statements
    assert len(belief_system.contradictions) == 1
    assert belief_system.contradictions[0].statement1 == contradictory_statement


def test_belief_system_with_prioritize_new_strategy_forks_with_prioritized_statement():
    initial_statement = Statement(verb="is", terms=["sky", "blue"], priority=1.0)
    belief_system = BeliefSystem(
        rules=[],
        contradiction_engine=ContradictionEngine(),
        strategy=ForkingStrategy.PRIORITIZE_NEW,
    )
    belief_system.add_statement(initial_statement)
    contradictory_statement = Statement(
        verb="is", terms=["sky", "blue"], negated=True, priority=1.0
    )
    sim_result = belief_system.simulate([contradictory_statement])
    assert sim_result.forked_belief_system is not None
    forked_system = sim_result.forked_belief_system
    old_statement_in_fork = next(s for s in forked_system.statements if not s.negated)
    new_statement_in_fork = next(s for s in forked_system.statements if s.negated)
    assert new_statement_in_fork.priority > old_statement_in_fork.priority


def test_belief_system_with_prioritize_old_strategy_forks_with_deprioritized_statement():
    initial_statement = Statement(
        verb="is", terms=["truth", "established"], priority=1.0
    )
    belief_system = BeliefSystem(
        rules=[],
        contradiction_engine=ContradictionEngine(),
        strategy=ForkingStrategy.PRIORITIZE_OLD,
    )
    belief_system.add_statement(initial_statement)
    contradictory_statement = Statement(
        verb="is", terms=["truth", "established"], negated=True, priority=1.0
    )
    sim_result = belief_system.simulate([contradictory_statement])
    assert sim_result.forked_belief_system is not None
    forked_system = sim_result.forked_belief_system
    old_statement_in_fork = next(s for s in forked_system.statements if not s.negated)
    new_statement_in_fork = next(s for s in forked_system.statements if s.negated)
    assert old_statement_in_fork.priority > new_statement_in_fork.priority


def test_rule_with_effect_modifies_world_state():
    """Tests that a rule with a generic Effect can modify the world_state."""
    belief_system = BeliefSystem(rules=[], contradiction_engine=ContradictionEngine())
    rule = Rule(
        condition=Condition(verb="is", terms=["alarm", "on"]),
        consequences=[
            Effect(
                target="world_state", attribute="status", operation="set", value="alert"
            )
        ],
    )
    belief_system.rules.append(rule)
    initial_statement = Statement(verb="is", terms=["alarm", "on"])
    belief_system.simulate([initial_statement])
    assert belief_system.world_state.get("status") == "alert"


def test_rule_with_effect_and_statement_consequences():
    """Tests that a rule can have both a Statement and an Effect as consequences."""
    belief_system = BeliefSystem(rules=[], contradiction_engine=ContradictionEngine())
    rule = Rule(
        condition=Condition(verb="is", terms=["?x", "a traitor"]),
        consequences=[
            Statement(verb="is", terms=["?x", "exiled"]),
            Effect(
                target="world_state",
                attribute="population",
                operation="decrement",
                value=1,
            ),
        ],
    )
    belief_system.world_state["population"] = 10
    belief_system.rules.append(rule)
    initial_statement = Statement(verb="is", terms=["Benedict", "a traitor"])
    sim_result = belief_system.simulate([initial_statement])

    # Assert the Statement was inferred
    assert (
        Statement(verb="is", terms=["Benedict", "exiled"]) in sim_result.derived_facts
    )
    # Assert the Effect modified the world_state
    assert belief_system.world_state.get("population") == 9


def test_effects_are_not_re_applied_across_simulations():
    """Tests that an effect is not re-triggered by old statements in a new simulation."""
    belief_system = BeliefSystem(rules=[], contradiction_engine=ContradictionEngine())
    rule = Rule(
        condition=Condition(verb="is", terms=["?x", "dead"]),
        consequences=[
            Effect(
                target="world_state",
                attribute="population",
                operation="decrement",
                value=1,
            )
        ],
    )
    belief_system.rules.append(rule)
    belief_system.world_state["population"] = 10

    # First simulation, which should trigger the effect
    first_statement = Statement(verb="is", terms=["jon", "dead"])
    belief_system.simulate([first_statement])
    assert belief_system.world_state.get("population") == 9

    # Second, unrelated simulation
    second_statement = Statement(verb="is", terms=["sky", "blue"])
    belief_system.simulate([second_statement])
    assert belief_system.world_state.get("population") == 9, (
        "Effect was re-applied incorrectly!"
    )


def test_rule_matches_based_on_statement_structure():
    statement = Statement(verb="gives", terms=["Alice", "the book", "to", "Bob"])
    condition = Condition(verb="gives", terms=["?x", "?y", "to", "?z"])
    rule = Rule(condition=condition, consequences=[])
    bindings = rule.applies_to([statement])
    assert bindings == {"?x": "Alice", "?y": "the book", "?z": "Bob"}


def test_rule_matches_with_wildcard_term():
    statement = Statement(
        verb="says", terms=["Alice", "hello", "world", "and", "goodbye"]
    )
    # The condition looks for a speaker and captures the rest of the terms as their speech.
    condition = Condition(verb="says", terms=["?speaker", "*speech"])
    rule = Rule(condition=condition, consequences=[])
    bindings = rule.applies_to([statement])
    assert bindings == {
        "?speaker": "Alice",
        "?speech": ["hello", "world", "and", "goodbye"],
    }


def test_engine_detects_conflict_with_context():
    """Tests that the engine can detect a conflict between two rules when a third rule provides the logical link."""
    engine = ContradictionEngine()

    # Rule 1: A penguin is a bird.
    rule_implication = Rule(
        condition=Condition(verb="is", terms=["?x", "a penguin"]),
        consequences=[Statement(verb="is", terms=["?x", "a bird"])],
    )

    # Rule 2: A bird can fly.
    rule_general = Rule(
        condition=Condition(verb="is", terms=["?y", "a bird"]),
        consequences=[Statement(verb="can", terms=["?y", "fly"])],
    )

    # Rule 3: A penguin cannot fly.
    rule_specific = Rule(
        condition=Condition(verb="is", terms=["?z", "a penguin"]),
        consequences=[Statement(verb="can", terms=["?z", "fly"], negated=True)],
    )

    # The engine should detect that for a penguin, rule_general and rule_specific will have contradictory consequences.
    assert (
        engine.detect_rule_conflict(
            rule_general, rule_specific, context_rules=[rule_implication]
        )
        is True
    )


def test_inference_chain_is_pure():
    """Tests that the new _run_inference_chain function is pure and correct."""
    rule1 = Rule(
        condition=Condition(verb="is", terms=["?x", "a man"]),
        consequences=[Statement(verb="is", terms=["?x", "mortal"])],
    )
    rule2 = Rule(
        condition=Condition(verb="is", terms=["?x", "mortal"]),
        consequences=[Statement(verb="needs", terms=["?x", "to eat"])],
    )
    initial_statements = {Statement(verb="is", terms=["Socrates", "a man"])}
    rules = [rule1, rule2]

    derived_facts, applications = BeliefSystem._run_inference_chain(
        initial_statements, rules
    )

    expected_facts = {
        Statement(verb="is", terms=["Socrates", "mortal"]),
        Statement(verb="needs", terms=["Socrates", "to eat"]),
    }

    assert set(derived_facts) == expected_facts
    assert len(applications) == 2


def test_belief_system_detects_and_records_latent_conflict_on_rule_add():
    # Initialize BeliefSystem
    # Define rules that will create a latent conflict
    # Rule 1: If ?x is a bird, then ?x can fly
    rule1 = Rule(
        condition=Condition(verb="is", terms=["?x", "a", "bird"]),
        consequences=[Statement(verb="can", terms=["?x", "fly"])],
    )

    # Rule 2: If ?x is a penguin, then ?x cannot fly
    rule2 = Rule(
        condition=Condition(verb="is", terms=["?x", "a", "penguin"]),
        consequences=[Statement(verb="can", terms=["?x", "fly"], negated=True)],
    )

    # Context Rule: If ?x is a penguin, then ?x is a bird
    # This rule creates the latent conflict when added
    context_rule = Rule(
        condition=Condition(verb="is", terms=["?x", "a", "penguin"]),
        consequences=[Statement(verb="is", terms=["?x", "a", "bird"])],
    )

    bs = BeliefSystem(
        rules=[rule1, rule2, context_rule], contradiction_engine=ContradictionEngine()
    )

    # Assert that a latent contradiction record was created
    # We expect one record for the conflict between rule1 and rule2, linked by context_rule
    assert len(bs._latent_contradictions) == 1
    record = bs._latent_contradictions[0]
    assert isinstance(record, ContradictionRecord)
    assert record.rule_a == rule1
    assert record.rule_b == rule2
    assert record.statement1 is None  # No statement-level contradiction here
    assert record.statement2 is None  # No statement-level contradiction here
    assert "latent conflict" in record.resolution.lower()
    assert record.type == "rule_latent"  # Assert the type

def test_statement_to_dict_json():
    """
    Tests that Statement.to_dict_json() returns a correct JSON string representation.
    """
    s = Statement(verb="is", terms=["Socrates", "a man"], negated=False, priority=1.0)
    expected_dict = {
        "verb": "is",
        "terms": ["Socrates", "a man"],
        "negated": False,
        "priority": 1.0,
    }
    assert s.to_dict_json() == json.dumps(expected_dict)

    s_negated = Statement(verb="is", terms=["sky", "blue"], negated=True, priority=0.5)
    expected_dict_negated = {
        "verb": "is",
        "terms": ["sky", "blue"],
        "negated": True,
        "priority": 0.5,
    }
    assert s_negated.to_dict_json() == json.dumps(expected_dict_negated)

def test_condition_to_dict_json():
    """
    Tests that Condition.to_dict_json() returns a correct JSON string representation.
    """
    # Test with a simple condition
    c_simple = Condition(verb="is", terms=["Socrates", "a man"])
    expected_dict_simple = {
        "verb": "is",
        "terms": ["Socrates", "a man"],
        "verb_synonyms": [],
    }
    assert c_simple.to_dict_json() == json.dumps(expected_dict_simple)

    # Test with a conjunctive condition
    sub_c1 = Condition(verb="is", terms=["?x", "a king"])
    sub_c2 = Condition(verb="is", terms=["?x", "wise"])
    c_conjunctive = Condition(and_conditions=[sub_c1, sub_c2])
    expected_dict_conjunctive = {
        "and_conditions": [
            {"verb": "is", "terms": ["?x", "a king"], "verb_synonyms": []},
            {"verb": "is", "terms": ["?x", "wise"], "verb_synonyms": []},
        ]
    }
    assert c_conjunctive.to_dict_json() == json.dumps(expected_dict_conjunctive)
