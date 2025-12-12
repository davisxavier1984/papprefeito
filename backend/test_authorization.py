#!/usr/bin/env python3
"""
Script de teste para o sistema de autorização de usuários
"""
import asyncio
import sys
from datetime import datetime

# Adiciona o diretório ao path
sys.path.insert(0, '.')

from app.models.schemas import User


def test_user_schema():
    """Testa o schema User com o novo campo is_authorized"""
    print("🧪 Testando schema User...")

    # Cria um usuário de teste
    user = User(
        id="test_123",
        email="test@example.com",
        nome="Usuário Teste",
        is_active=True,
        is_authorized=False,  # Novo campo
        is_superuser=False,
        created_at=datetime.utcnow()
    )

    # Verifica os campos
    assert user.id == "test_123"
    assert user.email == "test@example.com"
    assert user.nome == "Usuário Teste"
    assert user.is_active == True
    assert user.is_authorized == False  # Verifica novo campo
    assert user.is_superuser == False

    print("   ✅ Schema User OK")
    print(f"   - Campo is_authorized presente: {hasattr(user, 'is_authorized')}")
    print(f"   - Valor padrão is_authorized: {user.is_authorized}")
    print()


def test_user_authorization_schema():
    """Testa os novos schemas de autorização"""
    from app.models.schemas import UserAuthorizationUpdate, UserListResponse

    print("🧪 Testando schemas de autorização...")

    # Testa UserAuthorizationUpdate
    auth_update = UserAuthorizationUpdate(is_authorized=True)
    assert auth_update.is_authorized == True
    print("   ✅ UserAuthorizationUpdate OK")

    # Testa UserListResponse
    user = User(
        id="test_456",
        email="test2@example.com",
        nome="Usuário Teste 2",
        is_active=True,
        is_authorized=True,
        is_superuser=False,
        created_at=datetime.utcnow()
    )

    user_list = UserListResponse(total=1, users=[user])
    assert user_list.total == 1
    assert len(user_list.users) == 1
    assert user_list.users[0].is_authorized == True
    print("   ✅ UserListResponse OK")
    print()


def test_imports():
    """Testa se todos os imports estão funcionando"""
    print("🧪 Testando imports...")

    try:
        from app.services.user_service import UserService
        print("   ✅ UserService importado com sucesso")

        from app.api.endpoints.auth import router
        print("   ✅ Router de autenticação importado com sucesso")

        from app.core.dependencies import get_current_user
        print("   ✅ Dependências importadas com sucesso")

        print()
        return True
    except Exception as e:
        print(f"   ❌ Erro ao importar: {e}")
        print()
        return False


def main():
    """Executa todos os testes"""
    print("=" * 60)
    print("🔐 TESTE DO SISTEMA DE AUTORIZAÇÃO DE USUÁRIOS")
    print("=" * 60)
    print()

    try:
        # Testa schemas
        test_user_schema()
        test_user_authorization_schema()

        # Testa imports
        if not test_imports():
            sys.exit(1)

        print("=" * 60)
        print("✅ TODOS OS TESTES PASSARAM!")
        print("=" * 60)
        print()
        print("📋 Próximos passos:")
        print("   1. Execute: python3 add_authorization_field.py")
        print("   2. Execute: python3 create_first_superuser.py")
        print("   3. Inicie o servidor: uvicorn app.main:app --reload")
        print("   4. Acesse a documentação: http://localhost:8000/docs")
        print()

    except AssertionError as e:
        print(f"❌ ERRO: Teste falhou - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ ERRO INESPERADO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
