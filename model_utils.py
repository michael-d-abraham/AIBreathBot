"""Model initialization utilities for the Breathing Exercise Chatbot."""

import os
import dotenv
from smolagents import OpenAIServerModel


# Global state for environment loading
g_dotenv_loaded = False


def getenv(variable: str) -> str:
    """Load and return environment variable."""
    global g_dotenv_loaded
    if not g_dotenv_loaded:
        g_dotenv_loaded = True
        dotenv.load_dotenv()
    return os.getenv(variable)


def get_api_key(key_name: str) -> str:
    """Get API key from environment with validation."""
    api_key = getenv(key_name)
    if not api_key:
        raise ValueError(
            f"{key_name} not set. "
            f"Create a .env file with {key_name}=your_api_key"
        )
    return api_key


def google_build_reasoning_model(model_id: str = "gemini-2.5-flash") -> OpenAIServerModel:
    """Build and return a Gemini model instance."""
    api_key = get_api_key("GEMINI_API_KEY")
    api_base = "https://generativelanguage.googleapis.com/v1beta/openai/"
    
    return OpenAIServerModel(
        model_id=model_id,
        api_base=api_base,
        api_key=api_key,
        client_kwargs={"max_retries": 8}
    )
