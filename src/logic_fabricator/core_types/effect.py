class Effect:
    def __init__(self, target: str, attribute: str, operation: str, value: any):
        self.target = target
        self.attribute = attribute
        self.operation = operation
        self.value = value

    def __str__(self):
        return (
            f"Effect: {self.operation} {self.target}.{self.attribute} to {self.value}"
        )

    def __repr__(self):
        return f"Effect(op={self.operation}, target={self.target}.{self.attribute}, val={self.value})"

    def __eq__(self, other):
        if not isinstance(other, Effect):
            return NotImplemented
        return (
            self.target == other.target
            and self.attribute == other.attribute
            and self.operation == other.operation
            and self.value == other.value
        )

    def __hash__(self):
        return hash((self.target, self.attribute, self.operation, self.value))

    def to_dict(self):
        return {
            "target": self.target,
            "attribute": self.attribute,
            "operation": self.operation,
            "value": self.value,
        }
