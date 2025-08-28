import os
from dataclasses import dataclass
from dotenv import load_dotenv

@dataclass
class Config:
    """Configuration object for the Logic Fabricator, loaded from environment variables."""
    llm_provider: str
    llm_model: str
    llm_api_key: str
    llm_base_url: str | None

def load_config() -> Config:
    """Loads all configuration from environment variables.

    Raises ValueError if essential environment variables are not set.
    """
    load_dotenv()

    provider = os.environ.get("LOGIC_FABRICATOR_PROVIDER")
    model = os.environ.get("LOGIC_FABRICATOR_MODEL")
    api_key = os.environ.get("LOGIC_FABRICATOR_API_KEY")
    base_url = os.environ.get("LOGIC_FABRICATOR_BASE_URL")  # Optional

    if not provider:
        raise ValueError("Configuration error: LOGIC_FABRICATOR_PROVIDER is not set.")
    if not model:
        raise ValueError("Configuration error: LOGIC_FABRICATOR_MODEL is not set.")
    if not api_key:
        raise ValueError("Configuration error: LOGIC_FABRICATOR_API_KEY is not set.")

    return Config(
        llm_provider=provider,
        llm_model=model,
        llm_api_key=api_key,
        llm_base_url=base_url,
    )