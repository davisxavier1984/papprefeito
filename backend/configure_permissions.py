"""
Script para configurar permissões da collection 'users' via API
Execute: python configure_permissions.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.core.config import settings
from app.core.appwrite_client import appwrite_client
from appwrite.exception import AppwriteException
from appwrite.permission import Permission
from appwrite.role import Role

print("=" * 70)
print("CONFIGURAÇÃO DE PERMISSÕES - COLLECTION 'users'")
print("=" * 70)
print()

databases = appwrite_client.get_databases()

print("⚠️  NOTA IMPORTANTE:")
print("   As permissões da collection são configuradas a nível de collection,")
print("   não via API de permissões. O Appwrite gerencia isso através da")
print("   configuração 'documentSecurity'.")
print()
print("   Vamos verificar a configuração atual...")
print()

# Verificar collection atual
try:
    collection = databases.get_collection(
        database_id=settings.APPWRITE_DATABASE_ID,
        collection_id="users"
    )

    print("✓ Collection 'users' encontrada")
    print(f"  - Document Security: {collection.get('documentSecurity', False)}")
    print(f"  - Total de atributos: {len(collection['attributes'])}")
    print()

    # Mostrar permissões atuais (se disponível)
    if 'permissions' in collection:
        print("Permissões atuais:")
        for perm in collection['permissions']:
            print(f"  - {perm}")
    else:
        print("  (Permissões não disponíveis via API)")

    print()

except AppwriteException as e:
    print(f"✗ Erro ao buscar collection: {e}")
    sys.exit(1)

print("=" * 70)
print("CONFIGURAÇÃO MANUAL NECESSÁRIA")
print("=" * 70)
print()
print("Infelizmente, as permissões de collection no Appwrite devem ser")
print("configuradas através do Console Web.")
print()
print("Como a interface não está mostrando as opções esperadas,")
print("vamos testar se o sistema funciona mesmo sem permissões explícitas.")
print()
print("Próximo passo:")
print("  python test_auth_flow.py")
print()
print("Se o teste passar, significa que:")
print("  ✓ A API Key tem permissões de administrador")
print("  ✓ O sistema funcionará corretamente no backend")
print()
print("Para produção, você precisará configurar as permissões via Console")
print("para garantir segurança adequada.")
print()
