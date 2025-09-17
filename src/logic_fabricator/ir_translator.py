import structlog
from logic_fabricator.ir.ir_types import IRRule, IRCondition, IRStatement, IREffect
from logic_fabricator.fabric import Rule, Condition, Statement, Effect
from typing import Union, List
from logic_fabricator.exceptions import UnsupportedIRFeatureError
import itertools

logger = structlog.get_logger(__name__)


class IRTranslator:
    """Translates Intermediate Representation (IR) objects into fabric.py runtime types."""

    def translate_ir_condition(self, ir_condition: IRCondition) -> Condition:
        logger.info("Translating IRCondition", ir_condition=ir_condition)
        
        # Handle different types of conditions based on the 'type' field
        if ir_condition.type == "LEAF":
            return self._translate_leaf_condition(ir_condition)
        elif ir_condition.type == "AND":
            and_conditions = [
                self.translate_ir_condition(child) for child in ir_condition.children
            ]
            return Condition(type="AND", children=and_conditions)
        elif ir_condition.type == "OR":
            # OR conditions are handled by _decompose_condition, which is called by translate_ir_rule
            # This method should not receive a top-level OR unless it's part of a recursive call
            raise UnsupportedIRFeatureError(
                "Top-level OR operator in IRCondition should be handled by _decompose_condition."
            )
        elif ir_condition.type in ["EXISTS", "FORALL", "COUNT", "NONE"]:
            # Quantifier conditions
            if ir_condition.type == "FORALL":
                if not ir_condition.children or len(ir_condition.children) != 2:
                    raise ValueError(
                        "FORALL condition must have exactly two children: domain and property."
                    )
            elif not ir_condition.children or len(ir_condition.children) != 1:
                raise ValueError(
                    f"{ir_condition.type} condition must have exactly one child: the sub-condition."
                )

            translated_children = [
                self.translate_ir_condition(child) for child in ir_condition.children
            ]

            if ir_condition.type == "COUNT":
                return Condition(
                    type="COUNT",
                    children=translated_children,
                    operator=ir_condition.operator,
                    value=ir_condition.value,
                )
            else:
                return Condition(type=ir_condition.type, children=translated_children)
        else:
            raise UnsupportedIRFeatureError(
                f"Unsupported IRCondition type: {ir_condition.type}"
            )

    def translate_ir_statement(self, ir_statement: IRStatement) -> Statement:
        logger.info("Translating IRStatement", ir_statement=ir_statement)
        terms = [ir_statement.subject]
        if isinstance(ir_statement.object, list):
            terms.extend(ir_statement.object)
        else:
            terms.append(ir_statement.object)

        translated_statement = Statement(
            verb=ir_statement.verb,
            terms=terms,
            negated=ir_statement.negated,
            priority=1.0,  # Default priority for now
        )
        logger.debug("IRStatement translated", statement=translated_statement)
        return translated_statement

    def translate_ir_effect(self, ir_effect: IREffect) -> Effect:
        logger.info("Translating IREffect", ir_effect=ir_effect)
        translated_effect = Effect(
            target="world_state",
            attribute=ir_effect.target_world_state_key,
            operation=ir_effect.effect_operation,
            value=ir_effect.effect_value,
        )
        logger.debug("IREffect translated", effect=translated_effect)
        return translated_effect

    def _translate_leaf_condition(self, ir_condition: IRCondition) -> Condition:
        """Translates a single, non-recursive LEAF IRCondition."""
        logger.info("Translating LEAF IRCondition", ir_condition=ir_condition)
        terms = [ir_condition.subject]
        if isinstance(ir_condition.object, list):
            terms.extend(ir_condition.object)
        elif isinstance(ir_condition.object, str):
            terms.extend(ir_condition.object.split())
        else:
            terms.append(ir_condition.object)
        return Condition(type="LEAF", verb=ir_condition.verb, terms=terms)

    def _decompose_condition(self, ir_condition: IRCondition) -> List[List[Condition]]:
        """
        Recursively decomposes a complex IRCondition into a list of simple conjunctive groups.
        This is the Disjunctive Normal Form (DNF).
        Example: (A AND (B OR C)) -> [[A, B], [A, C]]
        """
        logger.debug("Decomposing condition", ir_condition=ir_condition)

        # Base case: A LEAF or quantified condition is a DNF group of one.
        if ir_condition.type == "LEAF" or ir_condition.type in ["EXISTS", "FORALL", "COUNT", "NONE"]:
            logger.debug("Decomposition base case: LEAF or quantifier")
            return [[self.translate_ir_condition(ir_condition)]]

        if ir_condition.type == "OR":
            logger.debug("Decomposing OR operator")
            all_decomposed_groups = []
            for child in ir_condition.children:
                all_decomposed_groups.extend(self._decompose_condition(child))
            return all_decomposed_groups

        if ir_condition.type == "AND":
            logger.debug("Decomposing AND operator")
            child_decompositions = [
                self._decompose_condition(child) for child in ir_condition.children
            ]

            product_of_decompositions = list(itertools.product(*child_decompositions))

            combined_groups = []
            for combo in product_of_decompositions:
                flattened_group = [condition for group in combo for condition in group]
                combined_groups.append(flattened_group)
            return combined_groups

        raise UnsupportedIRFeatureError(
            f"Unsupported IRCondition type for decomposition: {ir_condition.type}"
        )

    def translate_ir_rule(self, ir_rule: IRRule) -> List[Rule]:
        logger.info("Translating IRRule", ir_rule=ir_rule)

        if isinstance(ir_rule.consequence, IRStatement):
            translated_consequence = self.translate_ir_statement(ir_rule.consequence)
        elif isinstance(ir_rule.consequence, IREffect):
            translated_consequence = self.translate_ir_effect(ir_rule.consequence)
        else:
            raise ValueError(
                f"Unknown IR consequence type: {type(ir_rule.consequence)}"
            )

        decomposed_and_groups = self._decompose_condition(ir_rule.condition)
        logger.debug("Decomposed condition into DNF groups", groups=decomposed_and_groups)

        translated_rules = []
        for group in decomposed_and_groups:
            if len(group) > 1:
                final_condition = Condition(type="AND", children=group)
            else:
                final_condition = group[0]

            rule = Rule(
                condition=final_condition, consequences=[translated_consequence]
            )
            translated_rules.append(rule)

        logger.debug(
            "IRRule translated into multiple rules", count=len(translated_rules)
        )
        return translated_rules