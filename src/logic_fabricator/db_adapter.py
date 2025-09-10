
from typing import Protocol
from .fabric import Rule, Statement, ForkingStrategy, SimulationRecord

class DatabaseAdapter(Protocol):
    """
    A protocol that defines the interface for a database adapter.
    This allows the MCP to be decoupled from the specific database implementation.
    """

    def create_belief_system(self, id: str, name: str, strategy: ForkingStrategy):
        ...

    def add_rule(self, belief_system_id: str, rule: Rule):
        ...

    def fork_belief_system(self, parent_id: str, forked_id: str, name: str, strategy: ForkingStrategy):
        ...

    def persist_simulation(self, belief_system_id: str, simulation_record: SimulationRecord):
        ...

    def get_simulation_history(self, belief_system_id: str) -> list[SimulationRecord]:
        ...

    def save_statement(self, statement: Statement) -> str:
        ...

    def load_statement(self, statement_id: str) -> Statement | None:
        ...

    def close(self):
        ...
