"""
Configurações da aplicação
"""
import os
from typing import List, Optional
from pydantic import BaseModel
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configurações da aplicação usando pydantic"""

    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "papprefeito API"

    # CORS
    ALLOWED_HOSTS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "https://api-maispap.dasix.site",
        "https://maispap.dasix.site"
    ]

    # External API
    SAUDE_API_BASE_URL: str = "https://relatorioaps-prd.saude.gov.br/financiamento/pagamento"
    SAUDE_API_TIMEOUT: int = 30

    # Cache Configuration
    REDIS_URL: str = "redis://localhost:6379"
    CACHE_TTL: int = 3600  # 1 hora

    # Database Configuration
    SQLITE_URL: str = "sqlite+aiosqlite:///papprefeito.db"

    # JSON Data Files (compatibilidade com sistema atual)
    DATA_CACHE_FILE: str = "data_cache_papprefeito.json"
    EDITED_DATA_FILE: str = "municipios_editados.json"

    # Paginação
    DEFAULT_PAGE_SIZE: int = 50
    MAX_PAGE_SIZE: int = 100

    # Authentication / Security
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


# Instância global das configurações
settings = Settings()
