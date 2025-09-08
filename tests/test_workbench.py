import io
import pytest
from contextlib import redirect_stdout

from logic_fabricator.ir.ir_types import IRStatement
from logic_fabricator.workbench import (
    handle_reset_command,
    handle_sim_command,
    handle_history_command,
    _belief_system # Import _belief_system directly
)


@pytest.fixture(autouse=True)
def mock_load_config(monkeypatch):
    """Mocks the load_config function to avoid dependency on environment variables."""
    from logic_fabricator.config import Config
    def mock_config():
        return Config(
            llm_provider="mock",
            llm_model="mock",
            llm_api_key="mock",
            llm_base_url=None,
        )
    monkeypatch.setattr("logic_fabricator.llm_parser.load_config", mock_config)


@pytest.fixture
def mock_llm_parser(monkeypatch):
    """Mocks the LLMParser to avoid real API calls."""

    def mock_parse(self, text):
        if "socrates is a man" in text:
            # Return a predictable IR object for the test simulation
            return IRStatement(subject="Socrates", verb="is", object="a_man")
        return None

    monkeypatch.setattr(
        "logic_fabricator.llm_parser.LLMParser.parse_natural_language", mock_parse
    )


@pytest.mark.db
def test_history_command_prints_mcp_records(mock_llm_parser):
    """
    Tests that the 'history' command function prints MCP records from the belief system.
    """
    # Initialize the global belief system used by the handlers
    handle_reset_command()
    from logic_fabricator.workbench import _belief_system # Re-import to get updated global

    # Add a rule to ensure derived facts
    from logic_fabricator.fabric import Rule, Condition, Statement
    _belief_system.rules.append(
        Rule(
            condition=Condition(verb="is", terms=["?x", "a_man"]),
            consequences=[Statement(verb="is", terms=["?x", "mortal"])],
        )
    )

    # Run a simulation to create a history record
    handle_sim_command("socrates is a man")

    output_capture = io.StringIO()
    with redirect_stdout(output_capture):
        handle_history_command()

    output = output_capture.getvalue()

    # Assert that the output contains the string representation of the SimulationRecord
    assert "--- History ---" in output
    assert "SimulationRecord" in output
    assert (
        "initial_statements=[Statement(is ['Socrates', 'a_man'], neg=False, prio=1.0)]"
        in output
    )
