"""
Configurações da aplicação
"""
import os
from typing import List, Optional
from pydantic import BaseModel, field_validator
from pydantic_settings import BaseSettings

# Valor placeholder inseguro — proibido em produção (ver validador abaixo)
INSECURE_SECRET_KEY = "your-secret-key-here-change-in-production"


class Settings(BaseSettings):
    """Configurações da aplicação usando pydantic"""

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

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

    # SIAPS — API pública de classificação das equipes (CVAT + Qualidade)
    SIAPS_BASE_URL: str = "https://apisiaps.saude.gov.br"
    SIAPS_TIMEOUT: int = 60
    SIAPS_CACHE_DIR: str = "data/SIAPS"
    SIAPS_CACHE_TTL_DAYS: int = 30  # dado quadrimestral muda raramente

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
    SECRET_KEY: str = INSECURE_SECRET_KEY
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    @field_validator("SECRET_KEY")
    @classmethod
    def _enforce_secure_secret_key(cls, v: str, info) -> str:
        """Falha-rápido: proíbe a SECRET_KEY placeholder em produção."""
        env = str(info.data.get("ENVIRONMENT", "development")).lower()
        if env == "production" and (not v or v == INSECURE_SECRET_KEY):
            raise ValueError(
                "SECRET_KEY insegura em produção. Defina SECRET_KEY no .env/ambiente."
            )
        return v

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


# Instância global das configurações
settings = Settings()
