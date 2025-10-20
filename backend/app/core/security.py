"""
Utilitários de segurança para autenticação
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status

# Contexto para hash de senhas usando bcrypt
# bcrypt__default_rounds=12 define custo computacional
# bcrypt__min_rounds=10 e bcrypt__max_rounds=14 para validação
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__default_rounds=12,
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica se a senha em texto plano corresponde ao hash

    Args:
        plain_password: Senha em texto plano
        hashed_password: Hash da senha

    Returns:
        True se a senha corresponde, False caso contrário
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Gera hash da senha usando bcrypt

    Args:
        password: Senha em texto plano

    Returns:
        Hash da senha

    Note:
        bcrypt tem limite de 72 bytes. Senhas mais longas são truncadas.
    """
    # bcrypt tem limite de 72 bytes - trunca se necessário
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password = password_bytes[:72].decode('utf-8', errors='ignore')

    return pwd_context.hash(password)


def create_access_token(
    subject: str,
    secret_key: str,
    algorithm: str = "HS256",
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Cria um token JWT de acesso

    Args:
        subject: Subject do token (geralmente user ID)
        secret_key: Chave secreta para assinar o token
        algorithm: Algoritmo de criptografia (padrão HS256)
        expires_delta: Tempo de expiração do token

    Returns:
        Token JWT codificado
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=30)

    expire = datetime.utcnow() + expires_delta

    to_encode = {
        "sub": subject,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    }

    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt


def create_refresh_token(
    subject: str,
    secret_key: str,
    algorithm: str = "HS256",
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Cria um token JWT de renovação

    Args:
        subject: Subject do token (geralmente user ID)
        secret_key: Chave secreta para assinar o token
        algorithm: Algoritmo de criptografia (padrão HS256)
        expires_delta: Tempo de expiração do token

    Returns:
        Token JWT de renovação codificado
    """
    if expires_delta is None:
        expires_delta = timedelta(days=7)

    expire = datetime.utcnow() + expires_delta

    to_encode = {
        "sub": subject,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    }

    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt


def decode_token(
    token: str,
    secret_key: str,
    algorithm: str = "HS256"
) -> Dict[str, Any]:
    """
    Decodifica e valida um token JWT

    Args:
        token: Token JWT a ser decodificado
        secret_key: Chave secreta para verificar o token
        algorithm: Algoritmo de criptografia (padrão HS256)

    Returns:
        Payload do token decodificado

    Raises:
        HTTPException: Se o token for inválido ou expirado
    """
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não foi possível validar as credenciais",
            headers={"WWW-Authenticate": "Bearer"},
        )


def verify_token_type(payload: Dict[str, Any], expected_type: str) -> bool:
    """
    Verifica se o tipo do token corresponde ao esperado

    Args:
        payload: Payload do token decodificado
        expected_type: Tipo esperado do token ('access' ou 'refresh')

    Returns:
        True se o tipo corresponde, False caso contrário
    """
    token_type = payload.get("type")
    return token_type == expected_type
