#!/usr/bin/env python3
"""
Script de teste para o sistema de autenticação
"""
from datetime import timedelta
from app.core.config import settings
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token
)

def test_password_hashing():
    """Testa hash e verificação de senhas"""
    print("\n🔐 Testando hash de senhas...")

    password = "Senha123!"
    hashed = get_password_hash(password)

    print(f"  Senha original: {password}")
    print(f"  Hash gerado: {hashed[:50]}...")

    # Verifica senha correta
    assert verify_password(password, hashed), "❌ Falha ao verificar senha correta"
    print("  ✅ Senha correta verificada com sucesso")

    # Verifica senha incorreta
    assert not verify_password("SenhaErrada", hashed), "❌ Senha incorreta não foi rejeitada"
    print("  ✅ Senha incorreta rejeitada corretamente")


def test_jwt_tokens():
    """Testa criação e decodificação de tokens JWT"""
    print("\n🎫 Testando tokens JWT...")

    user_id = "test_user_123"

    # Cria access token
    access_token = create_access_token(
        subject=user_id,
        secret_key=settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
        expires_delta=timedelta(minutes=30)
    )
    print(f"  Access Token criado: {access_token[:50]}...")

    # Decodifica access token
    payload = decode_token(access_token, settings.SECRET_KEY, settings.ALGORITHM)
    assert payload["sub"] == user_id, "❌ User ID não corresponde"
    assert payload["type"] == "access", "❌ Tipo de token incorreto"
    print(f"  ✅ Access Token decodificado: user_id={payload['sub']}, type={payload['type']}")

    # Cria refresh token
    refresh_token = create_refresh_token(
        subject=user_id,
        secret_key=settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
        expires_delta=timedelta(days=7)
    )
    print(f"  Refresh Token criado: {refresh_token[:50]}...")

    # Decodifica refresh token
    refresh_payload = decode_token(refresh_token, settings.SECRET_KEY, settings.ALGORITHM)
    assert refresh_payload["sub"] == user_id, "❌ User ID não corresponde no refresh token"
    assert refresh_payload["type"] == "refresh", "❌ Tipo de token incorreto"
    print(f"  ✅ Refresh Token decodificado: user_id={refresh_payload['sub']}, type={refresh_payload['type']}")


def test_configuration():
    """Testa as configurações do sistema"""
    print("\n⚙️  Testando configurações...")

    print(f"  SECRET_KEY: {'✅ Configurada' if settings.SECRET_KEY else '❌ Não configurada'}")
    print(f"  ALGORITHM: {settings.ALGORITHM}")
    print(f"  ACCESS_TOKEN_EXPIRE_MINUTES: {settings.ACCESS_TOKEN_EXPIRE_MINUTES}")
    print(f"  REFRESH_TOKEN_EXPIRE_DAYS: {settings.REFRESH_TOKEN_EXPIRE_DAYS}")
    print(f"  APPWRITE_DATABASE_ID: {settings.APPWRITE_DATABASE_ID}")

    assert settings.SECRET_KEY != "your-secret-key-here-change-in-production", \
        "❌ SECRET_KEY padrão ainda está em uso!"
    print("  ✅ SECRET_KEY foi alterada da configuração padrão")


def main():
    """Executa todos os testes"""
    print("=" * 60)
    print("🧪 TESTE DO SISTEMA DE AUTENTICAÇÃO")
    print("=" * 60)

    try:
        test_configuration()
        test_password_hashing()
        test_jwt_tokens()

        print("\n" + "=" * 60)
        print("✅ TODOS OS TESTES PASSARAM COM SUCESSO!")
        print("=" * 60)
        print("\n📝 Próximos passos:")
        print("  1. Configure a collection 'users' no Appwrite (veja APPWRITE_SETUP.md)")
        print("  2. Inicie o backend: uvicorn app.main:app --reload --port 8000")
        print("  3. Acesse a documentação: http://localhost:8000/docs")
        print("  4. Teste o endpoint /api/auth/register")
        print()

    except AssertionError as e:
        print(f"\n❌ ERRO: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ ERRO INESPERADO: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
