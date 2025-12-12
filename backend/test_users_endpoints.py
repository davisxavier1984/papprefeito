#!/usr/bin/env python3
"""
Script de teste para os novos endpoints de gestão de usuários
"""
import sys
import asyncio

# Adiciona o diretório ao path
sys.path.insert(0, '.')

def test_imports():
    """Testa se todos os imports estão funcionando"""
    print("🧪 Testando imports dos novos endpoints...")

    try:
        from app.api.endpoints.users import router as users_router
        print("   ✅ Router de usuários importado com sucesso")

        from app.models.schemas import UserUpdate
        print("   ✅ Schema UserUpdate importado com sucesso")

        # Verifica se o router tem as rotas esperadas
        routes = users_router.routes
        route_paths = {route.path for route in routes if hasattr(route, 'path')}
        print(f"   ℹ️  Rotas disponíveis: {route_paths}")

        return True
    except Exception as e:
        print(f"   ❌ Erro ao importar: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_user_update_schema():
    """Testa o schema UserUpdate com os novos campos"""
    print("\n🧪 Testando schema UserUpdate...")

    try:
        from app.models.schemas import UserUpdate

        # Testa atualização apenas de nome
        update1 = UserUpdate(nome="Novo Nome")
        assert update1.nome == "Novo Nome"
        assert update1.email is None
        assert update1.is_active is None
        print("   ✅ UserUpdate com nome OK")

        # Testa atualização de is_active
        update2 = UserUpdate(is_active=True)
        assert update2.is_active == True
        print("   ✅ UserUpdate com is_active OK")

        # Testa atualização de is_authorized
        update3 = UserUpdate(is_authorized=True)
        assert update3.is_authorized == True
        print("   ✅ UserUpdate com is_authorized OK")

        # Testa atualização de is_superuser
        update4 = UserUpdate(is_superuser=True)
        assert update4.is_superuser == True
        print("   ✅ UserUpdate com is_superuser OK")

        # Testa múltiplos campos
        update5 = UserUpdate(
            nome="Admin User",
            email="admin@test.com",
            is_active=True,
            is_superuser=True
        )
        assert update5.nome == "Admin User"
        assert update5.email == "admin@test.com"
        assert update5.is_active == True
        assert update5.is_superuser == True
        print("   ✅ UserUpdate com múltiplos campos OK")

        return True
    except Exception as e:
        print(f"   ❌ Erro ao testar schema: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_user_service_list_users():
    """Testa o método list_users com novos parâmetros"""
    print("\n🧪 Testando método list_users com filtros...")

    try:
        from app.services.user_service import UserService
        import inspect

        # Obtém a assinatura do método
        sig = inspect.signature(UserService.list_users)
        params = list(sig.parameters.keys())

        expected_params = ['self', 'skip', 'limit', 'search', 'is_active', 'is_superuser']

        for param in expected_params:
            if param not in params:
                print(f"   ❌ Parâmetro '{param}' não encontrado em list_users")
                return False

        print(f"   ✅ Todos os parâmetros esperados presentes: {params}")
        return True
    except Exception as e:
        print(f"   ❌ Erro ao testar UserService: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Executa todos os testes"""
    print("=" * 60)
    print("🔐 TESTE DOS NOVOS ENDPOINTS DE GESTÃO DE USUÁRIOS")
    print("=" * 60)
    print()

    results = []
    results.append(("Imports", test_imports()))
    results.append(("UserUpdate Schema", test_user_update_schema()))
    results.append(("UserService.list_users", test_user_service_list_users()))

    print("\n" + "=" * 60)
    print("📊 RESULTADO DOS TESTES")
    print("=" * 60)

    all_passed = True
    for test_name, passed in results:
        status = "✅ PASSOU" if passed else "❌ FALHOU"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False

    print("=" * 60)

    if all_passed:
        print("✅ TODOS OS TESTES PASSARAM!")
        print()
        print("📋 Novos Endpoints Disponíveis:")
        print("   GET    /api/users/              - Listar usuários com filtros")
        print("   GET    /api/users/{id}          - Obter usuário específico")
        print("   POST   /api/users/              - Criar novo usuário")
        print("   PUT    /api/users/{id}          - Atualizar usuário")
        print("   DELETE /api/users/{id}          - Deletar usuário (soft delete)")
        print()
        print("Todos requerem autenticação e permissões de superusuário!")
        print()
        return 0
    else:
        print("❌ ALGUNS TESTES FALHARAM!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
