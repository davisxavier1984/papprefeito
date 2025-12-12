#!/usr/bin/env python3
"""
Script para migrar dados de municipios_editados.json para o Appwrite

Uso:
    python backend/scripts/migrate_json_to_appwrite.py
"""
import sys
import os
import json
from pathlib import Path
from datetime import datetime

# Adicionar diretório raiz ao path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir / "backend"))

from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.exception import AppwriteException
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurações
APPWRITE_ENDPOINT = os.getenv("APPWRITE_ENDPOINT", "https://cloud.appwrite.io/v1")
APPWRITE_PROJECT_ID = os.getenv("APPWRITE_PROJECT_ID", "68dc49bf000cebd54b85")
APPWRITE_API_KEY = os.getenv("APPWRITE_API_KEY")
DATABASE_ID = os.getenv("APPWRITE_DATABASE_ID", "papprefeito_db")
COLLECTION_ID = os.getenv("APPWRITE_COLLECTION_EDICOES_ID", "edicoes_municipios")

# Caminho do arquivo JSON
JSON_FILE = root_dir / "backend" / "municipios_editados.json"


def migrate_data():
    """Migra dados do JSON para o Appwrite"""

    if not APPWRITE_API_KEY:
        print("❌ ERRO: APPWRITE_API_KEY não configurada no .env")
        sys.exit(1)

    # Verificar se arquivo JSON existe
    if not JSON_FILE.exists():
        print(f"⚠️  Arquivo {JSON_FILE} não encontrado")
        print("Nenhum dado para migrar. Finalizando...")
        return

    # Carregar dados do JSON
    print(f"📂 Carregando dados de {JSON_FILE}...")
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if not data:
        print("ℹ️  Arquivo JSON vazio. Nenhum dado para migrar.")
        return

    print(f"📊 Encontrados {len(data)} registros para migrar")

    # Inicializar cliente Appwrite
    client = Client()
    client.set_endpoint(APPWRITE_ENDPOINT)
    client.set_project(APPWRITE_PROJECT_ID)
    client.set_key(APPWRITE_API_KEY)

    databases = Databases(client)

    print(f"\n🚀 Iniciando migração para Appwrite...")
    print(f"📡 Endpoint: {APPWRITE_ENDPOINT}")
    print(f"📦 Database: {DATABASE_ID}")
    print(f"📁 Collection: {COLLECTION_ID}")
    print()

    # Estatísticas
    success_count = 0
    error_count = 0
    skip_count = 0

    # Migrar cada registro
    for key, value in data.items():
        # Formato da chave: "codigo_municipio_competencia"
        parts = key.split('_')

        if len(parts) < 2:
            print(f"  ⚠️  Chave inválida: {key}, pulando...")
            skip_count += 1
            continue

        codigo_municipio = '_'.join(parts[:-1])  # Pode ter _ no código
        competencia = parts[-1]

        # Extrair dados
        perda_recurso = value.get('perda_recurso_mensal', [])

        if not isinstance(perda_recurso, list):
            print(f"  ⚠️  Formato inválido para {key}, pulando...")
            skip_count += 1
            continue

        # Preparar documento
        now = datetime.utcnow().isoformat()
        document_data = {
            'codigo_municipio': codigo_municipio,
            'competencia': competencia,
            'perda_recurso_mensal': json.dumps(perda_recurso),
            'created_at': now,
            'updated_at': now
        }

        # Inserir no Appwrite
        try:
            databases.create_document(
                database_id=DATABASE_ID,
                collection_id=COLLECTION_ID,
                document_id=key,
                data=document_data
            )
            print(f"  ✅ Migrado: {codigo_municipio} / {competencia}")
            success_count += 1

        except AppwriteException as e:
            if "already exists" in str(e).lower() or "document_already_exists" in str(e).lower():
                print(f"  ℹ️  Já existe: {codigo_municipio} / {competencia}")
                skip_count += 1
            else:
                print(f"  ❌ Erro ao migrar {key}: {e}")
                error_count += 1

    # Relatório final
    print("\n" + "="*60)
    print("📊 RELATÓRIO DE MIGRAÇÃO")
    print("="*60)
    print(f"✅ Sucesso: {success_count}")
    print(f"ℹ️  Pulados: {skip_count}")
    print(f"❌ Erros: {error_count}")
    print(f"📝 Total: {len(data)}")
    print("="*60)

    if success_count > 0:
        print(f"\n✅ Migração concluída! {success_count} registros migrados com sucesso.")

    if error_count > 0:
        print(f"\n⚠️  {error_count} erros encontrados durante a migração.")

    # Criar backup do JSON original
    if success_count > 0:
        backup_file = JSON_FILE.parent / f"municipios_editados.json.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        print(f"\n💾 Criando backup do arquivo original em:")
        print(f"   {backup_file}")

        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            original_data = f.read()

        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(original_data)

        print("✅ Backup criado com sucesso!")


if __name__ == "__main__":
    try:
        print("="*60)
        print("🔄 MIGRAÇÃO JSON → APPWRITE")
        print("="*60)
        print()

        migrate_data()

        print("\n✅ Processo finalizado!")

    except KeyboardInterrupt:
        print("\n\n⚠️  Migração cancelada pelo usuário")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
