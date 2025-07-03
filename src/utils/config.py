from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache
import os

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    # Default LLM provider
    default_llm_provider: str = os.getenv("DEFAULT_LLM_PROVIDER", "openai")
    
    # OpenAI settings
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model_name: str = os.getenv("OPENAI_MODEL_NAME", "gpt-4o")
    
    # Google Gemini settings
    gemini_api_key: Optional[str] = os.getenv("GEMINI_API_KEY")
    gemini_model_name: str = os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-pro")
    
    # Anthropic Claude settings
    anthropic_api_key: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    anthropic_model_name: str = os.getenv("ANTHROPIC_MODEL_NAME", "claude-3-opus-20240229")
    
    # Default parameter settings
    max_tokens_default: int = int(os.getenv("MAX_TOKENS_DEFAULT", "1000"))
    temperature_default: float = float(os.getenv("TEMPERATURE_DEFAULT", "0.7"))
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8"
    }

@lru_cache()
def get_settings() -> Settings:
    """Create and cache settings instance."""
    return Settings() 