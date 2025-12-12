"""
Script de teste completo do fluxo de autenticação
Execute: python test_auth_flow.py
"""
import sys
import asyncio
from pathlib import Path

# Adiciona o diretório backend ao path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_token_type
)
from app.core.config import settings
from app.services.user_service import UserService
from app.models.schemas import UserCreate


async def test_security_functions():
    """Testa funções de segurança (hash, JWT)"""
    print("=" * 60)
    print("1. TESTANDO FUNÇÕES DE SEGURANÇA")
    print("=" * 60)
    print()

    # Teste de hash de senha
    print("1.1 Teste de hash de senha...")
    password = "TesteSenha123!"
    try:
        hashed = get_password_hash(password)
        print(f"   ✓ Hash gerado: {hashed[:30]}...")

        # Verificar senha correta
        if verify_password(password, hashed):
            print("   ✓ Senha verificada corretamente")
        else:
            print("   ✗ Erro: Senha não foi verificada")
            return False

        # Verificar senha incorreta
        if not verify_password("SenhaErrada123!", hashed):
            print("   ✓ Senha incorreta rejeitada corretamente")
        else:
            print("   ✗ Erro: Senha incorreta foi aceita")
            return False

    except Exception as e:
        print(f"   ✗ Erro ao testar hash de senha: {e}")
        return False
    print()

    # Teste de JWT
    print("1.2 Teste de JWT (tokens)...")
    try:
        # Criar access token
        access_token = create_access_token(
            subject="test_user_id",
            secret_key=settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        print(f"   ✓ Access token gerado: {access_token[:30]}...")

        # Criar refresh token
        refresh_token = create_refresh_token(
            subject="test_user_id",
            secret_key=settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        print(f"   ✓ Refresh token gerado: {refresh_token[:30]}...")

        # Decodificar access token
        payload = decode_token(access_token, settings.SECRET_KEY, settings.ALGORITHM)
        if payload['sub'] == "test_user_id" and verify_token_type(payload, "access"):
            print("   ✓ Access token decodificado e validado")
        else:
            print("   ✗ Erro: Access token inválido")
            return False

        # Decodificar refresh token
        payload = decode_token(refresh_token, settings.SECRET_KEY, settings.ALGORITHM)
        if payload['sub'] == "test_user_id" and verify_token_type(payload, "refresh"):
            print("   ✓ Refresh token decodificado e validado")
        else:
            print("   ✗ Erro: Refresh token inválido")
            return False

    except Exception as e:
        print(f"   ✗ Erro ao testar JWT: {e}")
        return False
    print()

    print("✓ Todas as funções de segurança estão funcionando!\n")
    return True


async def test_user_service():
    """Testa o UserService (CRUD de usuários)"""
    print("=" * 60)
    print("2. TESTANDO USERSERVICE (INTEGRAÇÃO COM APPWRITE)")
    print("=" * 60)
    print()

    user_service = UserService()
    test_email = "teste_auth_flow@example.com"

    # Limpar usuário de teste anterior (se existir)
    print("2.1 Limpando usuário de teste anterior...")
    try:
        existing_user = await user_service.get_user_by_email(test_email)
        if existing_user:
            print(f"   ⚠ Usuário de teste já existe (ID: {existing_user.id})")
            # Remove para fazer teste limpo
            await user_service.delete_user(existing_user.id)
            print("   ✓ Usuário de teste anterior removido")
    except Exception as e:
        print(f"   ℹ Nenhum usuário anterior encontrado (ok)")
    print()

    # Teste de criação de usuário
    print("2.2 Criando novo usuário...")
    try:
        user_data = UserCreate(
            email=test_email,
            nome="Usuário de Teste",
            password="SenhaTeste123!"
        )

        created_user = await user_service.create_user(user_data)
        print(f"   ✓ Usuário criado com sucesso!")
        print(f"   ✓ ID: {created_user.id}")
        print(f"   ✓ Email: {created_user.email}")
        print(f"   ✓ Nome: {created_user.nome}")
        print(f"   ✓ Ativo: {created_user.is_active}")
        print(f"   ✓ Superusuário: {created_user.is_superuser}")

        user_id = created_user.id

    except Exception as e:
        print(f"   ✗ Erro ao criar usuário: {e}")
        print("\n   POSSÍVEIS CAUSAS:")
        print("   - Collection 'users' não existe")
        print("   - Atributos da collection incorretos")
        print("   - Permissões insuficientes")
        print("\n   Execute: python test_appwrite_connection.py")
        return False
    print()

    # Teste de autenticação
    print("2.3 Testando autenticação...")
    try:
        # Autenticação com credenciais corretas
        authenticated_user = await user_service.authenticate_user(
            test_email,
            "SenhaTeste123!"
        )

        if authenticated_user:
            print("   ✓ Autenticação com credenciais corretas: SUCESSO")
            print(f"   ✓ Usuário autenticado: {authenticated_user.nome}")
        else:
            print("   ✗ Erro: Autenticação falhou com credenciais corretas")
            return False

        # Autenticação com senha incorreta
        wrong_auth = await user_service.authenticate_user(
            test_email,
            "SenhaErrada123!"
        )

        if not wrong_auth:
            print("   ✓ Autenticação com senha incorreta: REJEITADA (correto)")
        else:
            print("   ✗ Erro: Senha incorreta foi aceita")
            return False

    except Exception as e:
        print(f"   ✗ Erro ao testar autenticação: {e}")
        return False
    print()

    # Teste de busca
    print("2.4 Testando busca de usuário...")
    try:
        # Buscar por ID
        found_user = await user_service.get_user_by_id(user_id)
        if found_user and found_user.id == user_id:
            print(f"   ✓ Busca por ID: SUCESSO")
        else:
            print("   ✗ Erro: Usuário não encontrado por ID")
            return False

        # Buscar por email
        found_user = await user_service.get_user_by_email(test_email)
        if found_user and found_user.email == test_email:
            print(f"   ✓ Busca por email: SUCESSO")
        else:
            print("   ✗ Erro: Usuário não encontrado por email")
            return False

    except Exception as e:
        print(f"   ✗ Erro ao testar busca: {e}")
        return False
    print()

    # Teste de atualização de senha
    print("2.5 Testando alteração de senha...")
    try:
        new_password = "NovaSenha123!"
        await user_service.update_password(
            user_id,
            "SenhaTeste123!",  # senha atual
            new_password  # nova senha
        )
        print("   ✓ Senha atualizada com sucesso")

        # Verificar se a nova senha funciona
        authenticated = await user_service.authenticate_user(test_email, new_password)
        if authenticated:
            print("   ✓ Autenticação com nova senha: SUCESSO")
        else:
            print("   ✗ Erro: Nova senha não funciona")
            return False

    except Exception as e:
        print(f"   ✗ Erro ao atualizar senha: {e}")
        return False
    print()

    # Limpeza
    print("2.6 Removendo usuário de teste...")
    try:
        await user_service.delete_user(user_id)
        print("   ✓ Usuário de teste removido com sucesso")
    except Exception as e:
        print(f"   ⚠ Aviso: Não foi possível remover usuário de teste: {e}")
    print()

    print("✓ UserService está funcionando perfeitamente!\n")
    return True


async def run_all_tests():
    """Executa todos os testes"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "TESTE COMPLETO DO SISTEMA DE AUTENTICAÇÃO" + " " * 7 + "║")
    print("╚" + "=" * 58 + "╝")
    print()

    # Teste 1: Funções de segurança
    success_security = await test_security_functions()
    if not success_security:
        print("\n✗ FALHA: Funções de segurança não estão funcionando")
        return False

    # Teste 2: UserService
    success_user_service = await test_user_service()
    if not success_user_service:
        print("\n✗ FALHA: UserService não está funcionando")
        print("\nVerifique:")
        print("1. Collection 'users' foi criada no Appwrite?")
        print("2. Todos os atributos estão corretos?")
        print("3. Execute: python test_appwrite_connection.py")
        return False

    # Resultado final
    print("=" * 60)
    print("✓ TODOS OS TESTES PASSARAM COM SUCESSO!")
    print("=" * 60)
    print()
    print("O sistema de autenticação está pronto para uso!")
    print()
    print("Próximos passos:")
    print("1. Inicie o backend: uvicorn app.main:app --reload")
    print("2. Inicie o frontend: cd frontend && npm run dev")
    print("3. Acesse /register para criar sua conta")
    print("4. Faça login e teste as funcionalidades")
    print()

    return True


if __name__ == "__main__":
    try:
        success = asyncio.run(run_all_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTeste interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ ERRO INESPERADO: {e}")
        import traceback
        traceback.print_exc()
        print("\n" + "=" * 60)
        print("POSSÍVEIS SOLUÇÕES:")
        print("=" * 60)
        print("1. Verifique se o .env está configurado corretamente")
        print("2. Execute: python test_appwrite_connection.py")
        print("3. Verifique os logs acima para mais detalhes")
        print()
        sys.exit(1)
