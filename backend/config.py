"""
Configuration settings for the application
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings"""

    # Database
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    DB_NAME: str = os.getenv("DB_NAME", "mudda_ai_db")
    DB_USER: str = os.getenv("DB_USER", "username")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "password")

    # Gemini AI
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    # Resend Email
    RESEND_API_KEY: str = os.getenv("RESEND_API_KEY", "")
    EMAIL_FROM_ADDRESS: str = os.getenv("EMAIL_FROM_ADDRESS", "noreply@example.com")
    EMAIL_FROM_NAME: str = os.getenv("EMAIL_FROM_NAME", "Mudda AI")

    # Temporal
    TEMPORAL_HOST: str = os.getenv("TEMPORAL_HOST", "localhost:7233")
    TEMPORAL_NAMESPACE: str = os.getenv("TEMPORAL_NAMESPACE", "default")

    # API
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8081"))

    # CORS
    CORS_ORIGINS: list = ["*"]

    # Application
    APP_NAME: str = "Mudda AI Workflow System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True


settings = Settings()
