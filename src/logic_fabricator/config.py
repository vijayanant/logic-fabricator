import os
import logging
import logging.handlers # Import logging.handlers
import structlog
from dataclasses import dataclass
from dotenv import load_dotenv

def configure_logging():
    """Configures structlog for the application."""
    os.makedirs('logs', exist_ok=True) # Ensure logs directory exists
    logging.basicConfig(
        format="%(message)s",
        handlers=[], # Do not add default console handler
        level=logging.INFO,
    )
    structlog.configure(
        processors=[
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"), # Add timestamp
            structlog.processors.StackInfoRenderer(),   # Add stack info
            structlog.processors.format_exc_info,       # Add exception info
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    # File handler for all messages (INFO and above)
    file_formatter = structlog.stdlib.ProcessorFormatter(
        processor=structlog.processors.JSONRenderer(), # Render to JSON for file
        fmt="%(message)s",
    )
    file_handler = logging.handlers.RotatingFileHandler(
        "logs/logic_fabricator.log",
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
    )
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.INFO) # Log INFO and above to file

    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)
    root_logger.setLevel(logging.INFO) # Root logger captures all INFO and above


@dataclass
class Config:
    """Configuration object for the Logic Fabricator, loaded from environment variables."""
    llm_provider: str
    llm_model: str
    llm_api_key: str
    llm_base_url: str | None
    llm_max_attempts: int

def load_config() -> Config:
    """Loads all configuration from environment variables.

    Raises ValueError if essential environment variables are not set.
    """
    load_dotenv()

    provider = os.environ.get("LOGIC_FABRICATOR_PROVIDER")
    model = os.environ.get("LOGIC_FABRICATOR_MODEL")
    api_key = os.environ.get("LOGIC_FABRICATOR_API_KEY")
    base_url = os.environ.get("LOGIC_FABRICATOR_BASE_URL")  # Optional
    max_attempts_str = os.environ.get("LOGIC_FABRICATOR_MAX_ATTEMPTS", "1")

    if not provider:
        raise ValueError("Configuration error: LOGIC_FABRICATOR_PROVIDER is not set.")
    if not model:
        raise ValueError("Configuration error: LOGIC_FABRICATOR_MODEL is not set.")
    if not api_key:
        raise ValueError("Configuration error: LOGIC_FABRICATOR_API_KEY is not set.")

    try:
        max_attempts = int(max_attempts_str)
    except ValueError:
        raise ValueError(
            f"Configuration error: LOGIC_FABRICATOR_MAX_ATTEMPTS must be an integer, but got '{max_attempts_str}'."
        )

    return Config(
        llm_provider=provider,
        llm_model=model,
        llm_api_key=api_key,
        llm_base_url=base_url,
        llm_max_attempts=max_attempts,
    )