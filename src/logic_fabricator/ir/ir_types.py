from typing import Any, List, Optional, Union

class IRBase:
    """Base class for all Intermediate Representation objects."""
    pass

class IRCondition(IRBase):
    def __init__(self, subject: str, verb: str, object: Union[str, List[str]], negated: bool = False,
                 modifiers: Optional[List[str]] = None,
                 conjunctive_conditions: Optional[List['IRCondition']] = None,
                 exceptions: Optional[List['IRCondition']] = None):
        self.subject = subject
        self.verb = verb
        self.object = object
        self.negated = negated
        self.modifiers = modifiers if modifiers is not None else []
        self.conjunctive_conditions = conjunctive_conditions if conjunctive_conditions is not None else []
        self.exceptions = exceptions if exceptions is not None else []

    def __eq__(self, other):
        if not isinstance(other, IRCondition):
            return NotImplemented
        return (self.subject == other.subject and
                self.verb == other.verb and
                self.object == other.object and
                self.negated == other.negated and
                self.modifiers == other.modifiers and
                self.conjunctive_conditions == other.conjunctive_conditions and
                self.exceptions == other.exceptions)

    def __repr__(self):
        return (f"IRCondition(subject='{self.subject}', verb='{self.verb}', object={self.object}, "
                f"negated={self.negated}, modifiers={self.modifiers}, "
                f"conjunctive_conditions={self.conjunctive_conditions}, exceptions={self.exceptions})")

    @classmethod
    def from_dict(cls, data: dict) -> 'IRCondition':
        return cls(
            subject=data["subject"],
            verb=data["verb"],
            object=data["object"],
            negated=data.get("negated", False),
            modifiers=data.get("modifiers", []),
            conjunctive_conditions=[IRCondition.from_dict(cc) for cc in data.get("conjunctive_conditions", [])],
            exceptions=[IRCondition.from_dict(exc) for exc in data.get("exceptions", [])]
        )

class IRStatement(IRBase):
    def __init__(self, subject: str, verb: str, object: Union[str, List[str]], negated: bool = False,
                 modifiers: Optional[List[str]] = None):
        self.subject = subject
        self.verb = verb
        self.object = object
        self.negated = negated
        self.modifiers = modifiers if modifiers is not None else []

    def __eq__(self, other):
        if not isinstance(other, IRStatement):
            return NotImplemented
        return (self.subject == other.subject and
                self.verb == other.verb and
                self.object == other.object and
                self.negated == other.negated and
                self.modifiers == other.modifiers)

    def __repr__(self):
        return (f"IRStatement(subject='{self.subject}', verb='{self.verb}', object={self.object}, "
                f"negated={self.negated}, modifiers={self.modifiers})")

    @classmethod
    def from_dict(cls, data: dict) -> 'IRStatement':
        return cls(
            subject=data["subject"],
            verb=data["verb"],
            object=data["object"],
            negated=data.get("negated", False),
            modifiers=data.get("modifiers", [])
        )

class IREffect(IRBase):
    def __init__(self, target_world_state_key: str, effect_operation: str, effect_value: Any):
        self.target_world_state_key = target_world_state_key
        self.effect_operation = effect_operation
        self.effect_value = effect_value

    def __eq__(self, other):
        if not isinstance(other, IREffect):
            return NotImplemented
        return (self.target_world_state_key == other.target_world_state_key and
                self.effect_operation == other.effect_operation and
                self.effect_value == other.effect_value)

    def __repr__(self):
        return (f"IREffect(target_world_state_key='{self.target_world_state_key}', "
                f"effect_operation='{self.effect_operation}', effect_value={self.effect_value})")

    @classmethod
    def from_dict(cls, data: dict) -> 'IREffect':
        return cls(
            target_world_state_key=data["target_world_state_key"],
            effect_operation=data["effect_operation"],
            effect_value=data["effect_value"]
        )

class IRRule(IRBase):
    def __init__(self, rule_type: str, condition: IRCondition,
                 consequence: Union[IRStatement, IREffect]):
        self.rule_type = rule_type # "standard" or "effect"
        self.condition = condition
        self.consequence = consequence

    def __eq__(self, other):
        if not isinstance(other, IRRule):
            return NotImplemented
        return (self.rule_type == other.rule_type and
                self.condition == other.condition and
                self.consequence == other.consequence)

    def __repr__(self):
        return (f"IRRule(rule_type='{self.rule_type}', condition={self.condition}, "
                f"consequence={self.consequence})")

    @classmethod
    def from_dict(cls, data: dict) -> 'IRRule':
        condition = IRCondition.from_dict(data["condition"])
        consequence_data = data["consequence"]

        if consequence_data["type"] == "statement":
            consequence = IRStatement.from_dict(consequence_data)
        elif consequence_data["type"] == "effect":
            consequence = IREffect.from_dict(consequence_data)
        else:
            raise ValueError(f"Unknown consequence type: {consequence_data['type']}")

        return cls(
            rule_type=data["rule_type"],
            condition=condition,
            consequence=consequence
        )