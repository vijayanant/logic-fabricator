import json
from openai import OpenAI
from .fabric import Rule, Condition, Statement
from .config import load_config


class LLMParser:
    """A class to parse natural language into structured logic using an LLM."""

    def __init__(self):
        """Initializes the parser using settings from the configuration."""
        self.config = load_config()
        self.client = OpenAI(
            base_url=self.config.llm_base_url,
            api_key=self.config.llm_api_key,
        )

    def parse_rule(self, text: str) -> Rule | None:
        """Takes a natural language string and returns a structured Rule object."""

        system_prompt = (
            "You are an expert system designed to parse natural language into structured logical rules. "
            "Your task is to convert a user's rule into a specific JSON format. "
            "The JSON object must have two keys: 'condition' and 'consequence'. "
            "Each key's value is an object with 'verb' and 'terms' keys. 'terms' is a list of strings. "
            "Identify variables in the user's rule and represent them with a '_?' prefix, like '?x' or '?person'."
            "Ensure the verb is a single, normalized token (e.g., 'is', 'trusts')."
            "For the text 'if a man exists, he is mortal', you would return: "
            '{"condition": {"verb": "is", "terms": ["?x", "a_man"]}, '
            '"consequence": {"verb": "is", "terms": ["?x", "mortal"]}}'
        )

        try:
            response = self.client.chat.completions.create(
                model=self.config.llm_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text},
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
            )

            json_response = response.choices[0].message.content
            data = json.loads(json_response)

            cond_data = data["condition"]
            cons_data = data["consequence"]

            condition = Condition(verb=cond_data["verb"], terms=cond_data["terms"])
            consequence = Statement(verb=cons_data["verb"], terms=cons_data["terms"])

            return Rule(condition=condition, consequences=[consequence])

        except Exception as e:
            print(f"[LLMParser Error]: An error occurred while parsing the rule: {e}")
            return None

