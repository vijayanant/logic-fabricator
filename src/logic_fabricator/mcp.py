import structlog
from .fabric import (
    BeliefSystem,
    Rule,
    Statement,
    ContradictionEngine,
    ForkingStrategy,
    SimulationRecord,
)
from .db_adapter import DatabaseAdapter

logger = structlog.get_logger(__name__)

class MCP:
    def __init__(self, db_adapter: DatabaseAdapter):
        self.db_adapter = db_adapter
        self.belief_systems = {}
        self.contradiction_engine = ContradictionEngine()
        logger.info("MCP initialized.")

    def close(self):
        self.db_adapter.close()

    def create_belief_system(
        self, name: str, strategy: ForkingStrategy = ForkingStrategy.COEXIST
    ) -> str:
        belief_system = BeliefSystem(
            rules=[], contradiction_engine=self.contradiction_engine, strategy=strategy
        )
        self.belief_systems[str(belief_system.id)] = belief_system
        self.db_adapter.create_belief_system(str(belief_system.id), name, strategy)
        return str(belief_system.id)

    def add_rule(self, belief_system_id: str, rule: Rule):
        belief_system = self.belief_systems.get(belief_system_id)
        if not belief_system:
            logger.error("BeliefSystem not found.", id=belief_system_id)
            raise ValueError(f"BeliefSystem with ID {belief_system_id} not found.")
        belief_system.rules.append(rule)
        self.db_adapter.add_rule(belief_system_id, rule)

    def fork_belief_system(self, parent_id: str, name: str) -> str:
        parent_belief_system = self.belief_systems.get(parent_id)
        if not parent_belief_system:
            logger.error("Parent BeliefSystem not found.", id=parent_id)
            raise ValueError(f"Parent BeliefSystem with ID {parent_id} not found.")
        
        forked_belief_system = BeliefSystem(
            rules=list(parent_belief_system.rules),
            contradiction_engine=parent_belief_system.contradiction_engine,
            strategy=parent_belief_system.strategy,
        )
        forked_belief_system.statements = set(parent_belief_system.statements)
        forked_belief_system.world_state = parent_belief_system.world_state.copy()
        forked_belief_system.effects_applied = set(parent_belief_system.effects_applied)

        self.belief_systems[str(forked_belief_system.id)] = forked_belief_system
        self.db_adapter.fork_belief_system(parent_id, str(forked_belief_system.id), name, forked_belief_system.strategy)
        return str(forked_belief_system.id)

    def simulate(self, belief_system_id: str, statements: list[Statement]) -> SimulationRecord:
        belief_system = self.belief_systems.get(belief_system_id)
        if not belief_system:
            logger.error("BeliefSystem not found.", id=belief_system_id)
            raise ValueError(f"BeliefSystem with ID {belief_system_id} not found.")

        simulation_result = belief_system.simulate(statements)
        
        simulation_record = SimulationRecord(
            initial_statements=statements,
            derived_facts=simulation_result.derived_facts,
            applied_rules=simulation_result.applied_rules,
            forked_belief_system=simulation_result.forked_belief_system,
            belief_system_id=belief_system_id,
        )

        self.db_adapter.persist_simulation(belief_system_id, simulation_record)
        return simulation_record

    def get_simulation_history(self, belief_system_id: str) -> list[SimulationRecord]:
        return self.db_adapter.get_simulation_history(belief_system_id)

