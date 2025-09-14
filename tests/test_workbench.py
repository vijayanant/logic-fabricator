import io
import pytest
from contextlib import redirect_stdout

from logic_fabricator.ir.ir_types import IRStatement
from logic_fabricator.fabric import SimulationRecord, Statement, Rule, Condition


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
            llm_max_attempts=1,
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


@pytest.fixture
def mock_mcp(monkeypatch):
    """
    Mocks the MCP and its underlying Neo4j driver to prevent actual database connections.
    """
    class MockSession:
        def run(self, *args, **kwargs):
            return [] # Return empty list for queries

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    class MockDriver:
        def session(self):
            return MockSession()

        def close(self):
            pass

    class MockGraphDatabase:
        def driver(self, *args, **kwargs):
            return MockDriver()

    class MockMCP:
        def __init__(self, db_adapter=None):
            pass

        def create_belief_system(self, *args, **kwargs):
            return "mock_belief_system_id"

        def simulate(self, *args, **kwargs):
            pass

        def get_simulation_history(self, *args, **kwargs):
            # Create a mock SimulationRecord that matches the expected output
            mock_statement = Statement(verb="is", terms=["Socrates", "a_man"], negated=False, priority=1.0)
            mock_derived_fact = Statement(verb="is", terms=["Socrates", "mortal"], negated=False, priority=1.0)
            mock_rule = Rule(condition=Condition(verb="is", terms=["?x", "a_man"]), consequences=[Statement(verb="is", terms=["?x", "mortal"])])

            mock_record = SimulationRecord(
                belief_system_id="mock_belief_system_id",
                initial_statements=[mock_statement],
                derived_facts=[mock_derived_fact],
                applied_rules=[mock_rule],
                forked_belief_system=None,
            )
            return [mock_record]

        def close(self):
            pass

    monkeypatch.setattr("logic_fabricator.mcp.MCP", MockMCP)
    monkeypatch.setattr("neo4j.GraphDatabase", MockGraphDatabase) # Mock the entire GraphDatabase object


def test_history_command_prints_mcp_records(mock_llm_parser, mock_mcp):
    """
    Tests that the 'history' command function prints MCP records from the belief system.
    """
    # We need to import Workbench here because it's used in this test
    from logic_fabricator.workbench import Workbench

    with Workbench() as workbench:
        # Initialize the global belief system used by the handlers
        workbench.handle_reset_command()

        # Add a rule to ensure derived facts
        from logic_fabricator.fabric import Rule, Condition, Statement
        workbench.belief_system.rules.append(
            Rule(
                condition=Condition(verb="is", terms=["?x", "a_man"]),
                consequences=[Statement(verb="is", terms=["?x", "mortal"])],
            )
        )

        # Run a simulation to create a history record
        workbench.handle_sim_command("socrates is a man")

        output_capture = io.StringIO()
        with redirect_stdout(output_capture):
            workbench.handle_history_command()

        output = output_capture.getvalue()

        # Assert that the output contains the string representation of the SimulationRecord
        assert "--- History ---" in output
        assert "SimulationRecord" in output
        assert (
            "initial_statements=[Statement(is ['Socrates', 'a_man'], neg=False, prio=1.0)]"
            in output
        )
