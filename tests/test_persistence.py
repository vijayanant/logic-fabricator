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

@pytest.mark.db
def test_add_rule_persists_rule_and_relationship(driver, mcp_fixture):
    """
    Tests that adding a rule to a belief system via MCP.add_rule
    persists the rule node and the CONTAINS_RULE relationship in Neo4j.
    """
    # ARRANGE
    from logic_fabricator.fabric import ForkingStrategy, Rule, Condition, Statement
    mcp = mcp_fixture
    belief_system_id = mcp.create_belief_system("Test Belief System for Rule Persistence", ForkingStrategy.COEXIST)

    rule = Rule(
        condition=Condition(verb="is", terms=["?x", "a man"]),
        consequences=[Statement(verb="is", terms=["?x", "mortal"])],
    )

    # ACT
    mcp.add_rule(belief_system_id, rule)

    # ASSERT
    with driver.session() as session:
        # Check if the Rule node exists
        rule_node_result = session.run(
            "MATCH (r:Rule {condition_json: $condition_json, consequences_json: $consequences_json}) RETURN r",
            condition_json=rule.condition.to_dict_json(),
            consequences_json=rule.consequences_to_dict_json(),
        ).single()
        assert rule_node_result is not None, "Rule node was not found in Neo4j."
        rule_node = rule_node_result["r"]

        # Check if the CONTAINS_RULE relationship exists
        relationship_result = session.run(
            f"MATCH (bs:BeliefSystem {{id: $bs_id}})-[:{mcp.REL_CONTAINS_RULE}]->(r:Rule {{id: $rule_id}}) RETURN bs, r",
            bs_id=belief_system_id,
            rule_id=rule_node["id"], # Use the ID from the persisted node
        ).single()
        assert relationship_result is not None, "CONTAINS_RULE relationship was not found."
        assert relationship_result["bs"]["id"] == belief_system_id
        assert relationship_result["r"]["id"] == rule_node["id"]

@pytest.mark.db
def test_fork_belief_system_persists_fork_and_relationship(driver, mcp_fixture):
    """
    Tests that forking a belief system via MCP.fork_belief_system
    persists a new BeliefSystem node and a FORKED_FROM relationship in Neo4j.
    """
    # ARRANGE
    from logic_fabricator.fabric import ForkingStrategy
    mcp = mcp_fixture
    parent_belief_system_id = mcp.create_belief_system("Parent Belief System", ForkingStrategy.COEXIST)
    fork_name = "Forked Belief System"

    # ACT
    forked_belief_system_id = mcp.fork_belief_system(parent_belief_system_id, fork_name)

    # ASSERT
    with driver.session() as session:
        # Check if the forked BeliefSystem node exists
        forked_bs_result = session.run(
            "MATCH (bs:BeliefSystem {id: $id, name: $name}) RETURN bs",
            id=forked_belief_system_id,
            name=fork_name,
        ).single()
        assert forked_bs_result is not None, "Forked BeliefSystem node was not found in Neo4j."
        forked_bs_node = forked_bs_result["bs"]
        assert forked_bs_node["id"] == forked_belief_system_id
        assert forked_bs_node["name"] == fork_name

        # Check if the FORKED_FROM relationship exists
        relationship_result = session.run(
            f"MATCH (forked_bs:BeliefSystem {{id: $forked_id}})-[:FORKED_FROM]->(parent_bs:BeliefSystem {{id: $parent_id}}) RETURN forked_bs, parent_bs",
            forked_id=forked_belief_system_id,
            parent_id=parent_belief_system_id,
        ).single()
        assert relationship_result is not None, "FORKED_FROM relationship was not found."
        assert relationship_result["forked_bs"]["id"] == forked_belief_system_id
        assert relationship_result["parent_bs"]["id"] == parent_belief_system_id