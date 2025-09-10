from logic_fabricator.ir_translator import IRTranslator
from logic_fabricator.ir.ir_types import IRStatement, IRCondition, IREffect, IRRule
from logic_fabricator.fabric import Statement, Condition, Effect, Rule
from logic_fabricator.exceptions import UnsupportedIRFeatureError
import pytest

def test_translate_simple_ir_statement():
    """Tests that IRTranslator can translate a simple IRStatement to a fabric.Statement."""
    ir_statement = IRStatement(
        subject="Alice",
        verb="trusts",
        object="Bob",
        negated=False,
        modifiers=[]
    )
    expected_statement = Statement(
        verb="trusts",
        terms=["Alice", "Bob"],
        negated=False,
        priority=1.0
    )

    translator = IRTranslator()
    translated_statement = translator.translate_ir_statement(ir_statement)

    assert translated_statement == expected_statement

def test_translate_ir_effect():
    """Tests that IRTranslator can translate an IREffect to a fabric.Effect."""
    ir_effect = IREffect(
        target_world_state_key="population",
        effect_operation="increment",
        effect_value=1
    )
    expected_effect = Effect(
        target="world_state",
        attribute="population",
        operation="increment",
        value=1
    )

    translator = IRTranslator()
    translated_effect = translator.translate_ir_effect(ir_effect)

    assert translated_effect == expected_effect

def test_translate_ir_rule():
    """Tests that IRTranslator can translate a simple IRRule to a fabric.Rule."""
    ir_rule = IRRule(
        rule_type="standard",
        condition=IRCondition(operator='LEAF', subject="?x", verb="is", object="a_man"),
        consequence=IRStatement(subject="?x", verb="is", object="mortal")
    )
    expected_rule = Rule(
        condition=Condition(verb="is", terms=["?x", "a_man"]),
        consequences=[Statement(verb="is", terms=["?x", "mortal"])]
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
            operator='AND',
            children=[
                IRCondition(
                    operator='LEAF', 
                    subject="?x", verb="is", object="a_king"
                ),
                IRCondition(
                    operator='OR',
                    children=[
                        IRCondition(operator='LEAF', subject="?x", verb="is", object="wise"),
                        IRCondition(operator='LEAF', subject="?x", verb="is", object="brave"),
                    ]
                )
            ]
        ),
        consequence=IRStatement(subject="?x", verb="is", object="a_good_ruler")
    )

    expected_rule1 = Rule(
        condition=Condition(
            and_conditions=[
                Condition(verb="is", terms=["?x", "a_king"]),
                Condition(verb="is", terms=["?x", "wise"]),
            ]
        ),
        consequences=[Statement(verb="is", terms=["?x", "a_good_ruler"])]
    )
    expected_rule2 = Rule(
        condition=Condition(
            and_conditions=[
                Condition(verb="is", terms=["?x", "a_king"]),
                Condition(verb="is", terms=["?x", "brave"]),
            ]
        ),
        consequences=[Statement(verb="is", terms=["?x", "a_good_ruler"])]
    )

    translator = IRTranslator()

    translated_rules = translator.translate_ir_rule(ir_rule)
    
    assert len(translated_rules) == 2
    assert expected_rule1 in translated_rules
    assert expected_rule2 in translated_rules