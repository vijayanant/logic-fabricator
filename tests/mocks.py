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

    def get_simulation_history(self, belief_system_id: str) -> list[SimulationRecord]:
        return [sim for sim in self.simulations if sim.belief_system_id == belief_system_id]

    def save_statement(self, statement: Statement) -> str:
        import uuid
        statement_id = str(uuid.uuid4())
        self.statements[statement_id] = statement
        return statement_id

    def load_statement(self, statement_id: str) -> Statement | None:
        return self.statements.get(statement_id)

    def close(self):
        pass