from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    model_name: str = os.getenv("MODEL_NAME", "gpt-3.5-turbo")
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    """
    Create and cache settings instance.
    """
    return Settings() 