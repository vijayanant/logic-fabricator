import os
import structlog
import time
import uuid
import json
from neo4j import GraphDatabase
from .fabric import BeliefSystem, Rule, Statement, ContradictionEngine, ForkingStrategy, SimulationRecord


logger = structlog.get_logger(__name__)

class MCP:
    def __init__(self):
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "password")
        self._driver = GraphDatabase.driver(uri, auth=(user, password))
        self.belief_systems = {}
        self.contradiction_engine = ContradictionEngine()
        logger.info("MCP initialized and connected to Neo4j.", uri=uri)

    def close(self):
        self._driver.close()

    def create_belief_system(self, name: str, strategy: ForkingStrategy = ForkingStrategy.COEXIST) -> str:
        belief_system = BeliefSystem(
            rules=[],
            contradiction_engine=self.contradiction_engine,
            strategy=strategy
        )
        self.belief_systems[str(belief_system.id)] = belief_system
        
        with self._driver.session() as session:
            session.run(
                "CREATE (bs:BeliefSystem {id: $id, name: $name, strategy: $strategy, created_at: $created_at})",
                id=str(belief_system.id),
                name=name,
                strategy=strategy.value,
                created_at=time.time()
            )
        logger.info("BeliefSystem created and persisted.", id=belief_system.id, name=name)
        return str(belief_system.id)

    def add_rule(self, belief_system_id: str, rule: Rule):
        belief_system = self.belief_systems.get(belief_system_id)
        if not belief_system:
            logger.error("BeliefSystem not found.", id=belief_system_id)
            return

        belief_system.rules.append(rule)

        with self._driver.session() as session:
            session.run(
                "MATCH (bs:BeliefSystem {id: $bs_id}) CREATE (r:Rule {id: $rule_id, condition_json: $condition_json, consequences_json: $consequences_json}) CREATE (bs)-[:CONTAINS_RULE]->(r)",
                bs_id=belief_system_id,
                rule_id=str(uuid.uuid4()), # Rules need their own UUID
                condition_json=json.dumps(rule.condition.to_dict()),
                consequences_json=json.dumps([c.to_dict() for c in rule.consequences])
            )
        logger.info("Rule added and persisted.", rule=rule, belief_system_id=belief_system_id)

    def persist_simulation_record(self, record_id: str, properties: dict):
        with self._driver.session() as session:
            session.run("CREATE (s:Simulation {id: $id}) SET s += $props", id=record_id, props=properties)

    def simulate(self, belief_system_id: str, statements: list[Statement]) -> str:
        belief_system = self.belief_systems.get(belief_system_id)
        if not belief_system:
            logger.error("BeliefSystem not found.", id=belief_system_id)
            raise ValueError(f"BeliefSystem with ID {belief_system_id} not found.")

        simulation_result = belief_system.simulate(statements)

        simulation_id = str(uuid.uuid4())
        
        # Prepare properties for the Simulation node
        properties = {
            "id": simulation_id,
            "timestamp": time.time(),
            "initial_statements": json.dumps([s.to_dict() for s in statements]),
            "derived_facts": json.dumps([s.to_dict() for s in simulation_result.derived_facts]),
            "applied_rules": json.dumps([r.to_dict() for r in simulation_result.applied_rules]),
            "forked_belief_system_id": str(simulation_result.forked_belief_system.id) if simulation_result.forked_belief_system else None
        }

        with self._driver.session() as session:
            session.run(
                "CREATE (s:Simulation {id: $id}) SET s += $props",
                id=simulation_id,
                props=properties
            )
            # Create relationships
            session.run(
                "MATCH (bs:BeliefSystem {id: $bs_id}), (s:Simulation {id: $s_id}) CREATE (s)-[:USED]->(bs)",
                bs_id=belief_system_id,
                s_id=simulation_id
            )
            # TODO: Add relationships for INTRODUCED, DERIVED_FACT, APPLIED_RULE

        # Update the in-memory belief system with any changes (e.g., new statements, world state)
        # This is crucial because BeliefSystem.simulate modifies the belief_system object in place
        # and the MCP is managing this in-memory object.
        self.belief_systems[belief_system_id] = belief_system 

        logger.info("Simulation orchestrated and persisted.", simulation_id=simulation_id, belief_system_id=belief_system_id)
        return simulation_id
