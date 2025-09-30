#!/usr/bin/env python3
"""
Script para configurar estrutura do Appwrite automaticamente
Cria database, collection e attributes necessários para o sistema MaisPAP

Uso:
    python backend/scripts/setup_appwrite.py
"""
import sys
import os
from pathlib import Path

# Adicionar diretório raiz ao path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir / "backend"))

from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.exception import AppwriteException
from appwrite.permission import Permission
from appwrite.role import Role
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurações
APPWRITE_ENDPOINT = os.getenv("APPWRITE_ENDPOINT", "https://cloud.appwrite.io/v1")
APPWRITE_PROJECT_ID = os.getenv("APPWRITE_PROJECT_ID", "68dc49bf000cebd54b85")
APPWRITE_API_KEY = os.getenv("APPWRITE_API_KEY")
DATABASE_ID = os.getenv("APPWRITE_DATABASE_ID", "papprefeito_db")
COLLECTION_ID = os.getenv("APPWRITE_COLLECTION_EDICOES_ID", "edicoes_municipios")


def setup_appwrite():
    """Configura database e collection no Appwrite"""

    if not APPWRITE_API_KEY:
        print("❌ ERRO: APPWRITE_API_KEY não configurada no .env")
        print("Por favor, adicione sua API Key no arquivo .env:")
        print("APPWRITE_API_KEY=sua_api_key_aqui")
        sys.exit(1)

    # Inicializar cliente
    client = Client()
    client.set_endpoint(APPWRITE_ENDPOINT)
    client.set_project(APPWRITE_PROJECT_ID)
    client.set_key(APPWRITE_API_KEY)

    databases = Databases(client)

    print("🚀 Iniciando setup do Appwrite...")
    print(f"📡 Endpoint: {APPWRITE_ENDPOINT}")
    print(f"📦 Project ID: {APPWRITE_PROJECT_ID}")
    print()

    # 1. Criar Database
    print("1️⃣  Criando database...")
    try:
        db = databases.create(
            database_id=DATABASE_ID,
            name="PAPPrefeito Database"
        )
        print(f"✅ Database '{DATABASE_ID}' criado com sucesso!")
    except AppwriteException as e:
        if "already exists" in str(e).lower() or "document_already_exists" in str(e).lower():
            print(f"ℹ️  Database '{DATABASE_ID}' já existe, pulando...")
        else:
            print(f"❌ Erro ao criar database: {e}")
            sys.exit(1)

    # 2. Criar Collection
    print("\n2️⃣  Criando collection...")
    try:
        collection = databases.create_collection(
            database_id=DATABASE_ID,
            collection_id=COLLECTION_ID,
            name="Edições de Municípios",
            permissions=[
                Permission.read(Role.any()),
                Permission.create(Role.users()),
                Permission.update(Role.users()),
                Permission.delete(Role.users())
            ],
            document_security=True
        )
        print(f"✅ Collection '{COLLECTION_ID}' criada com sucesso!")
    except AppwriteException as e:
        if "already exists" in str(e).lower() or "document_already_exists" in str(e).lower():
            print(f"ℹ️  Collection '{COLLECTION_ID}' já existe, pulando...")
        else:
            print(f"❌ Erro ao criar collection: {e}")
            sys.exit(1)

    # 3. Criar Attributes
    print("\n3️⃣  Criando attributes...")

    attributes = [
        {
            "name": "codigo_municipio",
            "type": "string",
            "size": 128,
            "required": True,
            "description": "Código IBGE do município"
        },
        {
            "name": "competencia",
            "type": "string",
            "size": 6,
            "required": True,
            "description": "Competência no formato AAAAMM"
        },
        {
            "name": "perca_recurso_mensal",
            "type": "string",
            "size": 10000,
            "required": True,
            "description": "JSON array com valores de perda mensal"
        },
        {
            "name": "usuario_id",
            "type": "string",
            "size": 128,
            "required": False,
            "description": "ID do usuário que fez a edição"
        },
        {
            "name": "created_at",
            "type": "datetime",
            "required": True,
            "description": "Data de criação"
        },
        {
            "name": "updated_at",
            "type": "datetime",
            "required": True,
            "description": "Data de última atualização"
        }
    ]

    for attr in attributes:
        try:
            if attr["type"] == "string":
                databases.create_string_attribute(
                    database_id=DATABASE_ID,
                    collection_id=COLLECTION_ID,
                    key=attr["name"],
                    size=attr["size"],
                    required=attr["required"]
                )
            elif attr["type"] == "datetime":
                databases.create_datetime_attribute(
                    database_id=DATABASE_ID,
                    collection_id=COLLECTION_ID,
                    key=attr["name"],
                    required=attr["required"]
                )
            print(f"  ✅ Attribute '{attr['name']}' criado")
        except AppwriteException as e:
            if "already exists" in str(e).lower() or "attribute_already_exists" in str(e).lower():
                print(f"  ℹ️  Attribute '{attr['name']}' já existe, pulando...")
            else:
                print(f"  ❌ Erro ao criar attribute '{attr['name']}': {e}")

    # 4. Criar Index
    print("\n4️⃣  Criando índice único...")
    try:
        databases.create_index(
            database_id=DATABASE_ID,
            collection_id=COLLECTION_ID,
            key="municipio_competencia",
            type="unique",
            attributes=["codigo_municipio", "competencia"]
        )
        print("  ✅ Index 'municipio_competencia' criado com sucesso!")
    except AppwriteException as e:
        if "already exists" in str(e).lower() or "index_already_exists" in str(e).lower():
            print("  ℹ️  Index 'municipio_competencia' já existe, pulando...")
        else:
            print(f"  ❌ Erro ao criar index: {e}")

    print("\n" + "="*60)
    print("✅ Setup do Appwrite concluído com sucesso!")
    print("="*60)
    print(f"\n📊 Database ID: {DATABASE_ID}")
    print(f"📁 Collection ID: {COLLECTION_ID}")
    print(f"\n🔗 Acesse o console do Appwrite:")
    print(f"   {APPWRITE_ENDPOINT.replace('/v1', '')}/console/project-{APPWRITE_PROJECT_ID}")
    print()


if __name__ == "__main__":
    try:
        setup_appwrite()
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup cancelado pelo usuário")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
