"""
Dependências do FastAPI para autenticação e autorização
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings
from app.core.security import decode_token, verify_token_type
from app.models.schemas import User, TokenPayload
from app.services.user_service import UserService

# Esquema de segurança Bearer
security = HTTPBearer()


def get_user_service() -> UserService:
    """
    Factory function para criar instância do UserService

    Returns:
        Instância do UserService
    """
    return UserService()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user_service: UserService = Depends(get_user_service)
) -> User:
    """
    Dependência para obter o usuário atual a partir do token JWT

    Args:
        credentials: Credenciais do cabeçalho Authorization
        user_service: Serviço de usuários

    Returns:
        Usuário autenticado

    Raises:
        HTTPException: Se o token for inválido ou o usuário não for encontrado
    """
    token = credentials.credentials

    # Decodifica o token
    payload = decode_token(token, settings.SECRET_KEY, settings.ALGORITHM)

    # Verifica se é um token de acesso
    if not verify_token_type(payload, "access"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tipo de token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Obtém o ID do usuário do payload
    user_id: Optional[str] = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não foi possível validar as credenciais",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Busca o usuário no banco de dados
    user = await user_service.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependência para obter o usuário atual ativo

    Args:
        current_user: Usuário autenticado

    Returns:
        Usuário autenticado e ativo

    Raises:
        HTTPException: Se o usuário não estiver ativo
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo"
        )
    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Dependência para obter o usuário atual que seja superusuário

    Args:
        current_user: Usuário autenticado e ativo

    Returns:
        Usuário autenticado, ativo e superusuário

    Raises:
        HTTPException: Se o usuário não for superusuário
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissões insuficientes"
        )
    return current_user


def verify_refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    Verifica e extrai o user_id de um refresh token

    Args:
        credentials: Credenciais do cabeçalho Authorization

    Returns:
        ID do usuário extraído do token

    Raises:
        HTTPException: Se o token for inválido ou não for um refresh token
    """
    token = credentials.credentials

    # Decodifica o token
    payload = decode_token(token, settings.SECRET_KEY, settings.ALGORITHM)

    # Verifica se é um token de renovação
    if not verify_token_type(payload, "refresh"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tipo de token inválido. Use um refresh token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Obtém o ID do usuário do payload
    user_id: Optional[str] = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não foi possível validar as credenciais",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_id
