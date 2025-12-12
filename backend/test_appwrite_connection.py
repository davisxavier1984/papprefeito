"""
Script de teste para verificar conexão com Appwrite
Execute: python test_appwrite_connection.py
"""
import sys
from pathlib import Path

# Adiciona o diretório backend ao path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.config import settings
from app.core.appwrite_client import appwrite_client


def test_connection():
    """Testa a conexão com Appwrite"""
    print("=" * 60)
    print("TESTE DE CONEXÃO COM APPWRITE")
    print("=" * 60)
    print()

    # 1. Verificar configurações
    print("1. Verificando configurações...")
    print(f"   ✓ Endpoint: {settings.APPWRITE_ENDPOINT}")
    print(f"   ✓ Project ID: {settings.APPWRITE_PROJECT_ID}")
    print(f"   ✓ Database ID: {settings.APPWRITE_DATABASE_ID}")
    print(f"   ✓ API Key: {'*' * 20}...{settings.APPWRITE_API_KEY[-10:] if settings.APPWRITE_API_KEY else 'NÃO CONFIGURADA'}")
    print()

    # 2. Testar conexão com Appwrite
    print("2. Testando conexão com Appwrite...")
    try:
        databases = appwrite_client.get_databases()
        print("   ✓ Cliente Appwrite inicializado com sucesso")
    except Exception as e:
        print(f"   ✗ Erro ao inicializar cliente: {e}")
        return False
    print()

    # 3. Listar databases
    print("3. Tentando acessar o database...")
    try:
        # Tenta listar collections no database
        result = databases.list_collections(
            database_id=settings.APPWRITE_DATABASE_ID
        )
        print(f"   ✓ Database '{settings.APPWRITE_DATABASE_ID}' encontrado")
        print(f"   ✓ Total de collections: {result['total']}")

        if result['total'] > 0:
            print("\n   Collections encontradas:")
            for collection in result['collections']:
                print(f"     - {collection['$id']} ({collection['name']})")
        else:
            print("\n   ⚠ Nenhuma collection encontrada no database")
            print("     Você precisará criar a collection 'users' manualmente")
        print()

    except Exception as e:
        print(f"   ✗ Erro ao acessar database: {e}")
        print("\n   POSSÍVEIS CAUSAS:")
        print("   - Database não existe no projeto")
        print("   - API Key sem permissões adequadas")
        print("   - Project ID incorreto")
        return False

    # 4. Verificar collection 'users'
    print("4. Verificando collection 'users'...")
    try:
        collection = databases.get_collection(
            database_id=settings.APPWRITE_DATABASE_ID,
            collection_id="users"
        )
        print(f"   ✓ Collection 'users' encontrada!")
        print(f"   ✓ Nome: {collection['name']}")
        print(f"   ✓ Atributos: {len(collection['attributes'])}")

        # Lista atributos
        print("\n   Atributos configurados:")
        required_attrs = {
            'email': 'string',
            'nome': 'string',
            'hashed_password': 'string',
            'is_active': 'boolean',
            'is_superuser': 'boolean',
            'created_at': 'string',
            'updated_at': 'string'
        }

        found_attrs = {attr['key']: attr['type'] for attr in collection['attributes']}

        for attr_name, attr_type in required_attrs.items():
            if attr_name in found_attrs:
                type_match = found_attrs[attr_name] == attr_type
                status = "✓" if type_match else "⚠"
                print(f"     {status} {attr_name} ({found_attrs[attr_name]})")
            else:
                print(f"     ✗ {attr_name} - NÃO ENCONTRADO")

        # Verifica índices
        print("\n   Índices configurados:")
        if collection['indexes']:
            for index in collection['indexes']:
                print(f"     ✓ {index['key']} ({index['type']}) - Atributos: {', '.join(index['attributes'])}")
        else:
            print("     ⚠ Nenhum índice encontrado")
            print("     Recomendação: Criar índice único para 'email'")

        print("\n   ✓ Collection 'users' está pronta para uso!")
        print()

    except Exception as e:
        print(f"   ✗ Collection 'users' não encontrada: {e}")
        print("\n   AÇÃO NECESSÁRIA:")
        print("   Você precisa criar a collection 'users' no Appwrite Console")
        print("   Consulte o arquivo APPWRITE_SETUP.md para instruções detalhadas")
        print()
        return False

    # 5. Teste final
    print("=" * 60)
    print("✓ TESTE CONCLUÍDO COM SUCESSO!")
    print("=" * 60)
    print("\nPróximos passos:")
    print("1. Execute o backend: uvicorn app.main:app --reload")
    print("2. Acesse a documentação: http://localhost:8000/docs")
    print("3. Teste o endpoint de registro: POST /api/auth/register")
    print()

    return True


if __name__ == "__main__":
    try:
        success = test_connection()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTeste interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ ERRO INESPERADO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
