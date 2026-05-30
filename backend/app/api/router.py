"""
Router principal da API que inclui todos os endpoints
"""
from fastapi import APIRouter, Depends

from app.api.endpoints import municipios, financiamento, municipios_editados, relatorios, edicoes, auth, users
from app.core.dependencies import get_current_authorized_user

# Router principal
api_router = APIRouter()

# Login obrigatório (usuário ativo e autorizado) nos endpoints de negócio
_auth_required = [Depends(get_current_authorized_user)]

# Incluir routers dos endpoints
api_router.include_router(
    municipios.router,
    prefix="/municipios",
    tags=["Municípios"],
    dependencies=_auth_required,
)

api_router.include_router(
    financiamento.router,
    prefix="/financiamento",
    tags=["Financiamento"],
    dependencies=_auth_required,
)

api_router.include_router(
    municipios_editados.router,
    prefix="/municipios-editados",
    tags=["Dados Editados"],
    dependencies=_auth_required,
)

api_router.include_router(
    relatorios.router,
    prefix="/relatorios",
    tags=["Relatórios"],
    dependencies=_auth_required,
)

api_router.include_router(
    edicoes.router,
    prefix="",
    tags=["Edições"],
    dependencies=_auth_required,
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
