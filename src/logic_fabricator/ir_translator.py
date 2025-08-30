import structlog # Added structlog import
from logic_fabricator.ir.ir_types import IRRule, IRCondition, IRStatement, IREffect
from logic_fabricator.fabric import Rule, Condition, Statement, Effect
from typing import Union, List
from logic_fabricator.exceptions import UnsupportedIRFeatureError

logger = structlog.get_logger(__name__) # Added logger instance

class IRTranslator:
    """Translates Intermediate Representation (IR) objects into fabric.py runtime types."""

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
            priority=1.0 # Default priority for now
        )
        logger.debug("IRStatement translated", statement=translated_statement)
        return translated_statement

    def translate_ir_condition(self, ir_condition: IRCondition) -> Condition:
        logger.info("Translating IRCondition", ir_condition=ir_condition)
        if ir_condition.exceptions:
            logger.error("Unsupported feature: IRCondition with exceptions.", ir_condition=ir_condition)
            raise UnsupportedIRFeatureError("IRCondition with exceptions is not currently supported by fabric.Condition.")

        if ir_condition.conjunctive_conditions:
            logger.info("Translating conjunctive IRCondition", ir_condition=ir_condition)
            # Create the Condition for the main part of the ir_condition
            main_condition_terms = [ir_condition.subject]
            if isinstance(ir_condition.object, list):
                main_condition_terms.extend(ir_condition.object)
            else:
                main_condition_terms.append(ir_condition.object)

            main_fabric_condition = Condition(
                verb=ir_condition.verb,
                terms=main_condition_terms,
            )

            # Translate the conjunctive conditions recursively
            translated_conjunctive_conditions = [
                self.translate_ir_condition(sub_cond)
                for sub_cond in ir_condition.conjunctive_conditions
            ]

            # Combine all conditions into the and_conditions list
            all_and_conditions = [main_fabric_condition] + translated_conjunctive_conditions

            translated_condition = Condition(
                and_conditions=all_and_conditions,
                verb=None,  # Not applicable for conjunctive conditions
                terms=None  # Not applicable for conjunctive conditions
            )
            logger.debug("Conjunctive IRCondition translated", condition=translated_condition)
            return translated_condition
        else:
            logger.info("Translating simple IRCondition", ir_condition=ir_condition)
            # Handle simple conditions
            terms = [ir_condition.subject]
            if isinstance(ir_condition.object, list):
                terms.extend(ir_condition.object)
            else:
                terms.append(ir_condition.object)

            translated_condition = Condition(
                verb=ir_condition.verb,
                terms=terms,
                and_conditions=None, # Not applicable for simple conditions
                verb_synonyms=None # Not in IR for now
            )
            logger.debug("Simple IRCondition translated", condition=translated_condition)
            return translated_condition

    def translate_ir_effect(self, ir_effect: IREffect) -> Effect:
        logger.info("Translating IREffect", ir_effect=ir_effect)
        translated_effect = Effect(
            target="world_state",
            attribute=ir_effect.target_world_state_key,
            operation=ir_effect.effect_operation,
            value=ir_effect.effect_value
        )
        logger.debug("IREffect translated", effect=translated_effect)
        return translated_effect

    def translate_ir_rule(self, ir_rule: IRRule) -> Rule:
        logger.info("Translating IRRule", ir_rule=ir_rule)
        translated_condition = self.translate_ir_condition(ir_rule.condition)

        if isinstance(ir_rule.consequence, IRStatement):
            translated_consequence = self.translate_ir_statement(ir_rule.consequence)
        elif isinstance(ir_rule.consequence, IREffect):
            translated_consequence = self.translate_ir_effect(ir_rule.consequence)
        else:
            logger.error("Unknown IR consequence type", ir_consequence_type=type(ir_rule.consequence))
            raise ValueError(f"Unknown IR consequence type: {type(ir_rule.consequence)}")

        translated_rule = Rule(
            condition=translated_condition,
            consequences=[translated_consequence]
        )
        logger.debug("IRRule translated", rule=translated_rule)
        return translated_rule
