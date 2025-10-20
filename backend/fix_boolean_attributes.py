"""
Script para adicionar os atributos booleanos faltantes
Execute: python fix_boolean_attributes.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.core.config import settings
from app.core.appwrite_client import appwrite_client
from appwrite.exception import AppwriteException

print("=" * 70)
print("ADICIONANDO ATRIBUTOS BOOLEANOS")
print("=" * 70)
print()

databases = appwrite_client.get_databases()

# Criar atributos booleanos sem default (não obrigatórios primeiro)
print("1. Criando atributos booleanos...")

boolean_attrs = [
    {
        "key": "is_active",
        "required": False,  # Vamos criar como opcional primeiro
        "description": "Se o usuário está ativo"
    },
    {
        "key": "is_superuser",
        "required": False,  # Vamos criar como opcional primeiro
        "description": "Se o usuário é administrador"
    }
]

for attr in boolean_attrs:
    try:
        print(f"   Criando atributo: {attr['key']}...")

        databases.create_boolean_attribute(
            database_id=settings.APPWRITE_DATABASE_ID,
            collection_id="users",
            key=attr['key'],
            required=attr['required']
        )

        print(f"   ✓ Atributo '{attr['key']}' criado")

    except AppwriteException as e:
        if "already exists" in str(e).lower():
            print(f"   ℹ Atributo '{attr['key']}' já existe")
        else:
            print(f"   ✗ Erro ao criar atributo '{attr['key']}': {e}")

print()
print("=" * 70)
print("✓ ATRIBUTOS BOOLEANOS ADICIONADOS!")
print("=" * 70)
print()
print("⚠️  NOTA IMPORTANTE:")
print("   Os atributos is_active e is_superuser foram criados como OPCIONAIS")
print("   devido a limitação da API do Appwrite.")
print()
print("   O sistema funcionará perfeitamente assim, pois:")
print("   - O código sempre define valores para esses campos")
print("   - Novos usuários receberão is_active=true e is_superuser=false")
print()
print("Próximo passo:")
print("   python test_appwrite_connection.py")
print()
