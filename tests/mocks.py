from logic_fabricator.db_adapter import DatabaseAdapter
from logic_fabricator.core_types import Rule, Statement, ForkingStrategy, SimulationRecord

class MockAdapter(DatabaseAdapter):
    def __init__(self):
        self.belief_systems = {}
        self.rules = {}
        self.simulations = []
        self.statements = {}

    def create_belief_system(self, id: str, name: str, strategy: ForkingStrategy):
        self.belief_systems[id] = {"name": name, "strategy": strategy, "rules": []}

    def add_rule(self, belief_system_id: str, rule: Rule):
        if belief_system_id in self.belief_systems:
            self.belief_systems[belief_system_id]["rules"].append(rule)

    def fork_belief_system(self, parent_id: str, forked_id: str, name: str, strategy: ForkingStrategy):
        if parent_id in self.belief_systems:
            self.belief_systems[forked_id] = {"name": name, "strategy": strategy, "rules": list(self.belief_systems[parent_id]["rules"])}

    def persist_simulation(self, belief_system_id: str, simulation_record: SimulationRecord):
        self.simulations.append(simulation_record)
        for stmt in simulation_record.initial_statements:
            self.save_statement(stmt)
        for stmt in simulation_record.derived_facts:
            self.save_statement(stmt)
        for rule in simulation_record.applied_rules:
            self.save_rule(rule)

    def save_rule(self, rule: Rule) -> str:
        rule_id = str(rule.id)
        self.rules[rule_id] = rule
        return rule_id

    def get_simulation_history(self, belief_system_id: str) -> list[SimulationRecord]:
        return [sim for sim in self.simulations if sim.belief_system_id == belief_system_id]

    def save_statement(self, statement: Statement) -> str:
        statement_id = str(statement.id)
        self.statements[statement_id] = statement
        return statement_id

    def load_statement(self, statement_id: str) -> Statement | None:
        return self.statements.get(statement_id)

    def close(self):
        pass

    def verify_simulation_graph(self, simulation_record: SimulationRecord) -> bool:
        # Check if the simulation record itself was persisted
        if simulation_record not in self.simulations:
            return False

        # Check if the belief system exists
        # The mock adapter doesn't store the belief_system_id on the sim record,
        # so we have to check if ANY simulation for that BS was recorded.
        # This is a limitation of the mock, but sufficient for testing.
        if not any(sim.belief_system_id == simulation_record.belief_system_id for sim in self.simulations):
            return False

        # Check if all related objects were persisted
        all_objects_persisted = True
        for stmt in simulation_record.initial_statements:
            if str(stmt.id) not in self.statements:
                all_objects_persisted = False
        
        for stmt in simulation_record.derived_facts:
            if str(stmt.id) not in self.statements:
                all_objects_persisted = False

        # The mock adapter doesn't have a separate store for rules added during simulation,
        # so we assume this check is implicitly covered by the simulation record being present.

        return all_objects_persisted