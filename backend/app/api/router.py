"""
Router principal da API que inclui todos os endpoints
"""
from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_authorized_user

from app.api.endpoints import municipios, financiamento, municipios_editados, relatorios, edicoes, auth, users

# Router principal
api_router = APIRouter()

# Rotas de dados exigem usuário ativo e autorizado
requer_autorizacao = [Depends(get_current_authorized_user)]

# Incluir routers dos endpoints
api_router.include_router(
    municipios.router,
    prefix="/municipios",
    tags=["Municípios"]
)

api_router.include_router(
    financiamento.router,
    prefix="/financiamento",
    dependencies=requer_autorizacao,
    tags=["Financiamento"]
)

api_router.include_router(
    municipios_editados.router,
    prefix="/municipios-editados",
    dependencies=requer_autorizacao,
    tags=["Dados Editados"]
)

api_router.include_router(
    relatorios.router,
    prefix="/relatorios",
    dependencies=requer_autorizacao,
    tags=["Relatórios"]
)

api_router.include_router(
    edicoes.router,
    prefix="",
    dependencies=requer_autorizacao,
    tags=["Edições"]
)

# Endpoints de autenticação
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Autenticação"]
)

# Endpoints de gestão de usuários (CRUD completo)
api_router.include_router(
    users.router,
    prefix="/users",
    tags=["Gestão de Usuários"]
)
