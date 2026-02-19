"""
Model Configuration
-------------------

Centralized model configuration for all agents.
"""

from os import getenv

from agno.models.litellm import LiteLLMOpenAI

# Model IDs
MODEL_ID = getenv("MODEL_ID", "gpt-5-mini")
EMBEDDING_MODEL_ID = getenv("EMBEDDING_MODEL_ID", "text-embedding-3-small")
EMBEDDING_DIMENSIONS = int(getenv("EMBEDDING_DIMENSIONS", "1536"))

# LiteLLM proxy config
LITELLM_BASE_URL = getenv("LITELLM_BASE_URL", "http://localhost:4000/v1")
LITELLM_API_KEY = getenv("LITELLM_API_KEY", "")


def get_model(model_id: str | None = None) -> LiteLLMOpenAI:
    """Create a LiteLLMOpenAI model instance with standard config."""
    return LiteLLMOpenAI(
        id=model_id or MODEL_ID,
        base_url=LITELLM_BASE_URL,
        api_key=LITELLM_API_KEY,
    )
