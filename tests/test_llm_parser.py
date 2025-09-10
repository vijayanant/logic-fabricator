import pytest
from logic_fabricator.llm_parser import LLMParser
from logic_fabricator.ir.ir_types import IRRule, IRCondition, IRStatement, IREffect


@pytest.mark.llm
def test_parses_simple_rule_to_ir():
    """Tests that the LLMParser can convert a simple natural language rule into its Intermediate Representation (IR) object."""
    natural_language_rule = "if ?x is a man, then ?x is mortal"

    expected_ir_condition = IRCondition(operator='LEAF', subject="?x", verb="is", object="man")
    expected_ir_consequence = IRStatement(subject="?x", verb="is", object="mortal", negated=False, modifiers=[])
    expected_ir_rule = IRRule(
        rule_type="standard",
        condition=expected_ir_condition,
        consequence=expected_ir_consequence,
    )

    parser = LLMParser()
    parsed_ir_rule = parser.parse_natural_language(natural_language_rule)
    assert parsed_ir_rule == expected_ir_rule


@pytest.mark.llm
def test_parse_simple_trust_rule_to_ir():
    """Tests that the LLMParser can parse a simple trust rule into its Intermediate Representation (IR) object."""
    natural_language_rule = "If Alice trusts Bob, then Bob is trustworthy."

    expected_ir_condition = IRCondition(
        operator='LEAF',
        subject="Alice",
        verb="trusts",
        object="Bob",
    )
    expected_ir_consequence = IRStatement(
        subject="Bob", verb="is", object="trustworthy"
    )
    expected_ir_rule = IRRule(
        rule_type="standard",
        condition=expected_ir_condition,
        consequence=expected_ir_consequence,
    )

    parser = LLMParser()
    parsed_ir_rule = parser.parse_natural_language(natural_language_rule)
    assert parsed_ir_rule == expected_ir_rule


@pytest.mark.llm
def test_parse_effect_rule_to_ir():
    """Tests that the LLMParser can parse an effect rule into its Intermediate Representation (IR) object."""
    natural_language_rule = "If ?x is mortal, then increment population by 1"

    expected_ir_condition = IRCondition(
        operator='LEAF',
        subject="?x",
        verb="is",
        object="mortal",
    )
    expected_ir_consequence = IREffect(
        target_world_state_key="population",
        effect_operation="increment",
        effect_value=1,
    )
    expected_ir_rule = IRRule(
        rule_type="effect",
        condition=expected_ir_condition,
        consequence=expected_ir_consequence,
    )

    parser = LLMParser()
    parsed_ir_rule = parser.parse_natural_language(natural_language_rule)
    assert parsed_ir_rule == expected_ir_rule


@pytest.mark.llm
def test_parse_simple_statement_to_ir():
    """Tests that the LLMParser can parse a simple statement into its Intermediate Representation (IR) object."""
    natural_language_input = "Alice trusts Bob."

    expected_ir_statement = IRStatement(
        subject="Alice", verb="trusts", object="Bob"
    )

    parser = LLMParser()
    parsed_ir_object = parser.parse_natural_language(natural_language_input)
    assert parsed_ir_object == expected_ir_statement


@pytest.mark.llm
@pytest.mark.xfail(
    reason="LLM output for wildcard parsing is inconsistent/limited for this model."
)
def test_parse_statement_with_wildcard_to_ir():
    """Tests that the LLMParser can parse a natural language statement with a wildcard into its IR object."""
    natural_language_input = 'ravi says "hello world, how are you"'

    expected_ir_statement = IRStatement(
        subject="Ravi",
        verb="say",
        object=["hello world", "how are you"],  # Wildcard terms should be a list
    )

    parser = LLMParser()
    parsed_ir_object = parser.parse_natural_language(natural_language_input)
    assert parsed_ir_object == expected_ir_statement


@pytest.mark.llm
def test_llm_parser_handles_disjunctive_rule():
    """
    Tests that the LLMParser can parse a rule with a disjunctive ('OR')
    condition into the new, recursive IR structure.
    """
    natural_language_rule = "If ?x is a king and (?x is wise or ?x is brave), then ?x is a good_ruler."

    expected_ir_rule = IRRule(
        rule_type="standard",
        condition=IRCondition(
            operator='AND',
            children=[
                IRCondition(
                    operator='LEAF',
                    subject="?x",
                    verb="is",
                    object="king"
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
        consequence=IRStatement(subject="?x", verb="is", object="good_ruler")
    )

    parser = LLMParser()
    parsed_ir_rule = parser.parse_natural_language(natural_language_rule)
    assert parsed_ir_rule == expected_ir_rule


@pytest.mark.llm
def test_llm_parser_handles_universal_quantifier():
    """
    Tests that the LLMParser can parse a rule with a universal quantifier ('all')
    into the IR structure.
    """
    natural_language_rule = "If all men are wise, then they are good."

    expected_ir_rule = IRRule(
        rule_type="standard",
        condition=IRCondition(
            operator='LEAF',
            subject="men",
            verb="are",
            object="wise",
            quantifier="ALL" # New field for quantifier
        ),
        consequence=IRStatement(
            subject="they",
            verb="are",
            object="good"
        )
    )

    parser = LLMParser()
    parsed_ir_rule = parser.parse_natural_language(natural_language_rule)

    assert parsed_ir_rule == expected_ir_rule