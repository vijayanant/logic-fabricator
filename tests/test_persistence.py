
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
    with GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD)) as db_driver:
        yield db_driver

@pytest.fixture(autouse=True)
def cleanup_db(driver):
    """Cleans the database before each test."""
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")

@pytest.mark.db
def test_persist_saves_belief_system_to_neo4j(driver):
    """Tests that a BeliefSystem can be persisted to Neo4j."""
    # Arrange
    rule = Rule(
        condition=Condition(verb="is", terms=["?x", "a man"]),
        consequences=[Statement(verb="is", terms=["?x", "mortal"])],
    )
    belief_system = BeliefSystem(rules=[rule], contradiction_engine=ContradictionEngine())
    belief_system_id = belief_system.id

    # Act
    belief_system.persist(driver)

    # Assert
    with driver.session() as session:
        result = session.run("MATCH (bs:BeliefSystem {id: $id}) RETURN bs", id=belief_system_id)
        record = result.single()
        assert record is not None
        node = record["bs"]
        assert node["id"] == belief_system_id
        
        # Verify the rules by loading the JSON string
        import json
        rules_from_db = json.loads(node["rules"])
        assert isinstance(rules_from_db, list)
        assert len(rules_from_db) == 1
        assert rules_from_db[0]["condition"]["verb"] == "is"
