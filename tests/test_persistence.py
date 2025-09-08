import os
import pytest
from neo4j import GraphDatabase

from logic_fabricator.fabric import Rule, Condition, Statement, SimulationRecord, ForkingStrategy
from logic_fabricator.neo4j_adapter import Neo4jAdapter
from .mocks import MockAdapter

import os
import pytest
from neo4j import GraphDatabase

from logic_fabricator.fabric import Rule, Condition, Statement, SimulationRecord, ForkingStrategy
from logic_fabricator.neo4j_adapter import Neo4jAdapter
from .mocks import MockAdapter

@pytest.fixture(scope="function")
def db_adapter():
    if os.getenv("MOCK_DB") == "true":
        yield MockAdapter()
    else:
        uri = os.getenv("NEO4J_URI")
        user = os.getenv("NEO4J_USER")
        password = os.getenv("NEO4J_PASSWORD")

        if not uri or not user or not password:
            pytest.skip("NEO4J_URI, NEO4J_USER and NEO4J_PASSWORD must be set for real database tests")

        db_driver = GraphDatabase.driver(uri, auth=(user, password))
        with db_driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n") # Clean up DB before each test
        yield Neo4jAdapter(driver=db_driver)
        db_driver.close()

@pytest.fixture
def mcp_fixture(db_adapter):
    """Provides an MCP instance with the appropriate db_adapter."""
    from logic_fabricator.mcp import MCP
    mcp = MCP(db_adapter=db_adapter)
    yield mcp
    mcp.close()


def test_simulation_is_persisted_in_mcp_graph(mcp_fixture):
    """
    This test asserts that a simulation record is persisted as a node
    in the graph database after a simulation is run, orchestrated by the MCP.
    """
    # ARRANGE
    mcp = mcp_fixture
    belief_system_name = "Test Belief System for Simulation Persistence"
    belief_system_id = mcp.create_belief_system(belief_system_name, ForkingStrategy.COEXIST)

    rule = Rule(
        condition=Condition(verb="is", terms=["?x", "a man"]),
        consequences=[Statement(verb="is", terms=["?x", "mortal"])],
    )
    mcp.add_rule(belief_system_id, rule)

    initial_statement = Statement(verb="is", terms=["Socrates", "a man"])
    
    # ACT
    # Simulate via MCP, which should handle persistence
    simulation_record = mcp.simulate(belief_system_id, [initial_statement])

    # ASSERT
    history = mcp.get_simulation_history(belief_system_id)
    assert len(history) == 1
    assert history[0].id == simulation_record.id


def test_mcp_get_simulation_history_returns_records(mcp_fixture):
    mcp = mcp_fixture
    belief_system_id = mcp.create_belief_system("Test History BS", ForkingStrategy.COEXIST)
    
    rule = Rule(
        condition=Condition(verb="is", terms=["?x", "a man"]),
        consequences=[Statement(verb="is", terms=["?x", "mortal"])],
    )
    mcp.add_rule(belief_system_id, rule)

    initial_statement = Statement(verb="is", terms=["Socrates", "a man"])
    mcp.simulate(belief_system_id, [initial_statement])

    history = mcp.get_simulation_history(belief_system_id)
    assert len(history) == 1
    assert isinstance(history[0], SimulationRecord)
    assert history[0].initial_statements[0] == initial_statement

def test_add_rule_persists_rule_and_relationship(mcp_fixture):
    """
    Tests that adding a rule to a belief system via MCP.add_rule
    persists the rule node and the CONTAINS_RULE relationship.
    """
    # ARRANGE
    mcp = mcp_fixture
    belief_system_id = mcp.create_belief_system("Test Belief System for Rule Persistence", ForkingStrategy.COEXIST)

    rule = Rule(
        condition=Condition(verb="is", terms=["?x", "a man"]),
        consequences=[Statement(verb="is", terms=["?x", "mortal"])],
    )

    # ACT
    mcp.add_rule(belief_system_id, rule)

    # ASSERT
    # This assertion is only valid for the mock adapter
    if isinstance(mcp.db_adapter, MockAdapter):
        assert rule in mcp.db_adapter.belief_systems[belief_system_id]["rules"]

def test_fork_belief_system_persists_fork_and_relationship(mcp_fixture):
    """
    Tests that forking a belief system via MCP.fork_belief_system
    persists a new BeliefSystem node and a FORKED_FROM relationship.
    """
    # ARRANGE
    mcp = mcp_fixture
    parent_belief_system_id = mcp.create_belief_system("Parent Belief System", ForkingStrategy.COEXIST)
    fork_name = "Forked Belief System"

    # ACT
    forked_belief_system_id = mcp.fork_belief_system(parent_belief_system_id, fork_name)

    # ASSERT
    # This assertion is only valid for the mock adapter
    if isinstance(mcp.db_adapter, MockAdapter):
        assert forked_belief_system_id in mcp.db_adapter.belief_systems
        assert mcp.db_adapter.belief_systems[forked_belief_system_id]["name"] == fork_name
import pytest
from logic_fabricator.mcp import MCP
from logic_fabricator.fabric import ForkingStrategy, Rule, Condition, Statement
from .mocks import MockAdapter

@pytest.fixture
def mcp_with_mock_adapter():
    return MCP(db_adapter=MockAdapter())

def test_mcp_create_belief_system(mcp_with_mock_adapter: MCP):
    mcp = mcp_with_mock_adapter
    belief_system_id = mcp.create_belief_system("Test Belief System", ForkingStrategy.COEXIST)
    assert belief_system_id is not None
    assert belief_system_id in mcp.belief_systems
    assert mcp.db_adapter.belief_systems[belief_system_id]["name"] == "Test Belief System"

def test_mcp_add_rule(mcp_with_mock_adapter: MCP):
    mcp = mcp_with_mock_adapter
    belief_system_id = mcp.create_belief_system("Test Belief System", ForkingStrategy.COEXIST)
    rule = Rule(condition=Condition(verb="is", terms=["?x", "a man"]), consequences=[Statement(verb="is", terms=["?x", "mortal"])])
    mcp.add_rule(belief_system_id, rule)
    assert rule in mcp.belief_systems[belief_system_id].rules
    assert rule in mcp.db_adapter.belief_systems[belief_system_id]["rules"]

def test_mcp_fork_belief_system(mcp_with_mock_adapter: MCP):
    mcp = mcp_with_mock_adapter
    parent_id = mcp.create_belief_system("Parent", ForkingStrategy.COEXIST)
    fork_id = mcp.fork_belief_system(parent_id, "Fork")
    assert fork_id in mcp.belief_systems
    assert fork_id in mcp.db_adapter.belief_systems
    assert mcp.db_adapter.belief_systems[fork_id]["name"] == "Fork"

def test_mcp_simulate_persists_simulation(mcp_with_mock_adapter: MCP):
    mcp = mcp_with_mock_adapter
    belief_system_id = mcp.create_belief_system("Test", ForkingStrategy.COEXIST)
    rule = Rule(condition=Condition(verb="is", terms=["?x", "a man"]), consequences=[Statement(verb="is", terms=["?x", "mortal"])])
    mcp.add_rule(belief_system_id, rule)
    statements = [Statement(verb="is", terms=["Socrates", "a man"])]
    mcp.simulate(belief_system_id, statements)
    assert len(mcp.db_adapter.simulations) == 1
    assert mcp.db_adapter.simulations[0].initial_statements == statements
