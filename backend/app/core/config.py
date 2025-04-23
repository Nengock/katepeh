from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List

class Settings(BaseSettings):
    # API Settings
    PROJECT_NAME: str = "KTP Recognition API"
    API_V1_STR: str = "/api"
    
    # CORS Settings
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",  # Vite dev server
        "http://localhost:4173"   # Vite preview
    ]
    
    # Security Settings
    MAX_CONTENT_LENGTH: int = 10 * 1024 * 1024  # 10MB max file size
    ALLOWED_IMAGE_TYPES: List[str] = ["image/jpeg", "image/png"]
    
    # ML Model Settings
    MODEL_CONFIDENCE_THRESHOLD: float = 0.8
    USE_GPU: bool = True
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    model_config = {
        "case_sensitive": True,
        "env_file": ".env"
    }

@lru_cache()
def get_settings() -> Settings:
    """Create cached instance of settings."""
    return Settings()