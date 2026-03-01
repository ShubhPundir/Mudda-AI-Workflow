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

    # LLM Configuration
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "gemini")  # gemini, bedrock
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    # Email Configuration
    EMAIL_PROVIDER: str = os.getenv("EMAIL_PROVIDER", "brevo")  # resend, aws_ses, sendgrid
    EMAIL_FROM_ADDRESS: str = os.getenv("EMAIL_FROM_ADDRESS", "project.mudda@gmail.com")
    EMAIL_FROM_NAME: str = os.getenv("EMAIL_FROM_NAME", "Mudda AI - Automated Email")

    # Resend Email
    RESEND_API_KEY: str = os.getenv("RESEND_API_KEY", "")
    RESEND_EMAIL_FROM_ADDRESS: str = os.getenv("RESEND_EMAIL_FROM_ADDRESS", "")
    RESEND_EMAIL_FROM_NAME: str = os.getenv("RESEND_EMAIL_FROM_NAME", "Mudda AI - Automated Email (Resend)")

    # AWS SES
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    AWS_REGION: str = os.getenv("AWS_REGION", "ap-south-1")

    # S3 Configuration
    S3_BUCKET_NAME: str = os.getenv("S3_BUCKET_NAME", "mudda-documents")
    
    # SendGrid
    SENDGRID_API_KEY: str = os.getenv("SENDGRID_API_KEY", "")

    # Brevo
    BREVO_API_KEY: str = os.getenv("BREVO_API_KEY", "")

    # Temporal
    TEMPORAL_HOST: str = os.getenv("TEMPORAL_HOST", "localhost:7233")
    TEMPORAL_NAMESPACE: str = os.getenv("TEMPORAL_NAMESPACE", "default")

    # API
    API_HOST: str = os.getenv("API_HOST", "127.0.0.1")
    API_PORT: int = int(os.getenv("API_PORT", "8081"))

    # CORS
    CORS_ORIGINS: list = ["*"]

    # RAG Service
    RAG_SERVICE_URL: str = os.getenv("RAG_SERVICE_URL", "http://localhost:8082")
    RAG_PROTOCOL: str = os.getenv("RAG_PROTOCOL", "http")  # "http" or "grpc"
    RAG_GRPC_ADDRESS: str = os.getenv("RAG_GRPC_ADDRESS", "localhost:8082")
    RAG_NAMESPACE: str = os.getenv("RAG_NAMESPACE", "waterworks-department")  # Default namespace for policy retrieval

    # Application
    APP_NAME: str = "Mudda AI Workflow System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True



settings = Settings()
