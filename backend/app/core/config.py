"""
Configuration management for the FastAPI application.
Uses pydantic-settings for environment variable handling.
"""

from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    # App settings
    app_name: str = Field(default="LifeTime AI", description="Application name")
    app_version: str = Field(default="0.1.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")

    # Server settings
    host: str = Field(default="127.0.0.1", description="Server host")
    port: int = Field(default=8000, description="Server port")
    reload: bool = Field(default=False, description="Auto-reload on code changes")

    # Database settings
    database_url: str = Field(
        default="sqlite:///./lifetime.db", description="Database connection URL"
    )
    database_echo: bool = Field(
        default=False, description="Echo SQL queries to console"
    )
    database_encrypt: bool = Field(
        default=False, description="Enable database encryption with SQLCipher"
    )
    database_key: str = Field(
        default="your-database-encryption-key-change-in-production",
        description="Database encryption key for SQLCipher",
    )
    database_pool_size: int = Field(
        default=10, description="Database connection pool size"
    )
    database_max_overflow: int = Field(
        default=20, description="Database connection pool max overflow"
    )

    # CORS settings
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        description="Allowed CORS origins",
    )
    cors_credentials: bool = Field(
        default=True, description="Allow credentials in CORS requests"
    )
    cors_methods: list[str] = Field(
        default=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        description="Allowed CORS methods",
    )
    cors_headers: list[str] = Field(default=["*"], description="Allowed CORS headers")

    # Security settings
    secret_key: str = Field(
        default="your-secret-key-change-in-production",
        description="Secret key for JWT tokens",
    )
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(
        default=30, description="Access token expiration time in minutes"
    )

    # Logging settings
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(
        default="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        description="Log format string",
    )

    # API settings
    api_v1_prefix: str = Field(default="/api/v1", description="API v1 prefix")
    docs_url: Optional[str] = Field(
        default="/docs", description="Swagger UI docs URL (None to disable)"
    )
    redoc_url: Optional[str] = Field(
        default="/redoc", description="ReDoc docs URL (None to disable)"
    )
    openapi_url: Optional[str] = Field(
        default="/openapi.json", description="OpenAPI JSON URL (None to disable)"
    )


# Global settings instance
settings = Settings()
