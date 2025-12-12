#!/usr/bin/env python3
"""
Script para criar o primeiro superusuário autorizado
"""
import os
import sys
from datetime import datetime
from getpass import getpass
from pathlib import Path
from dotenv import load_dotenv
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.id import ID
from appwrite.query import Query
from appwrite.exception import AppwriteException

# Carrega variáveis de ambiente do arquivo .env
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

# Adiciona o diretório pai ao path para importar módulos do app
sys.path.insert(0, os.path.dirname(__file__))

from app.core.security import get_password_hash

# Configuração do Appwrite
APPWRITE_ENDPOINT = os.getenv("APPWRITE_ENDPOINT", "https://cloud.appwrite.io/v1")
APPWRITE_PROJECT_ID = os.getenv("APPWRITE_PROJECT_ID")
APPWRITE_API_KEY = os.getenv("APPWRITE_API_KEY")
APPWRITE_DATABASE_ID = os.getenv("APPWRITE_DATABASE_ID")


def validate_email(email: str) -> bool:
    """Valida formato básico de email"""
    return '@' in email and '.' in email


def validate_password(password: str) -> bool:
    """Valida senha"""
    if len(password) < 8:
        print("❌ Senha deve ter no mínimo 8 caracteres")
        return False
    if not any(c.isupper() for c in password):
        print("❌ Senha deve conter ao menos uma letra maiúscula")
        return False
    if not any(c.islower() for c in password):
        print("❌ Senha deve conter ao menos uma letra minúscula")
        return False
    if not any(c.isdigit() for c in password):
        print("❌ Senha deve conter ao menos um número")
        return False
    return True


