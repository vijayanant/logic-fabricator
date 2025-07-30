
from logic_fabricator.fabric import Statement

def test_statement_has_structure():
    # This test proposes the initial structure of our Statement object.
    s = Statement(verb="is", terms=["Socrates", "a man"])
    assert s.verb == "is"
    assert s.terms == ["Socrates", "a man"]
