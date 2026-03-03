from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    # Database - use PostgreSQL in production
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/cleaning"
    )
    
    # Redis Cache
    REDIS_ENABLED: bool = os.getenv("REDIS_ENABLED", "false").lower() == "true"
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Upload
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 80
    
    class Config:
        env_file = ".env"


settings = Settings()
