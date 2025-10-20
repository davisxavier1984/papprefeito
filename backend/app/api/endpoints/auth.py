"""
Endpoints de autenticação
"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer

from app.models.schemas import (
    Token,
    LoginRequest,
    RefreshTokenRequest,
    UserCreate,
    User,
    UserUpdate,
    UserPasswordChange,
    ResponseBase
)
from app.services.user_service import UserService
from app.core.security import create_access_token, create_refresh_token
from app.core.dependencies import (
    get_current_active_user,
    verify_refresh_token,
    get_current_superuser,
    get_user_service
)
from app.core.config import settings
from app.utils.logger import logger

router = APIRouter()
security = HTTPBearer()


@router.post(
    "/register",
    response_model=User,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar novo usuário",
    description="Cria uma nova conta de usuário no sistema"
)
async def register(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service)
):
    """
    Registra um novo usuário.

    - **email**: Email do usuário (único)
    - **nome**: Nome completo
    - **password**: Senha (mínimo 8 caracteres, deve conter maiúscula, minúscula e número)
    """
    try:
        user = await user_service.create_user(user_data)
        logger.info(f"Novo usuário registrado: {user.email}")
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao registrar usuário: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao registrar usuário"
        )


@router.post(
    "/login",
    response_model=Token,
    summary="Login",
    description="Autentica um usuário e retorna tokens de acesso"
)
async def login(
    credentials: LoginRequest,
    user_service: UserService = Depends(get_user_service)
):
    """
    Autentica um usuário com email e senha.

    - **email**: Email do usuário
    - **password**: Senha do usuário

    Retorna:
    - **access_token**: Token JWT para autenticação
    - **refresh_token**: Token para renovação
    - **token_type**: Tipo do token (bearer)
    - **expires_in**: Tempo de expiração em segundos
    """
    # Autentica o usuário
    user = await user_service.authenticate_user(
        credentials.email,
        credentials.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo"
        )

    # Cria tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    access_token = create_access_token(
        subject=user.id,
        secret_key=settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
        expires_delta=access_token_expires
    )

    refresh_token = create_refresh_token(
        subject=user.id,
        secret_key=settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
        expires_delta=refresh_token_expires
    )

    logger.info(f"Login bem-sucedido: {user.email}")

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post(
    "/refresh",
    response_model=Token,
    summary="Renovar token",
    description="Renova o access token usando um refresh token válido"
)
async def refresh_token(
    user_id: str = Depends(verify_refresh_token),
    user_service: UserService = Depends(get_user_service)
):
    """
    Renova o access token usando um refresh token válido.

    Requer um refresh token válido no header Authorization.

    Retorna novos tokens de acesso e renovação.
    """
    # Busca o usuário
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo"
        )

    # Cria novos tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    access_token = create_access_token(
        subject=user.id,
        secret_key=settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
        expires_delta=access_token_expires
    )

    new_refresh_token = create_refresh_token(
        subject=user.id,
        secret_key=settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
        expires_delta=refresh_token_expires
    )

    logger.info(f"Token renovado para usuário: {user.email}")

    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.get(
    "/me",
    response_model=User,
    summary="Obter perfil atual",
    description="Retorna os dados do usuário autenticado"
)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user)
):
    """
    Retorna os dados do usuário autenticado.

    Requer autenticação.
    """
    return current_user


@router.put(
    "/me",
    response_model=User,
    summary="Atualizar perfil",
    description="Atualiza os dados do usuário autenticado"
)
async def update_current_user_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service)
):
    """
    Atualiza os dados do usuário autenticado.

    Requer autenticação.

    - **nome**: Novo nome (opcional)
    - **email**: Novo email (opcional)
    """
    try:
        updated_user = await user_service.update_user(current_user.id, user_data)
        logger.info(f"Perfil atualizado: {current_user.email}")
        return updated_user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar perfil: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar perfil"
        )


@router.post(
    "/me/change-password",
    response_model=ResponseBase,
    summary="Alterar senha",
    description="Altera a senha do usuário autenticado"
)
async def change_password(
    password_data: UserPasswordChange,
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service)
):
    """
    Altera a senha do usuário autenticado.

    Requer autenticação.

    - **current_password**: Senha atual
    - **new_password**: Nova senha (mínimo 8 caracteres, deve conter maiúscula, minúscula e número)
    """
    try:
        await user_service.update_password(
            current_user.id,
            password_data.current_password,
            password_data.new_password
        )
        logger.info(f"Senha alterada: {current_user.email}")
        return ResponseBase(
            success=True,
            message="Senha alterada com sucesso"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao alterar senha: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao alterar senha"
        )


@router.delete(
    "/me",
    response_model=ResponseBase,
    summary="Desativar conta",
    description="Desativa a conta do usuário autenticado"
)
async def delete_current_user(
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service)
):
    """
    Desativa a conta do usuário autenticado.

    Requer autenticação.

    A conta será marcada como inativa e não poderá mais fazer login.
    """
    try:
        await user_service.delete_user(current_user.id)
        logger.info(f"Conta desativada: {current_user.email}")
        return ResponseBase(
            success=True,
            message="Conta desativada com sucesso"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao desativar conta: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao desativar conta"
        )


@router.post(
    "/logout",
    response_model=ResponseBase,
    summary="Logout",
    description="Invalida a sessão do usuário (no cliente)"
)
async def logout(
    current_user: User = Depends(get_current_active_user)
):
    """
    Logout do usuário.

    Requer autenticação.

    Nota: Como estamos usando JWT stateless, o logout deve ser implementado
    no cliente descartando os tokens. Este endpoint serve apenas para
    validar o token e registrar o logout.
    """
    logger.info(f"Logout: {current_user.email}")
    return ResponseBase(
        success=True,
        message="Logout realizado com sucesso"
    )
