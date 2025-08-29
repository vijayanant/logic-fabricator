from logic_fabricator.ir.ir_types import IRRule, IRCondition, IRStatement, IREffect
from logic_fabricator.fabric import Rule, Condition, Statement, Effect
from typing import Union, List
from logic_fabricator.exceptions import UnsupportedIRFeatureError

class IRTranslator:
    """Translates Intermediate Representation (IR) objects into fabric.py runtime types."""

    def translate_ir_statement(self, ir_statement: IRStatement) -> Statement:
        terms = [ir_statement.subject]
        if isinstance(ir_statement.object, list):
            terms.extend(ir_statement.object)
        else:
            terms.append(ir_statement.object)

        return Statement(
            verb=ir_statement.verb,
            terms=terms,
            negated=ir_statement.negated,
            priority=1.0 # Default priority for now
        )

    def translate_ir_condition(self, ir_condition: IRCondition) -> Condition:
        if ir_condition.exceptions:
            raise UnsupportedIRFeatureError("IRCondition with exceptions is not currently supported by fabric.Condition.")

        if ir_condition.conjunctive_conditions:
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

            return Condition(
                and_conditions=all_and_conditions,
                verb=None,  # Not applicable for conjunctive conditions
                terms=None  # Not applicable for conjunctive conditions
            )
            # The first condition in the conjunctive list is the main one
            # The rest are 'and_conditions'
            # fabric.Condition expects a list of Conditions for and_conditions
            # and the main condition's verb/terms are None
            return Condition(
                and_conditions=translated_and_conditions,
                verb=None,
                terms=None
            )
        else:
            # Handle simple conditions
            terms = [ir_condition.subject]
            if isinstance(ir_condition.object, list):
                terms.extend(ir_condition.object)
            else:
                terms.append(ir_condition.object)

            return Condition(
                verb=ir_condition.verb,
                terms=terms,
                and_conditions=None, # Not applicable for simple conditions
                verb_synonyms=None # Not in IR for now
            )

    def translate_ir_effect(self, ir_effect: IREffect) -> Effect:
        return Effect(
            target="world_state",
            attribute=ir_effect.target_world_state_key,
            operation=ir_effect.effect_operation,
            value=ir_effect.effect_value
        )

    def translate_ir_rule(self, ir_rule: IRRule) -> Rule:
        translated_condition = self.translate_ir_condition(ir_rule.condition)

        if isinstance(ir_rule.consequence, IRStatement):
            translated_consequence = self.translate_ir_statement(ir_rule.consequence)
        elif isinstance(ir_rule.consequence, IREffect):
            translated_consequence = self.translate_ir_effect(ir_rule.consequence)
        else:
            raise ValueError(f"Unknown IR consequence type: {type(ir_rule.consequence)}")

        return Rule(
            condition=translated_condition,
            consequences=[translated_consequence]
        )
