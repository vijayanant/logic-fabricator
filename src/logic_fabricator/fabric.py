import enum
import json
import structlog
from typing import Optional
import uuid
from dataclasses import dataclass, field

from .core_types import (
    Statement,
    Condition,
    Rule,
    Effect,
    ContradictionRecord,
    InferredContradiction,
    BeliefSystem,
    ContradictionEngine,
    ForkingStrategy,
    op_set,
    op_increment,
    op_decrement,
    op_append,
    SimulationResult,
    SimulationRecord,
)

logger = structlog.get_logger(__name__)