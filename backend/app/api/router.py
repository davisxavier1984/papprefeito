"""
Router principal da API que inclui todos os endpoints
"""
from fastapi import APIRouter

from app.api.endpoints import municipios, financiamento, municipios_editados, relatorios

# Router principal
api_router = APIRouter()

# Incluir routers dos endpoints
api_router.include_router(
    municipios.router,
    prefix="/municipios",
    tags=["Municípios"]
)

api_router.include_router(
    financiamento.router,
    prefix="/financiamento",
    tags=["Financiamento"]
)

api_router.include_router(
    municipios_editados.router,
    prefix="/municipios-editados",
    tags=["Dados Editados"]
)

api_router.include_router(
    relatorios.router,
    prefix="/relatorios",
    tags=["Relatórios"]
)
