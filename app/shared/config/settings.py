# app/shared/config/settings.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Configuración de la aplicación"""

    # Base de datos
    DATABASE_URL: str

    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Email SMTP
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str
    SMTP_PASSWORD: str
    SMTP_FROM_EMAIL: str
    SMTP_FROM_NAME: str = "Sistema de Catering"

    # Aplicación
    APP_NAME: str = "Sistema de Catering"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "https://app.catering.com"]

    # Token de activación
    ACTIVATION_TOKEN_EXPIRE_HOURS: int = 48
    ACTIVATION_BASE_URL: str = "http://localhost:8000/activate"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()