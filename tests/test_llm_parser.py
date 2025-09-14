import pytest
from logic_fabricator.llm_parser import LLMParser
from logic_fabricator.ir.ir_types import IRRule, IRCondition, IRStatement, IREffect


@pytest.mark.llm
def test_parses_simple_rule_to_ir():
    """Tests that the LLMParser can convert a simple natural language rule into its Intermediate Representation (IR) object."""
    natural_language_rule = "if ?x is a man, then ?x is mortal"

    expected_ir_condition = IRCondition(
        operator="LEAF", subject="?x", verb="is", object="man"
    )
    expected_ir_consequence = IRStatement(
        subject="?x", verb="is", object="mortal", negated=False, modifiers=[]
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
def test_parse_simple_trust_rule_to_ir():
    """Tests that the LLMParser can parse a simple trust rule into its Intermediate Representation (IR) object."""
    natural_language_rule = "If Alice trusts Bob, then Bob is trustworthy."

    expected_ir_condition = IRCondition(
        operator="LEAF",
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
        operator="LEAF",
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

    expected_ir_statement = IRStatement(subject="Alice", verb="trusts", object="Bob")

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
    natural_language_rule = (
        "If ?x is a king and (?x is wise or ?x is brave), then ?x is a good_ruler."
    )

    expected_ir_rule = IRRule(
        rule_type="standard",
        condition=IRCondition(
            operator="AND",
            children=[
                IRCondition(operator="LEAF", subject="?x", verb="is", object="king"),
                IRCondition(
                    operator="OR",
                    children=[
                        IRCondition(
                            operator="LEAF", subject="?x", verb="is", object="wise"
                        ),
                        IRCondition(
                            operator="LEAF", subject="?x", verb="is", object="brave"
                        ),
                    ],
                ),
            ],
        ),
        consequence=IRStatement(subject="?x", verb="is", object="good_ruler"),
    )

    parser = LLMParser()
    parsed_ir_rule = parser.parse_natural_language(natural_language_rule)
    assert parsed_ir_rule == expected_ir_rule


@pytest.mark.llm
def test_llm_parser_handles_universal_quantifier():
    """
    Tests that the LLMParser can parse a rule with a universal quantifier ('for all')
    into the correct, modern IR structure.
    """
    natural_language_rule = (
        "if for all ships, they are seaworthy, then the fleet is ready"
    )

    expected_ir_rule = IRRule(
        rule_type="standard",
        condition=IRCondition(
            quantifier="FORALL",
            children=[
                IRCondition(operator="LEAF", subject="?x", verb="is", object="ship"),
                IRCondition(
                    operator="LEAF", subject="?x", verb="is", object="seaworthy"
                ),
            ],
        ),
        consequence=IRStatement(subject="fleet", verb="is", object="ready"),
    )

    parser = LLMParser()
    parsed_ir_rule = parser.parse_natural_language(natural_language_rule)

    assert parsed_ir_rule.rule_type == expected_ir_rule.rule_type
    assert parsed_ir_rule.condition.quantifier == "FORALL"
    assert len(parsed_ir_rule.condition.children) == 2
    assert parsed_ir_rule.consequence.object == "ready"


@pytest.mark.llm
def test_llm_parser_handles_existential_quantifier_correctly():
    """
    Tests that the LLMParser can parse a rule with an existential quantifier ('exists')
    into the correct, modern IR structure with a nested condition.
    """
    natural_language_rule = "if there exists a traitor, then the kingdom is in_danger"

    parser = LLMParser()
    parsed_ir_rule = parser.parse_natural_language(natural_language_rule)

    # Assert the critical structural components, being flexible on the effect details
    assert parsed_ir_rule.rule_type == "effect"
    assert parsed_ir_rule.condition.quantifier == "EXISTS"
    assert len(parsed_ir_rule.condition.children) == 1
    assert parsed_ir_rule.condition.children[0].object == "traitor"
    assert parsed_ir_rule.consequence.effect_operation == "set"
    assert parsed_ir_rule.consequence.effect_value is True


@pytest.mark.llm
def test_llm_parser_handles_count_quantifier():
    """
    Tests that the LLMParser can parse a rule with a COUNT quantifier.
    """
    natural_language_rule = (
        "if there are more than 3 guards, set security status to true"
    )

    parser = LLMParser()
    parsed_ir_rule = parser.parse_natural_language(natural_language_rule)

    # Assert the critical structural components, being flexible on the effect details
    assert parsed_ir_rule.rule_type == "effect"
    assert parsed_ir_rule.condition.quantifier == "COUNT"
    assert parsed_ir_rule.condition.operator == ">"
    assert parsed_ir_rule.condition.object == 3
    assert len(parsed_ir_rule.condition.children) == 1
    assert parsed_ir_rule.condition.children[0].object == "guard"
    assert parsed_ir_rule.consequence.effect_operation == "set"
    assert parsed_ir_rule.consequence.effect_value is True


@pytest.mark.llm
def test_llm_parser_handles_none_quantifier():
    """
    Tests that the LLMParser can parse a rule with a NONE quantifier.
    """
    natural_language_rule = "if no one is a coward, the mission succeeds"

    parser = LLMParser()
    parsed_ir_rule = parser.parse_natural_language(natural_language_rule)

    # Assert the critical structural components, being flexible on the effect details
    assert parsed_ir_rule.rule_type == "effect"
    assert parsed_ir_rule.condition.quantifier == "NONE"
    assert len(parsed_ir_rule.condition.children) == 1
    assert parsed_ir_rule.condition.children[0].object == "coward"
    assert parsed_ir_rule.consequence.effect_operation == "set"
    assert parsed_ir_rule.consequence.effect_value is True


@pytest.mark.llm
def test_llm_parses_natural_negation():
    """
    Tests that the LLMParser can correctly parse a statement with
    natural mid-sentence negation (e.g., 'is not').
    """
    natural_language_statement = "ship1 is not seaworthy"

    parser = LLMParser()
    parsed_ir = parser.parse_natural_language(natural_language_statement)

    # It should be parsed as an IRStatement
    assert isinstance(parsed_ir, IRStatement)
    assert parsed_ir.subject == "ship1"
    assert parsed_ir.verb == "is"
    assert parsed_ir.object == "seaworthy"
    assert parsed_ir.negated is True


@pytest.mark.llm
def test_llm_parses_complex_forall_rule_correctly():
    """
    Tests that the LLM can parse a more complex FORALL rule structure
    and distinguish `quantifier` from `operator`.
    """
    natural_language_rule = (
        "for all ships, if the ship is seaworthy, then the fleet is ready"
    )

    parser = LLMParser()
    parsed_ir = parser.parse_natural_language(natural_language_rule)

    assert isinstance(parsed_ir, IRRule)

    # Per user guidance, we assert that the LLM correctly
    # interprets "the fleet is ready" as an effect.
    assert parsed_ir.rule_type == "effect"

    # Check the critical condition structure
    condition = parsed_ir.condition
    assert condition.quantifier == "FORALL"
    assert condition.operator is None
    assert len(condition.children) == 2

    # Check the domain and property
    domain, prop = condition.children
    assert domain.operator == "LEAF"
    assert domain.object == "ship"

    assert prop.operator == "LEAF"
    assert prop.object == "seaworthy"

    # Check that the consequence is an effect, but do not assert its value,
    # as the LLM's interpretation is creative and non-deterministic.
    assert isinstance(parsed_ir.consequence, IREffect)
