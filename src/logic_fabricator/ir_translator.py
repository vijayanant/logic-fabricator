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
        if ir_condition.quantifier == "FORALL":
            if not ir_condition.children or len(ir_condition.children) != 2:
                raise ValueError(
                    "FORALL condition must have exactly two children: domain and property."
                )
            domain_ir = ir_condition.children[0]
            property_ir = ir_condition.children[1]
            return Condition(
                forall_condition=(
                    self.translate_ir_condition(domain_ir),
                    self.translate_ir_condition(property_ir),
                )
            )
        elif ir_condition.quantifier == "EXISTS":
            if not ir_condition.children or len(ir_condition.children) != 1:
                raise ValueError(
                    "EXISTS condition must have exactly one child: the sub-condition."
                )
            sub_ir_condition = ir_condition.children[0]
            return Condition(
                exists_condition=self.translate_ir_condition(sub_ir_condition)
            )
        elif ir_condition.quantifier == "COUNT":
            if not ir_condition.children or len(ir_condition.children) != 1:
                raise ValueError(
                    "COUNT condition must have exactly one child: the sub-condition."
                )
            sub_ir_condition = ir_condition.children[0]
            operator = (
                ir_condition.operator
            )  # Assuming operator is directly on IRCondition for COUNT
            value = (
                ir_condition.object
            )  # Assuming value is directly on IRCondition for COUNT
            return Condition(
                count_condition=(
                    self.translate_ir_condition(sub_ir_condition),
                    operator,
                    value,
                )
            )
        elif ir_condition.quantifier == "NONE":
            if not ir_condition.children or len(ir_condition.children) != 1:
                raise ValueError(
                    "NONE condition must have exactly one child: the sub-condition."
                )
            sub_ir_condition = ir_condition.children[0]
            return Condition(
                none_condition=self.translate_ir_condition(sub_ir_condition)
            )

        # Quantifier checks are done. Now check operators.
        elif ir_condition.operator == "LEAF":
            return self._translate_leaf_condition(ir_condition)
        elif ir_condition.operator == "AND":
            # For AND, we need to translate its children recursively
            and_conditions = [
                self.translate_ir_condition(child) for child in ir_condition.children
            ]
            return Condition(and_conditions=and_conditions)
        elif ir_condition.operator == "OR":
            # OR conditions are handled by _decompose_condition, which is called by translate_ir_rule
            # This method should not receive a top-level OR unless it's part of a recursive call
            raise UnsupportedIRFeatureError(
                "Top-level OR operator in IRCondition should be handled by _decompose_condition."
            )
        else:
            raise UnsupportedIRFeatureError(
                f"Unsupported IRCondition type: {ir_condition.operator} or {ir_condition.quantifier}"
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
        return Condition(verb=ir_condition.verb, terms=terms)

    def _decompose_condition(self, ir_condition: IRCondition) -> List[List[Condition]]:
        """
        Recursively decomposes a complex IRCondition into a list of simple conjunctive groups.
        This is the Disjunctive Normal Form (DNF).
        Example: (A AND (B OR C)) -> [[A, B], [A, C]]
        """
        if ir_condition.operator == "LEAF" or ir_condition.quantifier: # Combined check
            return [[self.translate_ir_condition(ir_condition)]]  # Call new method

        if ir_condition.operator == "OR":
            all_decomposed_groups = []
            for child in ir_condition.children:
                all_decomposed_groups.extend(self._decompose_condition(child))
            return all_decomposed_groups

        if ir_condition.operator == "AND":
            child_decompositions = [
                self._decompose_condition(child) for child in ir_condition.children
            ]

            product_of_decompositions = list(itertools.product(*child_decompositions))

            combined_groups = []
            for combo in product_of_decompositions:
                flattened_group = [condition for group in combo for condition in group]
                combined_groups.append(flattened_group)
            return combined_groups

        # This handles the legacy IRCondition format
        if (
            hasattr(ir_condition, "conjunctive_conditions")
            and ir_condition.conjunctive_conditions
        ):
            main_cond = self.translate_ir_condition(ir_condition)  # Call new method
            child_conds = [
                self.translate_ir_condition(c)
                for c in ir_condition.conjunctive_conditions
            ]  # Call new method
            return [[main_cond] + child_conds]
        else:
            raise UnsupportedIRFeatureError(f"Unsupported IRCondition type for decomposition: {ir_condition.operator} or {ir_condition.quantifier}")

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

        translated_rules = []
        for group in decomposed_and_groups:
            if len(group) > 1:
                final_condition = Condition(and_conditions=group)
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