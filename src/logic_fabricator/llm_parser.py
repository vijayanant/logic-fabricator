import json
import os
from pathlib import Path
from openai import OpenAI
import json
import structlog  # Added structlog import
from typing import Union
from .ir.ir_types import IRRule, IRCondition, IREffect, IRStatement
from .config import Config, load_config

logger = structlog.get_logger(__name__)  # Added logger instance


class LLMParser:
    """A class to parse natural language into structured logic using an LLM."""

    def __init__(self):
        """Initializes the parser using settings from the configuration and loads the system prompt."""
        self.config = load_config()
        self.client = OpenAI(
            base_url=self.config.llm_base_url,
            api_key=self.config.llm_api_key,
        )
        # Load the system prompt from file
        prompt_file_path = (
            Path(__file__).parent / "prompts" / "ir_parser_system_prompt.md"
        )
        with open(prompt_file_path, "r") as f:
            self.system_prompt = f.read()

    def _parse_ir_condition(self, data: dict) -> IRCondition:
        return IRCondition(
            subject=data["subject"],
            verb=data["verb"],
            object=data["object"],
            negated=data.get("negated", False),
            modifiers=data.get("modifiers", []),
            conjunctive_conditions=[
                self._parse_ir_condition(cc)
                for cc in data.get("conjunctive_conditions", [])
            ],
            exceptions=[
                self._parse_ir_condition(exc) for exc in data.get("exceptions", [])
            ],
        )

    def _parse_ir_statement(self, data: dict) -> IRStatement:
        return IRStatement(
            subject=data["subject"],
            verb=data["verb"],
            object=data["object"],
            negated=data.get("negated", False),
            modifiers=data.get("modifiers", []),
        )

    def _parse_ir_effect(self, data: dict) -> IREffect:
        return IREffect(
            target_world_state_key=data["target_world_state_key"],
            effect_operation=data["effect_operation"],
            effect_value=data["effect_value"],
        )

    def parse_natural_language(self, text: str) -> Union[IRRule, IRStatement, None]:
        """
        Parses any natural language input and returns the appropriate IR object.
        The LLM will determine the type of input.
        """
        try:
            response = self.client.chat.completions.create(
                model=self.config.llm_model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": text},
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
            )

            json_response = response.choices[0].message.content
            data = json.loads(json_response)

            input_type = data.get("input_type")
            ir_data = data.get("data")

            if input_type == "rule":
                return IRRule.from_dict(ir_data)
            elif input_type == "statement":
                return IRStatement.from_dict(ir_data)
            # Add more types (e.g., "question") here in the future
            else:
                raise ValueError(f"Unknown input type: {input_type}")

        except Exception as e:
            logger.error("LLM parsing error", error=str(e))
            return None
