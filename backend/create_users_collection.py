"""
Script para criar automaticamente a collection 'users' no Appwrite
Execute: python create_users_collection.py
"""
import sys
from pathlib import Path

# Adiciona o diretório backend ao path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.config import settings
from app.core.appwrite_client import appwrite_client
from appwrite.exception import AppwriteException

print("=" * 70)
print("CRIAÇÃO AUTOMÁTICA DA COLLECTION 'users'")
print("=" * 70)
print()

# Verificar configurações
print("1. Verificando configurações...")
print(f"   Database ID: {settings.APPWRITE_DATABASE_ID}")
print(f"   Collection ID: users")
print()

# Confirmar
print("⚠️  ATENÇÃO:")
print("   Este script irá criar a collection 'users' com todos os atributos")
print("   necessários para o sistema de autenticação.")
print()
response = input("Deseja continuar? (s/N): ").strip().lower()
if response != 's':
    print("\n✗ Operação cancelada pelo usuário")
    sys.exit(0)

print()
databases = appwrite_client.get_databases()

# Criar collection
print("2. Criando collection 'users'...")
try:
    collection = databases.create_collection(
        database_id=settings.APPWRITE_DATABASE_ID,
        collection_id="users",
        name="Users",
        document_security=True
    )
    print(f"   ✓ Collection criada com sucesso!")
    print(f"   ✓ ID: {collection['$id']}")
    print(f"   ✓ Nome: {collection['name']}")
except AppwriteException as e:
    if "already exists" in str(e).lower():
        print(f"   ℹ Collection 'users' já existe")
    else:
        print(f"   ✗ Erro ao criar collection: {e}")
        sys.exit(1)
print()

# Criar atributos
print("3. Criando atributos...")

attributes = [
    {
        "key": "email",
        "type": "string",
        "size": 255,
        "required": True,
        "description": "Email do usuário (único)"
    },
    {
        "key": "nome",
        "type": "string",
        "size": 255,
        "required": True,
        "description": "Nome completo do usuário"
    },
    {
        "key": "hashed_password",
        "type": "string",
        "size": 255,
        "required": True,
        "description": "Hash da senha (bcrypt)"
    },
    {
        "key": "is_active",
        "type": "boolean",
        "required": True,
        "default": True,
        "description": "Se o usuário está ativo"
    },
    {
        "key": "is_superuser",
        "type": "boolean",
        "required": True,
        "default": False,
        "description": "Se o usuário é administrador"
    },
    {
        "key": "created_at",
        "type": "string",
        "size": 50,
        "required": True,
        "description": "Data de criação (ISO format)"
    },
    {
        "key": "updated_at",
        "type": "string",
        "size": 50,
        "required": False,
        "description": "Data da última atualização (ISO format)"
    }
]

for i, attr in enumerate(attributes, 1):
    try:
        attr_key = attr.pop("key")
        attr_type = attr.pop("type")
        description = attr.pop("description", "")

        print(f"   Criando atributo {i}/7: {attr_key} ({attr_type})...")

        if attr_type == "string":
            databases.create_string_attribute(
                database_id=settings.APPWRITE_DATABASE_ID,
                collection_id="users",
                key=attr_key,
                **attr
            )
        elif attr_type == "boolean":
            databases.create_boolean_attribute(
                database_id=settings.APPWRITE_DATABASE_ID,
                collection_id="users",
                key=attr_key,
                **attr
            )

        print(f"   ✓ Atributo '{attr_key}' criado")

    except AppwriteException as e:
        if "already exists" in str(e).lower():
            print(f"   ℹ Atributo '{attr_key}' já existe")
        else:
            print(f"   ⚠ Erro ao criar atributo '{attr_key}': {e}")

print()

# Aguardar processamento dos atributos
print("4. Aguardando processamento dos atributos...")
print("   (Appwrite precisa de alguns segundos para processar os atributos)")
import time
time.sleep(5)
print("   ✓ Pronto")
print()

# Criar índice
print("5. Criando índice único para email...")
try:
    index = databases.create_index(
        database_id=settings.APPWRITE_DATABASE_ID,
        collection_id="users",
        key="email_unique",
        type="unique",
        attributes=["email"]
    )
    print(f"   ✓ Índice criado com sucesso")
except AppwriteException as e:
    if "already exists" in str(e).lower():
        print(f"   ℹ Índice já existe")
    else:
        print(f"   ⚠ Erro ao criar índice: {e}")
        print(f"   ℹ Você pode criar manualmente no console")
print()

# Configurar permissões
print("6. Configurando permissões...")
print("   ⚠️  ATENÇÃO: Permissões devem ser configuradas manualmente no Appwrite Console")
print("   ℹ Acesse: Settings → Permissions na collection 'users'")
print()
print("   Configure:")
print("   - Create: any (permite registro público)")
print("   - Read: users (apenas autenticados)")
print("   - Update: users (apenas autenticados)")
print("   - Delete: users (apenas autenticados)")
print()

# Verificar resultado
print("7. Verificando collection criada...")
try:
    collection = databases.get_collection(
        database_id=settings.APPWRITE_DATABASE_ID,
        collection_id="users"
    )

    print(f"   ✓ Collection encontrada!")
    print(f"   ✓ Nome: {collection['name']}")
    print(f"   ✓ Atributos: {len(collection['attributes'])}")
    print()

    print("   Atributos encontrados:")
    for attr in collection['attributes']:
        required = "✓" if attr['required'] else "○"
        print(f"     {required} {attr['key']} ({attr['type']})")
    print()

except AppwriteException as e:
    print(f"   ✗ Erro ao verificar collection: {e}")
    sys.exit(1)

# Resultado final
print("=" * 70)
print("✓ COLLECTION 'users' CRIADA COM SUCESSO!")
print("=" * 70)
print()
print("⚠️  IMPORTANTE: Configure as permissões manualmente no Appwrite Console")
print()
print("Próximos passos:")
print("1. Acesse o Appwrite Console")
print("2. Vá em Settings da collection 'users'")
print("3. Configure as permissões conforme indicado acima")
print("4. Execute: python test_appwrite_connection.py")
print("5. Execute: python test_auth_flow.py")
print()
