import os
import pytest
from neo4j import GraphDatabase

from logic_fabricator.fabric import (
    BeliefSystem,
    ContradictionEngine,
    Rule,
    Condition,
    Statement,
)

# Neo4j connection details from environment variables set in docker-compose.yml
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

@pytest.fixture(scope="module")
def driver():
    """Provides a Neo4j driver instance for the test module."""
    if not NEO4J_URI or not NEO4J_USER or not NEO4J_PASSWORD:
        pytest.skip("NEO4J_URI, NEO4J_USER and NEO4J_PASSWORD must be set for persistence tests")
    db_driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    yield db_driver
    db_driver.close()

@pytest.fixture(autouse=True)
def cleanup_db(driver):
    """Cleans the database before each test."""
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")

@pytest.fixture(scope="function")
def mcp_fixture():
    """Provides an MCP instance and ensures its driver is closed."""
    from logic_fabricator.mcp import MCP
    mcp = MCP()
    yield mcp
    mcp.close()

@pytest.mark.db
def test_simulation_is_persisted_in_mcp_graph(driver, mcp_fixture):
    """
    This test asserts that a simulation record is persisted as a node
    in the Neo4j graph database after a simulation is run, orchestrated by the MCP.
    """
    # ARRANGE
    from logic_fabricator.fabric import ForkingStrategy

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
    simulation_id = mcp.simulate(belief_system_id, [initial_statement])

    # ASSERT
    # Retrieve the simulation node directly from Neo4j using the driver fixture
    with driver.session() as session:
        result = session.run(
            "MATCH (s:Simulation {id: $id}) RETURN s", id=str(simulation_id)
        ).single()
        
        assert result is not None
        node = result["s"]
        assert node["id"] == str(simulation_id)

        import json
        initial_statements_db = json.loads(node["initial_statements"])
        derived_facts_db = json.loads(node["derived_facts"])
        assert len(initial_statements_db) == 1
        assert initial_statements_db[0]["verb"] == "is"
        assert len(derived_facts_db) == 1
        assert derived_facts_db[0]["terms"] == ["Socrates", "mortal"]

    # CLEANUP: Delete the node to ensure test idempotency
    with driver.session() as session:
        session.run("MATCH (s:Simulation {id: $id}) DETACH DELETE s", id=str(simulation_id))

@pytest.mark.db
def test_mcp_get_simulation_history_returns_records(driver, mcp_fixture):
    from logic_fabricator.fabric import ForkingStrategy, Rule, Condition, Statement, SimulationRecord
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