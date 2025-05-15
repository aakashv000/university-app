import os
from typing import List, Union, Dict, Any
from pydantic import BaseSettings, PostgresDsn, validator

class Settings(BaseSettings):
    PROJECT_NAME: str = "University App"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = "YOUR_SECRET_KEY_HERE"  # In production, use a secure random key
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Database settings
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "university_app")
    SQLALCHEMY_DATABASE_URI: Union[PostgresDsn, str] = ""

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: str, values: Dict[str, Any]) -> Any:
        if isinstance(v, str) and v != "":
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
