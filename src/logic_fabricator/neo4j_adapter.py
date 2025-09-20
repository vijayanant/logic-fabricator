
import os
import time
import uuid
import json
import structlog
from neo4j import GraphDatabase
from .core_types import Rule, Statement, ForkingStrategy, SimulationRecord
from .db_adapter import DatabaseAdapter

logger = structlog.get_logger(__name__)

class Neo4jAdapter(DatabaseAdapter):
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
        logger.info("Neo4jAdapter initialized and connected to Neo4j.")

    def close(self):
        self._driver.close()

    def create_belief_system(self, id: str, name: str, strategy: ForkingStrategy):
        with self._driver.session() as session:
            session.run(
                "CREATE (bs:BeliefSystem {id: $id, name: $name, strategy: $strategy, created_at: $created_at})",
                id=id,
                name=name,
                strategy=strategy.value,
                created_at=time.time(),
            )
        logger.info("BeliefSystem created and persisted.", id=id, name=name)

    def add_rule(self, belief_system_id: str, rule: Rule):
        with self._driver.session() as session:
            condition_json = json.dumps(rule.condition.to_dict())
            consequences_json = json.dumps([c.to_dict() for c in rule.consequences])
            session.run(
                f"""MERGE (r:Rule {{condition_json: $condition_json, consequences_json: $consequences_json}})
                   ON CREATE SET r.id = $rule_id
                   WITH r
                   MATCH (bs:BeliefSystem {{id: $bs_id}})
                   MERGE (bs)-[:{self.REL_CONTAINS_RULE}]->(r)""",
                bs_id=belief_system_id,
                rule_id=str(rule.id),
                condition_json=condition_json,
                consequences_json=consequences_json,
            )
        logger.info("Rule added and persisted.", rule=rule, belief_system_id=belief_system_id)

    def fork_belief_system(self, parent_id: str, forked_id: str, name: str, strategy: ForkingStrategy):
        with self._driver.session() as session:
            session.run(
                "CREATE (bs:BeliefSystem {id: $id, name: $name, strategy: $strategy, created_at: $created_at})",
                id=forked_id,
                name=name,
                strategy=strategy.value,
                created_at=time.time(),
            )
            session.run(
                f"MATCH (forked_bs:BeliefSystem {{id: $forked_id}}), (parent_bs:BeliefSystem {{id: $parent_id}}) CREATE (forked_bs)-[:FORKED_FROM]->(parent_bs)",
                forked_id=forked_id,
                parent_id=parent_id,
            )
        logger.info("BeliefSystem forked and persisted.", parent_id=parent_id, forked_id=forked_id, name=name)

    def persist_simulation(self, belief_system_id: str, simulation_record: SimulationRecord):
        with self._driver.session() as session:
            properties = {
                "id": str(simulation_record.id),
                "timestamp": time.time(),
                "forked_belief_system_id": str(simulation_record.forked_belief_system.id) if simulation_record.forked_belief_system else None,
            }
            session.run(
                "CREATE (s:Simulation {id: $id}) SET s += $props",
                id=str(simulation_record.id),
                props=properties,
            )
            session.run(
                f"MATCH (bs:BeliefSystem {{id: $bs_id}}), (s:Simulation {{id: $s_id}}) CREATE (s)-[:{self.REL_USED}]->(bs)",
                bs_id=belief_system_id,
                s_id=str(simulation_record.id),
            )
            for stmt in simulation_record.initial_statements:
                stmt_id = self.save_statement(stmt)
                session.run(
                    f"MATCH (s:Simulation {{id: $s_id}}), (st:Statement {{id: $st_id}}) CREATE (s)-[:{self.REL_INTRODUCED}]->(st)",
                    s_id=str(simulation_record.id),
                    st_id=stmt_id,
                )
            for stmt in simulation_record.derived_facts:
                stmt_id = self.save_statement(stmt)
                session.run(
                    f"MATCH (s:Simulation {{id: $s_id}}), (st:Statement {{id: $st_id}}) CREATE (s)-[:{self.REL_DERIVED_FACT}]->(st)",
                    s_id=str(simulation_record.id),
                    st_id=stmt_id,
                )
            for rule in simulation_record.applied_rules:
                self._persist_rule(session, rule, str(simulation_record.id), self.REL_APPLIED_RULE)
        logger.info("Simulation orchestrated and persisted.", simulation_id=simulation_record.id, belief_system_id=belief_system_id)

    def save_statement(self, statement: Statement) -> str:
        with self._driver.session() as session:
            terms_json = json.dumps(statement.terms)
            result = session.run(
                """MERGE (st:Statement {verb: $verb, terms_json: $terms_json, negated: $negated})
                   ON CREATE SET st.id = $id, st.priority = $priority
                   RETURN st.id AS id""",
                verb=statement.verb,
                terms_json=terms_json,
                negated=statement.negated,
                id=str(statement.id),
                priority=statement.priority,
            )
            # Get the ID of the merged node, whether it was created or matched.
            record = result.single()
            return record["id"]

    def load_statement(self, statement_id: str) -> Statement | None:
        with self._driver.session() as session:
            result = session.run("MATCH (st:Statement {id: $id}) RETURN st", id=statement_id)
            record = result.single()
            if record:
                node = record["st"]
                return Statement(
                    id=uuid.UUID(node["id"]),
                    verb=node["verb"],
                    terms=json.loads(node["terms_json"]),
                    negated=node["negated"],
                    priority=node["priority"],
                )
            return None

    def _persist_rule(self, session, rule: Rule, simulation_id: str, relationship_type: str):
        condition_json = json.dumps(rule.condition.to_dict())
        consequences_json = json.dumps([c.to_dict() for c in rule.consequences])
        session.run(
            f"""MERGE (r:Rule {{condition_json: $condition_json, consequences_json: $consequences_json}})
               ON CREATE SET r.id = $rule_id
               WITH r
               MATCH (s:Simulation {{id: $s_id}})
               MERGE (s)-[:{relationship_type}]->(r)""",
            s_id=simulation_id,
            rule_id=str(rule.id),
            condition_json=condition_json,
            consequences_json=consequences_json,
        )

    def get_simulation_history(self, belief_system_id: str) -> list[SimulationRecord]:
        history = []
        with self._driver.session() as session:
            query = f"MATCH (bs:BeliefSystem {{id: $belief_system_id}})<-[:{self.REL_USED}]-(s:Simulation) RETURN s ORDER BY s.timestamp ASC"
            result = session.run(query, belief_system_id=belief_system_id)
            for record_node in result:
                props = record_node["s"]
                initial_statements_data = session.run(
                    "MATCH (s:Simulation {id: $s_id})-[:INTRODUCED]->(st:Statement) RETURN st.id AS id",
                    s_id=props["id"],
                ).data()
                initial_statements = [self.load_statement(v["id"]) for v in initial_statements_data]
                derived_facts_data = session.run(
                    "MATCH (s:Simulation {id: $s_id})-[:DERIVED_FACT]->(st:Statement) RETURN st.id AS id",
                    s_id=props["id"],
                ).data()
                derived_facts = [self.load_statement(v["id"]) for v in derived_facts_data]
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
                    belief_system_id=belief_system_id,
                    initial_statements=initial_statements,
                    derived_facts=derived_facts,
                    applied_rules=applied_rules,
                    forked_belief_system=None,
                    id=uuid.UUID(props["id"]),
                )
                history.append(sim_record)
        return history

    def verify_simulation_graph(self, simulation_record: SimulationRecord) -> bool:
        with self._driver.session() as session:
            bs_id = str(simulation_record.belief_system_id)

            # This is the query from our test, now properly encapsulated.
            result = session.run("""
                MATCH (sim:Simulation {id: $sim_id})
                MATCH (bs:BeliefSystem {id: $bs_id})
                MATCH (intro_stmt:Statement {id: $intro_id})
                MATCH (derived_stmt:Statement {id: $derived_id})
                MATCH (rule_node:Rule {id: $rule_id})
                
                MATCH (sim)-[:USED]->(bs)
                MATCH (sim)-[:INTRODUCED]->(intro_stmt)
                MATCH (sim)-[:APPLIED_RULE]->(rule_node)
                MATCH (sim)-[:DERIVED_FACT]->(derived_stmt)
                
                RETURN sim
            """, {
                "sim_id": str(simulation_record.id),
                "bs_id": bs_id,
                "intro_id": str(simulation_record.initial_statements[0].id),
                "derived_id": str(simulation_record.derived_facts[0].id),
                "rule_id": str(simulation_record.applied_rules[0].id)
            }).single()
            
            return result is not None
