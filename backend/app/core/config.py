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
    DATABASE_URL: str = "postgresql://user:password@localhost/papprefeito"

    # JSON Data Files (compatibilidade com sistema atual)
    DATA_CACHE_FILE: str = "data_cache_papprefeito.json"
    EDITED_DATA_FILE: str = "municipios_editados.json"

    # Appwrite Configuration
    APPWRITE_ENDPOINT: str = "https://cloud.appwrite.io/v1"
    APPWRITE_PROJECT_ID: str = "68dc49bf000cebd54b85"
    APPWRITE_API_KEY: Optional[str] = None
    APPWRITE_DATABASE_ID: str = "papprefeito_db"
    APPWRITE_COLLECTION_EDICOES_ID: str = "edicoes_municipios"

    # Paginação
    DEFAULT_PAGE_SIZE: int = 50
    MAX_PAGE_SIZE: int = 100

    class Config:
        env_file = ".env"
        case_sensitive = True


# Instância global das configurações
settings = Settings()
