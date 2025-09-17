from logic_fabricator.ir_translator import IRTranslator
from logic_fabricator.ir.ir_types import IRStatement, IRCondition, IREffect, IRRule
from logic_fabricator.fabric import Statement, Condition, Effect, Rule
from logic_fabricator.exceptions import UnsupportedIRFeatureError
import pytest


def test_translate_simple_ir_statement():
    """Tests that IRTranslator can translate a simple IRStatement to a fabric.Statement."""
    ir_statement = IRStatement(
        subject="Alice", verb="trusts", object="Bob", negated=False, modifiers=[]
    )
    expected_statement = Statement(
        verb="trusts", terms=["Alice", "Bob"], negated=False, priority=1.0
    )

    translator = IRTranslator()
    translated_statement = translator.translate_ir_statement(ir_statement)

    assert translated_statement == expected_statement


def test_translate_ir_effect():
    """Tests that IRTranslator can translate an IREffect to a fabric.Effect."""
    ir_effect = IREffect(
        target_world_state_key="population",
        effect_operation="increment",
        effect_value=1,
    )
    expected_effect = Effect(
        target="world_state", attribute="population", operation="increment", value=1
    )

    translator = IRTranslator()
    translated_effect = translator.translate_ir_effect(ir_effect)

    assert translated_effect == expected_effect


def test_translate_ir_rule():
    """Tests that IRTranslator can translate a simple IRRule to a fabric.Rule."""
    ir_rule = IRRule(
        rule_type="standard",
        condition=IRCondition(type="LEAF", subject="?x", verb="is", object="a_man"),
        consequence=IRStatement(subject="?x", verb="is", object="mortal"),
    )
    expected_rule = Rule(
        condition=Condition(type="LEAF", verb="is", terms=["?x", "a_man"]),
        consequences=[Statement(verb="is", terms=["?x", "mortal"])],
    )

    translator = IRTranslator()
    translated_rule = translator.translate_ir_rule(ir_rule)

    assert translated_rule == [expected_rule]


def test_translate_ir_rule_with_disjunctive_condition():
    """
    Tests that the IRTranslator can decompose a complex IRCondition with
    disjunctive ('OR') logic into multiple fabric.Rule objects.
    """
    ir_rule = IRRule(
        rule_type="standard",
        condition=IRCondition(
            type="AND",
            children=[
                IRCondition(type="LEAF", subject="?x", verb="is", object="a_king"),
                IRCondition(
                    type="OR",
                    children=[
                        IRCondition(
                            type="LEAF", subject="?x", verb="is", object="wise"
                        ),
                        IRCondition(
                            type="LEAF", subject="?x", verb="is", object="brave"
                        ),
                    ],
                ),
            ],
        ),
        consequence=IRStatement(subject="?x", verb="is", object="a_good_ruler"),
    )

    expected_rule1 = Rule(
        condition=Condition(
            type="AND",
            children=[
                Condition(type="LEAF", verb="is", terms=["?x", "a_king"]),
                Condition(type="LEAF", verb="is", terms=["?x", "wise"]),
            ],
        ),
        consequences=[Statement(verb="is", terms=["?x", "a_good_ruler"])],
    )
    expected_rule2 = Rule(
        condition=Condition(
            type="AND",
            children=[
                Condition(type="LEAF", verb="is", terms=["?x", "a_king"]),
                Condition(type="LEAF", verb="is", terms=["?x", "brave"]),
            ],
        ),
        consequences=[Statement(verb="is", terms=["?x", "a_good_ruler"])],
    )

    translator = IRTranslator()

    translated_rules = translator.translate_ir_rule(ir_rule)

    assert len(translated_rules) == 2
    assert expected_rule1 in translated_rules
    assert expected_rule2 in translated_rules


