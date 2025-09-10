from dataclasses import dataclass, field
from typing import Optional
import uuid

from .statement import Statement
from .rule import Rule


@dataclass
class SimulationRecord:
    belief_system_id: str
    initial_statements: list[Statement]
    derived_facts: list[Statement]
    applied_rules: list[Rule]
    forked_belief_system: Optional["BeliefSystem"] = None
    id: uuid.UUID = field(default_factory=uuid.uuid4)

    def __str__(self):
        fork_str = (
            f", forked={self.forked_belief_system.id}"
            if self.forked_belief_system
            else ""
        )
        return (
            f"SimulationRecord(initial={len(self.initial_statements)}, "
            f"derived={len(self.derived_facts)}, applied={len(self.applied_rules)}{fork_str})"
        )

    def __repr__(self):
        fork_repr = (
            repr(self.forked_belief_system) if self.forked_belief_system else "None"
        )
        return (
            f"SimulationRecord(initial_statements={repr(self.initial_statements)}, "
            f"derived_facts={repr(self.derived_facts)}, "
            f"applied_rules={repr(self.applied_rules)}, "
            f"forked_belief_system={fork_repr})"
        )


class SimulationResult:
    def __init__(
        self,
        derived_facts: list[Statement],
        applied_rules: list[Rule],
        forked_belief_system: Optional["BeliefSystem"] = None,
    ):
        self.derived_facts = derived_facts
        self.applied_rules = applied_rules
        self.forked_belief_system = forked_belief_system

    def __str__(self):
        fork_str = (
            f", forked={self.forked_belief_system.id}"
            if self.forked_belief_system
            else ""
        )
        return (
            f"SimulationResult(derived={len(self.derived_facts)}, "
            f"applied={len(self.applied_rules)}{fork_str})"
        )

    def __repr__(self):
        fork_repr = (
            repr(self.forked_belief_system) if self.forked_belief_system else "None"
        )
        return (
            f"SimulationResult(derived_facts={repr(self.derived_facts)}, "
            f"applied_rules={repr(self.applied_rules)}, "
            f"forked_belief_system={fork_repr})"
        )
