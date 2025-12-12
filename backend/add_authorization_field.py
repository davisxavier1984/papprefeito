#!/usr/bin/env python3
"""
Script para adicionar o campo is_authorized na collection de usuários
"""
import os
import sys
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.exception import AppwriteException

# Configuração do Appwrite
APPWRITE_ENDPOINT = os.getenv("APPWRITE_ENDPOINT", "https://cloud.appwrite.io/v1")
APPWRITE_PROJECT_ID = os.getenv("APPWRITE_PROJECT_ID")
APPWRITE_API_KEY = os.getenv("APPWRITE_API_KEY")
APPWRITE_DATABASE_ID = os.getenv("APPWRITE_DATABASE_ID")

def main():
    """Adiciona o campo is_authorized na collection de usuários"""

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

    print(f"🔧 Adicionando campo is_authorized na collection '{collection_id}'...")
    print(f"   Database: {APPWRITE_DATABASE_ID}")
    print(f"   Endpoint: {APPWRITE_ENDPOINT}")
    print()

    try:
        # Verifica se o atributo já existe
        try:
            collection = databases.get_collection(
                database_id=APPWRITE_DATABASE_ID,
                collection_id=collection_id
            )

            # Verifica se is_authorized já existe
            existing_attrs = [attr['key'] for attr in collection['attributes']]
            if 'is_authorized' in existing_attrs:
                print("⚠️  Campo 'is_authorized' já existe na collection")
                print()

                # Pergunta se quer atualizar usuários existentes
                response = input("Deseja marcar todos os superusuários como autorizados? (s/n): ")
                if response.lower() == 's':
                    update_existing_users(databases, APPWRITE_DATABASE_ID, collection_id)
                return

        except AppwriteException as e:
            if e.code != 404:
                raise

        # Adiciona o atributo is_authorized (boolean, opcional, padrão false)
        databases.create_boolean_attribute(
            database_id=APPWRITE_DATABASE_ID,
            collection_id=collection_id,
            key="is_authorized",
            required=False,
            default=False
        )

        print("✅ Campo 'is_authorized' adicionado com sucesso!")
        print()
        print("📋 Configuração do campo:")
        print("   - Tipo: Boolean")
        print("   - Obrigatório: Não")
        print("   - Valor padrão: false")
        print()
        print("⚠️  IMPORTANTE:")
        print("   - Novos usuários serão criados com is_authorized = false")
        print("   - Usuários existentes precisarão ser autorizados manualmente")
        print()

        # Pergunta se quer atualizar usuários existentes
        response = input("Deseja marcar todos os superusuários como autorizados? (s/n): ")
        if response.lower() == 's':
            # Aguarda o Appwrite processar o novo atributo
            import time
            print("⏳ Aguardando Appwrite processar o novo atributo...")
            time.sleep(3)
            update_existing_users(databases, APPWRITE_DATABASE_ID, collection_id)

    except AppwriteException as e:
        print(f"❌ Erro ao adicionar campo: {e.message}")
        print(f"   Código: {e.code}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        sys.exit(1)


def update_existing_users(databases: Databases, database_id: str, collection_id: str):
    """Atualiza usuários existentes marcando superusuários como autorizados"""
    from appwrite.query import Query

    print()
    print("🔄 Atualizando usuários existentes...")

    try:
        # Busca todos os superusuários
        result = databases.list_documents(
            database_id=database_id,
            collection_id=collection_id,
            queries=[
                Query.equal("is_superuser", True),
                Query.limit(100)
            ]
        )

        if result['total'] == 0:
            print("⚠️  Nenhum superusuário encontrado")
            print()
            print("💡 Dica: Você pode criar um superusuário usando:")
            print("   python create_first_superuser.py")
            return

        # Atualiza cada superusuário
        updated_count = 0
        for doc in result['documents']:
            try:
                databases.update_document(
                    database_id=database_id,
                    collection_id=collection_id,
                    document_id=doc['$id'],
                    data={'is_authorized': True}
                )
                print(f"   ✅ {doc.get('email', 'N/A')} - autorizado")
                updated_count += 1
            except Exception as e:
                print(f"   ❌ Erro ao atualizar {doc.get('email', 'N/A')}: {e}")

        print()
        print(f"✅ {updated_count} superusuário(s) autorizado(s) com sucesso!")

    except AppwriteException as e:
        print(f"❌ Erro ao atualizar usuários: {e.message}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")


if __name__ == "__main__":
    main()
