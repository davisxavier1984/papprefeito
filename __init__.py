"""
Sistema papprefeito - Consulta de Dados de Financiamento da Saúde

Módulo independente para consulta e visualização de dados da API 
de financiamento da saúde do Ministério da Saúde.
"""

from .utils import (
    consultar_api,
    format_currency,
    load_data_from_json
)

__version__ = "1.0.0"
__author__ = "Sistema papprefeito"

__all__ = [
    "consultar_api",
    "format_currency", 
    "load_data_from_json"
]