def main():
    """Cria o primeiro superusuário"""

    if not all([APPWRITE_PROJECT_ID, APPWRITE_API_KEY, APPWRITE_DATABASE_ID]):
        print("❌ Erro: Variáveis de ambiente não configuradas")
        print("   Configure: APPWRITE_PROJECT_ID, APPWRITE_API_KEY, APPWRITE_DATABASE_ID")
        sys.exit(1)

    # Inicializa o cliente Appwrite
    client = Client()
    client.set_endpoint(APPWRITE_ENDPOINT)
    client.set_project(APPWRITE_PROJECT_ID)
    client.set_key(APPWRITE_API_KEY)

    databases = Databases(client)
    collection_id = "users"

    print("=" * 60)
    print("🔐 CRIAR PRIMEIRO SUPERUSUÁRIO")
    print("=" * 60)
    print()

    # Verifica se já existem superusuários
    try:
        result = databases.list_documents(
            database_id=APPWRITE_DATABASE_ID,
            collection_id=collection_id,
            queries=[
                Query.equal("is_superuser", True),
                Query.limit(1)
            ]
        )

        if result['total'] > 0:
            print("⚠️  Já existe pelo menos um superusuário no sistema:")
            doc = result['documents'][0]
            print(f"   Email: {doc.get('email', 'N/A')}")
            print(f"   Nome: {doc.get('nome', 'N/A')}")
            print()
            response = input("Deseja criar outro superusuário? (s/n): ")
            if response.lower() != 's':
                print("Operação cancelada.")
                return

    except AppwriteException as e:
        print(f"⚠️  Aviso: {e.message}")
        print()

    # Verifica atributos existentes na collection e cria 'is_authorized' se necessário
    allowed_attrs = set()
    try:
        collection = databases.get_collection(
            database_id=APPWRITE_DATABASE_ID,
            collection_id=collection_id,
        )
        allowed_attrs = {attr['key'] for attr in collection.get('attributes', [])}

        if 'is_authorized' not in allowed_attrs:
            print("⚠️  Campo 'is_authorized' não existe na collection 'users'.")
            resp = input("Deseja adicioná-lo automaticamente agora? (s/n): ").strip().lower()
            if resp == 's':
                try:
                    databases.create_boolean_attribute(
                        database_id=APPWRITE_DATABASE_ID,
                        collection_id=collection_id,
                        key="is_authorized",
                        required=False,
                        default=False,
                    )
                    # Aguarda o processamento do Appwrite
                    import time
                    print("⏳ Aguardando o processamento do novo atributo...")
                    time.sleep(4)
                    # Recarrega atributos
                    collection = databases.get_collection(
                        database_id=APPWRITE_DATABASE_ID,
                        collection_id=collection_id,
                    )
                    allowed_attrs = {attr['key'] for attr in collection.get('attributes', [])}
                    if 'is_authorized' in allowed_attrs:
                        print("✅ Atributo 'is_authorized' adicionado com sucesso.")
                    else:
                        print("⚠️  Não foi possível confirmar o atributo 'is_authorized'. Prosseguindo sem ele.")
                except AppwriteException as e:
                    print(f"⚠️  Não foi possível criar o atributo automaticamente: {e.message}")
                    print("   Dica: execute 'python add_authorization_field.py' e tente novamente.")
            else:
                print("ℹ Prosseguindo sem o campo 'is_authorized'.")
    except AppwriteException as e:
        if e.code == 404:
            print("❌ Collection 'users' não encontrada.")
            print("   Execute primeiro: python create_users_collection.py")
            sys.exit(1)
        else:
            print(f"⚠️  Aviso ao ler collection: {e.message}")

    # Coleta informações do superusuário
    print("Digite os dados do superusuário:")
    print()

    while True:
        email = input("Email: ").strip()
        if validate_email(email):
            break
        print("❌ Email inválido. Tente novamente.")

    nome = input("Nome completo: ").strip()
    if not nome:
        nome = "Administrador"

    while True:
        password = getpass("Senha (mínimo 8 caracteres, com maiúscula, minúscula e número): ")
        if validate_password(password):
            password_confirm = getpass("Confirme a senha: ")
            if password == password_confirm:
                break
            print("❌ As senhas não conferem. Tente novamente.")
        else:
            print("Tente novamente.")

    print()
    print("📋 Resumo:")
    print(f"   Email: {email}")
    print(f"   Nome: {nome}")
    print(f"   Superusuário: Sim")
    if 'is_authorized' in allowed_attrs:
        print(f"   Autorizado: Sim")
    else:
        print(f"   Autorizado: (campo ausente na collection)")
    print()

    response = input("Confirma a criação? (s/n): ")
    if response.lower() != 's':
        print("Operação cancelada.")
        return

    # Cria o superusuário
    try:
        # Verifica se já existe usuário com este email
        existing = databases.list_documents(
            database_id=APPWRITE_DATABASE_ID,
            collection_id=collection_id,
            queries=[Query.equal("email", email.lower())]
        )

        if existing['total'] > 0:
            print(f"❌ Já existe um usuário com o email {email}")
            sys.exit(1)

        # Hash da senha
        hashed_password = get_password_hash(password)

        # Cria documento
        now = datetime.utcnow().isoformat()
        base_document_data = {
            "email": email.lower(),
            "nome": nome,
            "hashed_password": hashed_password,
            "is_active": True,
            "is_superuser": True,
            "created_at": now,
            "updated_at": now
        }

        # Inclui autorização apenas se o atributo existir, caso contrário remove
        if 'is_authorized' in allowed_attrs:
            base_document_data["is_authorized"] = True
        else:
            base_document_data.pop("is_authorized", None)

        # Mantém demais campos como definidos; Appwrite ignora extras válidos e
        # retornará erro apenas se houver atributos inexistentes (já tratados acima)
        document_data = base_document_data

        doc = databases.create_document(
            database_id=APPWRITE_DATABASE_ID,
            collection_id=collection_id,
            document_id=ID.unique(),
            data=document_data
        )

        print()
        print("✅ Superusuário criado com sucesso!")
        print()
        print("📋 Detalhes:")
        print(f"   ID: {doc['$id']}")
        print(f"   Email: {doc['email']}")
        print(f"   Nome: {doc['nome']}")
        print(f"   Autorizado: {doc.get('is_authorized', False)}")
        print(f"   Superusuário: {doc.get('is_superuser', False)}")
        print()
        print("✅ Você já pode fazer login com este usuário!")

    except AppwriteException as e:
        print(f"❌ Erro ao criar superusuário: {e.message}")
        print(f"   Código: {e.code}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
