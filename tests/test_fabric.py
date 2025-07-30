from logic_fabricator.fabric import Statement, Rule, Condition


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
        condition=Condition(verb="is", terms=[])
    )  # Use Condition object with empty terms

    assert rule.applies_to(statement) is not None


def test_rule_applies_with_variable_binding():
    # This test proposes that Rule.applies_to should return bindings
    # when a variable in the condition matches a term in the statement.
    statement = Statement(verb="is", terms=["Socrates", "a man"])
    condition = Condition(verb="is", terms=["?x", "a man"])
    rule = Rule(condition=condition)

    bindings = rule.applies_to(statement)
    assert bindings == {"?x": "Socrates"}

    # Test a non-matching case
    statement_no_match = Statement(verb="is", terms=["Plato", "a philosopher"])
    bindings_no_match = rule.applies_to(statement_no_match)
    assert bindings_no_match is None


def test_rule_applies_with_fewer_condition_terms():
    # This test challenges the strict term count matching.
    # A rule with fewer terms should still match if its terms are present
    # at the beginning of the statement's terms.
    statement = Statement(verb="is", terms=["Socrates", "a man", "wise"])
    condition = Condition(verb="is", terms=["?x", "a man"])
    rule = Rule(condition=condition)

    bindings = rule.applies_to(statement)
    assert bindings == {"?x": "Socrates"}