def test_ir_translator_translates_forall_condition():
    """Tests that IRTranslator can translate an IRCondition with FORALL quantifier."""
    ir_forall_condition = IRCondition(
        type="FORALL",
        children=[
            IRCondition(
                type="LEAF", subject="?x", verb="is", object="a raven"
            ),  # Domain
            IRCondition(
                type="LEAF", subject="?x", verb="is", object="black"
            ),  # Property
        ],
    )
    expected_condition = Condition(
        type="FORALL",
        children=[
            Condition(type="LEAF", verb="is", terms=["?x", "a", "raven"]),
            Condition(type="LEAF", verb="is", terms=["?x", "black"]),
        ],
    )

    translator = IRTranslator()
    translated_condition = translator.translate_ir_condition(ir_forall_condition)

    assert translated_condition == expected_condition


def test_ir_translator_translates_exists_condition():
    """Tests that IRTranslator can translate an IRCondition with EXISTS quantifier."""
    ir_exists_condition = IRCondition(
        type="EXISTS",
        children=[
            IRCondition(type="LEAF", subject="?x", verb="is", object="a traitor")
        ],
    )
    expected_condition = Condition(
        type="EXISTS",
        children=[Condition(type="LEAF", verb="is", terms=["?x", "a", "traitor"])],
    )

    translator = IRTranslator()
    translated_condition = translator.translate_ir_condition(ir_exists_condition)

    assert translated_condition == expected_condition


def test_ir_translator_translates_count_condition():
    """Tests that IRTranslator can translate an IRCondition with COUNT quantifier."""
    ir_count_condition = IRCondition(
        type="COUNT",
        children=[IRCondition(type="LEAF", subject="?x", verb="is", object="a knight")],
        operator=">",  # This is the comparison operator for the count
        value=2,  # This is the value to compare against
    )
    expected_condition = Condition(
        type="COUNT",
        children=[Condition(type="LEAF", verb="is", terms=["?x", "a", "knight"])],
        operator=">",
        value=2,
    )

    translator = IRTranslator()
    translated_condition = translator.translate_ir_condition(ir_count_condition)

    assert translated_condition == expected_condition


def test_ir_translator_translates_none_condition():
    """Tests that IRTranslator can translate an IRCondition with NONE quantifier."""
    ir_none_condition = IRCondition(
        type="NONE",
        children=[
            IRCondition(type="LEAF", subject="?x", verb="is", object="a monster")
        ],
    )
    expected_condition = Condition(
        type="NONE",
        children=[Condition(type="LEAF", verb="is", terms=["?x", "a", "monster"])],
    )

    translator = IRTranslator()
    translated_condition = translator.translate_ir_condition(ir_none_condition)

    assert translated_condition == expected_condition


def test_translate_ir_rule_with_quantified_condition():
    """Tests that IRTranslator can translate an IRRule with a quantified condition."""
    ir_rule = IRRule(
        rule_type="standard",
        condition=IRCondition(
            type="EXISTS",
            children=[
                IRCondition(type="LEAF", subject="?x", verb="is", object="a_traitor")
            ],
        ),
        consequence=IRStatement(subject="system", verb="triggers", object="alarm"),
    )
    expected_rule = Rule(
        condition=Condition(
            type="EXISTS",
            children=[Condition(type="LEAF", verb="is", terms=["?x", "a_traitor"])],
        ),
        consequences=[Statement(verb="triggers", terms=["system", "alarm"])],
    )

    translator = IRTranslator()
    translated_rules = translator.translate_ir_rule(ir_rule)

    assert translated_rules == [expected_rule]


def test_translate_rule_with_and_and_exists_condition():
    """Tests rule with a conjunctive condition including a quantifier."""
    ir_rule = IRRule(
        rule_type="standard",
        condition=IRCondition(
            type="AND",
            children=[
                IRCondition(type="LEAF", subject="?x", verb="is", object="a_king"),
                IRCondition(
                    type="EXISTS",
                    children=[
                        IRCondition(
                            type="LEAF", subject="?y", verb="is", object="a_dragon"
                        )
                    ],
                ),
            ],
        ),
        consequence=IRStatement(subject="?x", verb="is", object="in_danger"),
    )

    expected_rule = Rule(
        condition=Condition(
            type="AND",
            children=[
                Condition(type="LEAF", verb="is", terms=["?x", "a_king"]),
                Condition(
                    type="EXISTS",
                    children=[
                        Condition(type="LEAF", verb="is", terms=["?y", "a_dragon"])
                    ],
                ),
            ],
        ),
        consequences=[Statement(verb="is", terms=["?x", "in_danger"])],
    )

    translator = IRTranslator()
    translated_rules = translator.translate_ir_rule(ir_rule)

    assert translated_rules == [expected_rule]


