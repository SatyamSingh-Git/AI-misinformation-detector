from pydantic_settings import BaseSettings
from functools import lru_cache
from pydantic import Field 

class Settings(BaseSettings):
    """
    Manages application-wide settings.
    Settings are loaded from environment variables. If an env var is not found,
    the default value specified here is used.
    """
    # Application metadata
    PROJECT_NAME: str = "Misinformation Detector API"
    DATABASE_URL: str = "sqlite:///./misinformation.db"
    API_V1_STR: str = "/api/v1"



    # CORS (Cross-Origin Resource Sharing) configuration
    # This determines which frontend origins are allowed to communicate with the API.
    # For development, a wildcard ("*") is often used.
    # For production, you would list specific domains: ["https://your-frontend.com"]
    BACKEND_CORS_ORIGINS: list[str] = ["*"]

    GOOGLE_API_KEY: str = Field(..., env="GOOGLE_API_KEY")

    class Config:
        # This tells Pydantic to look for environment variables in a .env file.
        # Useful for local development.
        env_file = ".env"
        case_sensitive = True

# The @lru_cache decorator caches the Settings object, so it's created only once.
# This is an efficient way to access settings throughout the application.
@lru_cache()
def get_settings():
    return Settings()

# You can create a .env file in the root of your `backend/` directory for local overrides:
# PROJECT_NAME="My Awesome Misinfo API"
