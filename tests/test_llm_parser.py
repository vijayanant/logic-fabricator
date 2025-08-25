from logic_fabricator.fabric import Rule, Condition, Statement
from logic_fabricator.llm_parser import LLMParser

def test_parses_simple_rule_to_statement():
    """Tests that the LLMParser can convert a simple natural language rule into a structured Rule object."""
    
    # The natural language rule we want to parse
    natural_language_rule = "if ?x is a man, then ?x is mortal"
    
    # The structured object we expect the parser to produce
    expected_condition = Condition(verb="is", terms=["?x", "a_man"])
    expected_consequence = Statement(verb="is", terms=["?x", "mortal"])
    expected_rule = Rule(condition=expected_condition, consequences=[expected_consequence])
    
    # The (not-yet-existent) parser
    parser = LLMParser()
    
    # The call that will fail
    parsed_rule = parser.parse_rule(natural_language_rule)
    
    # The assertion that proves our success
    assert parsed_rule == expected_rule
