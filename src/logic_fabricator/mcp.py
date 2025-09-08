import os
import structlog
import time
import uuid
import json
from neo4j import GraphDatabase
from .fabric import (
    BeliefSystem,
    Rule,
    Statement,
    ContradictionEngine,
    ForkingStrategy,
    SimulationRecord,
    Condition,
)


logger = structlog.get_logger(__name__)


class MCP:
    # Define Neo4j relationship types as constants
    REL_CONTAINS_RULE = "CONTAINS_RULE"
    REL_USED = "USED"
    REL_INTRODUCED = "INTRODUCED"
    REL_DERIVED_FACT = "DERIVED_FACT"
    REL_APPLIED_RULE = "APPLIED_RULE"

    def __init__(self, driver=None):
        if driver:
            self._driver = driver
        else:
            uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
            user = os.getenv("NEO4J_USER", "neo4j")
            password = os.getenv("NEO4J_PASSWORD", "password")
            self._driver = GraphDatabase.driver(uri, auth=(user, password))
        
        self.belief_systems = {}
        self.contradiction_engine = ContradictionEngine()
        logger.info("MCP initialized and connected to its database.")

    def close(self):
        self._driver.close()

    def create_belief_system(
        self, name: str, strategy: ForkingStrategy = ForkingStrategy.COEXIST
    ) -> str:
        belief_system = BeliefSystem(
            rules=[], contradiction_engine=self.contradiction_engine, strategy=strategy
        )
        self.belief_systems[str(belief_system.id)] = belief_system

        with self._driver.session() as session:
            session.run(
                "CREATE (bs:BeliefSystem {id: $id, name: $name, strategy: $strategy, created_at: $created_at})",
                id=str(belief_system.id),
                name=name,
                strategy=strategy.value,
                created_at=time.time(),
            )
        logger.info(
            "BeliefSystem created and persisted.", id=belief_system.id, name=name
        )
        return str(belief_system.id)

    def add_rule(self, belief_system_id: str, rule: Rule):
        belief_system = self.belief_systems.get(belief_system_id)
        if not belief_system:
            logger.error("BeliefSystem not found.", id=belief_system_id)
            raise ValueError(f"BeliefSystem with ID {belief_system_id} not found.")

        belief_system.rules.append(rule)

        with self._driver.session() as session:
            session.run(
                f"MATCH (bs:BeliefSystem {{id: $bs_id}}) CREATE (r:Rule {{id: $rule_id, condition_json: $condition_json, consequences_json: $consequences_json}}) CREATE (bs)-[:{self.REL_CONTAINS_RULE}]->(r)",
                bs_id=belief_system_id,
                rule_id=str(uuid.uuid4()),  # Rules need their own UUID
                condition_json=json.dumps(rule.condition.to_dict()),
                consequences_json=json.dumps([c.to_dict() for c in rule.consequences]),
            )
        logger.info(
            "Rule added and persisted.", rule=rule, belief_system_id=belief_system_id
        )

    def fork_belief_system(self, parent_id: str, name: str) -> str:
        parent_belief_system = self.belief_systems.get(parent_id)
        if not parent_belief_system:
            logger.error("Parent BeliefSystem not found.", id=parent_id)
            raise ValueError(f"Parent BeliefSystem with ID {parent_id} not found.")

        # Create a new BeliefSystem instance (in-memory clone)
        # We need to deep copy rules, statements, world_state, etc.
        # For simplicity, let's assume a shallow copy of rules for now,
        # and a new ID for the forked system.
        # A proper deep copy would involve cloning all mutable objects.
        forked_belief_system = BeliefSystem(
            rules=list(parent_belief_system.rules), # Shallow copy of rules
            contradiction_engine=parent_belief_system.contradiction_engine,
            strategy=parent_belief_system.strategy,
        )
        # Copy statements and world_state
        forked_belief_system.statements = set(parent_belief_system.statements)
        forked_belief_system.world_state = parent_belief_system.world_state.copy()
        forked_belief_system.effects_applied = set(parent_belief_system.effects_applied)


        self.belief_systems[str(forked_belief_system.id)] = forked_belief_system

        with self._driver.session() as session:
            # Create the new BeliefSystem node
            session.run(
                "CREATE (bs:BeliefSystem {id: $id, name: $name, strategy: $strategy, created_at: $created_at})",
                id=str(forked_belief_system.id),
                name=name,
                strategy=forked_belief_system.strategy.value,
                created_at=time.time(),
            )
            # Create the FORKED_FROM relationship
            session.run(
                f"MATCH (forked_bs:BeliefSystem {{id: $forked_id}}), (parent_bs:BeliefSystem {{id: $parent_id}}) CREATE (forked_bs)-[:FORKED_FROM]->(parent_bs)",
                forked_id=str(forked_belief_system.id),
                parent_id=parent_id,
            )
        logger.info(
            "BeliefSystem forked and persisted.",
            parent_id=parent_id,
            forked_id=forked_belief_system.id,
            name=name,
        )
        return str(forked_belief_system.id)

    

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
            "derived_facts": json.dumps(
                [s.to_dict() for s in simulation_result.derived_facts]
            ),
            "applied_rules": json.dumps(
                [r.to_dict() for r in simulation_result.applied_rules]
            ),
            "forked_belief_system_id": str(simulation_result.forked_belief_system.id)
            if simulation_result.forked_belief_system
            else None,
        }

        with self._driver.session() as session:
            session.run(
                "CREATE (s:Simulation {id: $id}) SET s += $props",
                id=simulation_id,
                props=properties,
            )
            # Create relationships
            session.run(
                f"MATCH (bs:BeliefSystem {{id: $bs_id}}), (s:Simulation {{id: $s_id}}) CREATE (s)-[:{self.REL_USED}]->(bs)",
                bs_id=belief_system_id,
                s_id=simulation_id,
            )
            # Create relationships for initial statements
            for stmt in statements:
                self._persist_statement(session, stmt, simulation_id, "INTRODUCED")

            # Create relationships for derived facts
            for stmt in simulation_result.derived_facts:
                self._persist_statement(session, stmt, simulation_id, "DERIVED_FACT")

            # Create relationships for applied rules
            for rule in simulation_result.applied_rules:
                self._persist_rule(session, rule, simulation_id, "APPLIED_RULE")

        # Update the in-memory belief system with any changes (e.g., new statements, world state)
        # This is crucial because BeliefSystem.simulate modifies the belief_system object in place
        # and the MCP is managing this in-memory object.
        self.belief_systems[belief_system_id] = belief_system

        logger.info(
            "Simulation orchestrated and persisted.",
            simulation_id=simulation_id,
            belief_system_id=belief_system_id,
        )
        return simulation_id

    def _persist_statement(
        self, session, statement: Statement, simulation_id: str, relationship_type: str
    ):
        stmt_id = str(uuid.uuid4())
        session.run(
            "MERGE (st:Statement {id: $id}) ON CREATE SET st.data_json = $data_json",
            id=stmt_id,
            data_json=json.dumps(statement.to_dict()),
        )
        session.run(
            f"MATCH (s:Simulation {{id: $s_id}}), (st:Statement {{id: $st_id}}) CREATE (s)-[:{relationship_type}]->(st)",
            s_id=simulation_id,
            st_id=stmt_id,
        )

    def _persist_rule(
        self, session, rule: Rule, simulation_id: str, relationship_type: str
    ):
        rule_id = str(uuid.uuid4())  # Rules should ideally have stable IDs
        session.run(
            "MERGE (r:Rule {id: $id}) ON CREATE SET r.condition_json = $condition_json, r.consequences_json = $consequences_json",
            id=rule_id,
            condition_json=json.dumps(rule.condition.to_dict()),
            consequences_json=json.dumps([c.to_dict() for c in rule.consequences]),
        )
        session.run(
            f"MATCH (s:Simulation {{id: $s_id}}), (r:Rule {{id: $r_id}}) CREATE (s)-[:{relationship_type}]->(r)",
            s_id=simulation_id,
            r_id=rule_id,
        )

    def get_simulation_history(self, belief_system_id: str) -> list[SimulationRecord]:
        history = []
        with self._driver.session() as session:
            query = f"MATCH (bs:BeliefSystem {{id: $belief_system_id}})<-[:{self.REL_USED}]-(s:Simulation) RETURN s ORDER BY s.timestamp ASC"
            result = session.run(query, belief_system_id=belief_system_id)
            for record_node in result:
                props = record_node["s"]
                # Reconstruct SimulationRecord from stored properties
                # Note: This is a simplified reconstruction.
                # For full fidelity, you'd need to fetch related Statement and Rule nodes.
                # Fetch related statements and rules
                initial_statements_data = session.run(
                    "MATCH (s:Simulation {id: $s_id})-[:INTRODUCED]->(st:Statement) RETURN st.data_json AS data",
                    s_id=props["id"],
                ).data()
                initial_statements = [
                    Statement.from_dict(json.loads(v["data"]))
                    for v in initial_statements_data
                ]

                derived_facts_data = session.run(
                    "MATCH (s:Simulation {id: $s_id})-[:DERIVED_FACT]->(st:Statement) RETURN st.data_json AS data",
                    s_id=props["id"],
                ).data()
                derived_facts = [
                    Statement.from_dict(json.loads(v["data"]))
                    for v in derived_facts_data
                ]

                applied_rules_data = session.run(
                    "MATCH (s:Simulation {id: $s_id})-[:APPLIED_RULE]->(r:Rule) RETURN r.condition_json AS condition_data, r.consequences_json AS consequences_data",
                    s_id=props["id"],
                ).data()
                applied_rules = []
                for v in applied_rules_data:
                    rule_dict = {
                        "condition": json.loads(v["condition_data"]),
                        "consequences": json.loads(v["consequences_data"]),
                    }
                    applied_rules.append(Rule.from_dict(rule_dict))

                sim_record = SimulationRecord(
                    initial_statements=initial_statements,
                    derived_facts=derived_facts,
                    applied_rules=applied_rules,
                    forked_belief_system=None,  # Forked system not reconstructed here
                    id=uuid.UUID(props["id"]),
                )
                history.append(sim_record)
        return history

