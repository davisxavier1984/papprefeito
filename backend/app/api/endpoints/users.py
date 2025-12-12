"""
Endpoints para Gestão Completa de Usuários (CRUD)
Apenas administradores (superusuários) podem acessar estes endpoints
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.models.schemas import (
    User,
    UserCreate,
    UserUpdate,
    UserListResponse,
    ResponseBase
)
from app.services.user_service import UserService
from app.core.dependencies import (
    get_current_superuser,
    get_user_service
)
from app.utils.logger import logger

router = APIRouter()


@router.get(
    "/",
    response_model=UserListResponse,
    summary="Listar usuários",
    description="Lista todos os usuários cadastrados com paginação (apenas superusuários)"
)
async def list_users(
    skip: int = Query(0, ge=0, description="Número de registros a pular"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros"),
    search: Optional[str] = Query(None, description="Buscar por nome ou email"),
    is_active: Optional[bool] = Query(None, description="Filtrar por status ativo"),
    is_superuser: Optional[bool] = Query(None, description="Filtrar por superusuário"),
    current_user: User = Depends(get_current_superuser),
    user_service: UserService = Depends(get_user_service)
):
    """
    Lista usuários com filtros opcionais.

    Requer permissões de administrador.

    - **skip**: Número de registros a pular (paginação)
    - **limit**: Número máximo de registros (máx: 1000)
    - **search**: Buscar por nome ou email
    - **is_active**: Filtrar por status ativo/inativo
    - **is_superuser**: Filtrar por tipo de usuário
    """
    try:
        users = await user_service.list_users(
            skip=skip,
            limit=limit,
            search=search,
            is_active=is_active,
            is_superuser=is_superuser
        )
        logger.info(f"Admin {current_user.email} listou {len(users)} usuários")
        return UserListResponse(
            total=len(users),
            users=users
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao listar usuários: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao listar usuários"
        )


@router.get(
    "/{user_id}",
    response_model=User,
    summary="Obter detalhes do usuário",
    description="Obtém informações completas de um usuário específico"
)
async def get_user(
    user_id: str,
    current_user: User = Depends(get_current_superuser),
    user_service: UserService = Depends(get_user_service)
):
    """
    Obtém detalhes de um usuário específico.

    Requer permissões de administrador.

    - **user_id**: ID do usuário
    """
    try:
        user = await user_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
        logger.info(f"Admin {current_user.email} obteve detalhes do usuário {user.email}")
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter detalhes do usuário: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao obter detalhes do usuário"
        )


@router.post(
    "/",
    response_model=User,
    status_code=status.HTTP_201_CREATED,
    summary="Criar novo usuário",
    description="Cria um novo usuário no sistema (apenas superusuários)"
)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(get_current_superuser),
    user_service: UserService = Depends(get_user_service)
):
    """
    Cria um novo usuário no sistema.

    Requer permissões de administrador.

    - **email**: Email do usuário (único)
    - **nome**: Nome completo
    - **password**: Senha (mínimo 8 caracteres, maiúscula, minúscula, número)
    """
    try:
        user = await user_service.create_user(user_data)
        logger.info(f"Admin {current_user.email} criou novo usuário: {user.email}")
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar usuário: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao criar usuário"
        )


@router.put(
    "/{user_id}",
    response_model=User,
    summary="Atualizar usuário",
    description="Atualiza informações de um usuário (apenas superusuários)"
)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_superuser),
    user_service: UserService = Depends(get_user_service)
):
    """
    Atualiza informações de um usuário existente.

    Requer permissões de administrador.

    - **user_id**: ID do usuário
    - **nome**: Novo nome (opcional)
    - **email**: Novo email (opcional)
    - **is_active**: Status ativo/inativo (opcional)
    """
    try:
        # Verifica se o usuário existe
        user = await user_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )

        # Atualiza o usuário
        updated_user = await user_service.update_user(user_id, user_data)
        logger.info(f"Admin {current_user.email} atualizou usuário {user.email}")
        return updated_user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar usuário: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar usuário"
        )


@router.delete(
    "/{user_id}",
    response_model=ResponseBase,
    summary="Deletar usuário",
    description="Deleta um usuário (soft delete - marca como inativo)"
)
async def delete_user(
    user_id: str,
    current_user: User = Depends(get_current_superuser),
    user_service: UserService = Depends(get_user_service)
):
    """
    Deleta um usuário (soft delete).

    Requer permissões de administrador.

    - **user_id**: ID do usuário

    Nota: O usuário será marcado como inativo mas seus dados serão preservados.
    """
    # Impede que o admin delete a si mesmo
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Você não pode deletar sua própria conta"
        )

    try:
        # Verifica se o usuário existe
        user = await user_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )

        # Deleta o usuário
        await user_service.delete_user(user_id)
        logger.info(f"Admin {current_user.email} deletou usuário {user.email}")
        return ResponseBase(
            success=True,
            message="Usuário deletado com sucesso"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao deletar usuário: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao deletar usuário"
        )
