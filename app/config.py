import os
from pydantic import BaseSettings

# Environment Variables

class Settings(BaseSettings):
    DB_USERNAME: str
    DB_PASSWORD: str
    QUERY_LIMIT: int
    USER_LIMIT: int

    class Config:
        env_file = ".env"


settings = Settings()