def test_translate_rule_with_or_and_exists_condition():
    """Tests rule with a disjunctive condition including a quantifier."""
    ir_rule = IRRule(
        rule_type="standard",
        condition=IRCondition(
            type="OR",
            children=[
                IRCondition(type="LEAF", subject="?x", verb="is", object="a_hero"),
                IRCondition(
                    type="EXISTS",
                    children=[
                        IRCondition(
                            type="LEAF", subject="?y", verb="is", object="a_villain"
                        )
                    ],
                ),
            ],
        ),
        consequence=IRStatement(subject="story", verb="is", object="interesting"),
    )

    expected_rule1 = Rule(
        condition=Condition(type="LEAF", verb="is", terms=["?x", "a_hero"]),
        consequences=[Statement(verb="is", terms=["story", "interesting"])],
    )
    expected_rule2 = Rule(
        condition=Condition(
            type="EXISTS",
            children=[Condition(type="LEAF", verb="is", terms=["?y", "a_villain"])],
        ),
        consequences=[Statement(verb="is", terms=["story", "interesting"])],
    )

    translator = IRTranslator()
    translated_rules = translator.translate_ir_rule(ir_rule)

    assert len(translated_rules) == 2
    assert expected_rule1 in translated_rules
    assert expected_rule2 in translated_rules


def test_translate_rule_with_and_and_forall_condition():
    """Tests a conjunctive condition with a FORALL quantifier."""
    ir_rule = IRRule(
        rule_type="standard",
        condition=IRCondition(
            type="AND",
            children=[
                IRCondition(type="LEAF", subject="?x", verb="is", object="a_shepherd"),
                IRCondition(
                    type="FORALL",
                    children=[
                        IRCondition(
                            type="LEAF", subject="?y", verb="in", object="flock"
                        ),
                        IRCondition(
                            type="LEAF", subject="?y", verb="is", object="safe"
                        ),
                    ],
                ),
            ],
        ),
        consequence=IRStatement(subject="?x", verb="is", object="happy"),
    )
    expected_rule = Rule(
        condition=Condition(
            type="AND",
            children=[
                Condition(type="LEAF", verb="is", terms=["?x", "a_shepherd"]),
                Condition(
                    type="FORALL",
                    children=[
                        Condition(type="LEAF", verb="in", terms=["?y", "flock"]),
                        Condition(type="LEAF", verb="is", terms=["?y", "safe"]),
                    ],
                ),
            ],
        ),
        consequences=[Statement(verb="is", terms=["?x", "happy"])],
    )
    translator = IRTranslator()
    translated_rules = translator.translate_ir_rule(ir_rule)
    assert translated_rules == [expected_rule]


def test_translate_rule_with_or_and_forall_condition():
    """Tests a disjunctive condition with a FORALL quantifier."""
    ir_rule = IRRule(
        rule_type="standard",
        condition=IRCondition(
            type="OR",
            children=[
                IRCondition(type="LEAF", subject="?x", verb="is", object="a_general"),
                IRCondition(
                    type="FORALL",
                    children=[
                        IRCondition(
                            type="LEAF", subject="?y", verb="in", object="army"
                        ),
                        IRCondition(
                            type="LEAF", subject="?y", verb="is", object="loyal"
                        ),
                    ],
                ),
            ],
        ),
        consequence=IRStatement(subject="victory", verb="is", object="possible"),
    )
    expected_rule1 = Rule(
        condition=Condition(type="LEAF", verb="is", terms=["?x", "a_general"]),
        consequences=[Statement(verb="is", terms=["victory", "possible"])],
    )
    expected_rule2 = Rule(
        condition=Condition(
            type="FORALL",
            children=[
                Condition(type="LEAF", verb="in", terms=["?y", "army"]),
                Condition(type="LEAF", verb="is", terms=["?y", "loyal"]),
            ],
        ),
        consequences=[Statement(verb="is", terms=["victory", "possible"])],
    )
    translator = IRTranslator()
    translated_rules = translator.translate_ir_rule(ir_rule)
    assert len(translated_rules) == 2
    assert expected_rule1 in translated_rules
    assert expected_rule2 in translated_rules


def test_translate_rule_with_and_and_count_condition():
    """Tests a conjunctive condition with a COUNT quantifier."""
    ir_rule = IRRule(
        rule_type="standard",
        condition=IRCondition(
            type="AND",
            children=[
                IRCondition(type="LEAF", subject="?x", verb="is", object="a_captain"),
                IRCondition(
                    type="COUNT",
                    children=[
                        IRCondition(type="LEAF", subject="?y", verb="in", object="crew")
                    ],
                    operator=">",
                    value=10,
                ),
            ],
        ),
        consequence=IRStatement(subject="?x", verb="has", object="a_large_crew"),
    )
    expected_rule = Rule(
        condition=Condition(
            type="AND",
            children=[
                Condition(type="LEAF", verb="is", terms=["?x", "a_captain"]),
                Condition(
                    type="COUNT",
                    children=[Condition(type="LEAF", verb="in", terms=["?y", "crew"])],
                    operator=">",
                    value=10,
                ),
            ],
        ),
        consequences=[Statement(verb="has", terms=["?x", "a_large_crew"])],
    )
    translator = IRTranslator()
    translated_rules = translator.translate_ir_rule(ir_rule)
    assert translated_rules == [expected_rule]


def test_translate_rule_with_or_and_none_condition():
    """Tests a disjunctive condition with a NONE quantifier."""
    ir_rule = IRRule(
        rule_type="standard",
        condition=IRCondition(
            type="OR",
            children=[
                IRCondition(type="LEAF", subject="?x", verb="is", object="a_paladin"),
                IRCondition(
                    type="NONE",
                    children=[
                        IRCondition(
                            type="LEAF", subject="?y", verb="is", object="undead"
                        )
                    ],
                ),
            ],
        ),
        consequence=IRStatement(subject="the_land", verb="is", object="blessed"),
    )
    expected_rule1 = Rule(
        condition=Condition(type="LEAF", verb="is", terms=["?x", "a_paladin"]),
        consequences=[Statement(verb="is", terms=["the_land", "blessed"])],
    )
    expected_rule2 = Rule(
        condition=Condition(
            type="NONE",
            children=[Condition(type="LEAF", verb="is", terms=["?y", "undead"])],
        ),
        consequences=[Statement(verb="is", terms=["the_land", "blessed"])],
    )

    translator = IRTranslator()
    translated_rules = translator.translate_ir_rule(ir_rule)
    assert len(translated_rules) == 2
    assert expected_rule1 in translated_rules
    assert expected_rule2 in translated_rules


def test_translate_rule_with_nested_quantifiers():
    """Tests a rule with a nested quantifier (FORALL contains EXISTS)."""
    ir_rule = IRRule(
        rule_type="standard",
        condition=IRCondition(
            type="FORALL",
            children=[
                IRCondition(
                    type="LEAF", subject="?x", verb="is", object="a_village"
                ),  # Domain
                IRCondition(
                    type="EXISTS",
                    children=[
                        IRCondition(
                            type="LEAF", subject="?y", verb="is_a_well_in", object="?x"
                        )
                    ],
                ),  # Property
            ],
        ),
        consequence=IRStatement(subject="all_villages", verb="have", object="water"),
    )
    expected_rule = Rule(
        condition=Condition(
            type="FORALL",
            children=[
                Condition(type="LEAF", verb="is", terms=["?x", "a_village"]),
                Condition(
                    type="EXISTS",
                    children=[
                        Condition(type="LEAF", verb="is_a_well_in", terms=["?y", "?x"])
                    ],
                ),
            ],
        ),
        consequences=[Statement(verb="have", terms=["all_villages", "water"])],
    )
    translator = IRTranslator()
    translated_rules = translator.translate_ir_rule(ir_rule)
    assert translated_rules == [expected_rule]
