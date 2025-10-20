"""
Script para testar e verificar compatibilidade do bcrypt
Execute: python test_bcrypt.py
"""
import sys
from pathlib import Path

# Adiciona o diretório backend ao path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("TESTE DE COMPATIBILIDADE BCRYPT")
print("=" * 60)
print()

# 1. Verificar versões instaladas
print("1. Verificando versões instaladas...")
try:
    import bcrypt
    import passlib

    # Tenta obter versão do bcrypt
    try:
        bcrypt_version = bcrypt.__version__
        print(f"   ✓ bcrypt versão: {bcrypt_version}")
    except AttributeError:
        try:
            bcrypt_version = bcrypt.__about__.__version__
            print(f"   ✓ bcrypt versão: {bcrypt_version}")
        except:
            print(f"   ⚠ bcrypt versão: (não detectada, mas instalado)")

    passlib_version = passlib.__version__
    print(f"   ✓ passlib versão: {passlib_version}")

except ImportError as e:
    print(f"   ✗ Erro ao importar: {e}")
    print("\n   Execute: pip install bcrypt passlib")
    sys.exit(1)
print()

# 2. Testar funções de hash
print("2. Testando funções de hash de senha...")
try:
    from app.core.security import get_password_hash, verify_password

    # Teste 1: Hash básico
    password = "TesteSenha123!"
    hashed = get_password_hash(password)
    print(f"   ✓ Hash gerado: {hashed[:40]}...")

    # Teste 2: Verificação positiva
    if verify_password(password, hashed):
        print(f"   ✓ Verificação de senha correta: OK")
    else:
        print(f"   ✗ Erro: Senha não verificada corretamente")
        sys.exit(1)

    # Teste 3: Verificação negativa
    if not verify_password("SenhaErrada123!", hashed):
        print(f"   ✓ Rejeição de senha incorreta: OK")
    else:
        print(f"   ✗ Erro: Senha incorreta foi aceita")
        sys.exit(1)

    # Teste 4: Múltiplos hashes
    print(f"\n   Testando múltiplos hashes...")
    for i in range(5):
        test_pwd = f"Teste{i}Pass123!"
        test_hash = get_password_hash(test_pwd)
        if verify_password(test_pwd, test_hash):
            print(f"     ✓ Teste {i+1}/5: OK")
        else:
            print(f"     ✗ Teste {i+1}/5: FALHOU")
            sys.exit(1)

except Exception as e:
    print(f"   ✗ Erro ao testar hash: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
print()

# 3. Verificar compatibilidade com diferentes senhas
print("3. Testando diferentes tipos de senha...")
test_passwords = [
    "Simples123!",
    "Muito_Complexa_2024@#$%",
    "CømÇârãçtérés123!",
    "Espaços São OK 123!",
    "a" * 100 + "Z1!",  # Senha longa
]

try:
    for i, pwd in enumerate(test_passwords, 1):
        h = get_password_hash(pwd)
        if verify_password(pwd, h):
            print(f"   ✓ Teste {i}/{len(test_passwords)}: OK")
        else:
            print(f"   ✗ Teste {i}/{len(test_passwords)}: FALHOU")
            sys.exit(1)
except Exception as e:
    print(f"   ✗ Erro: {e}")
    sys.exit(1)
print()

# 4. Verificar performance
print("4. Testando performance...")
import time
try:
    start = time.time()
    for _ in range(10):
        get_password_hash("TestPerformance123!")
    elapsed = time.time() - start
    avg = elapsed / 10

    print(f"   ✓ 10 hashes gerados em {elapsed:.2f}s")
    print(f"   ✓ Média: {avg:.3f}s por hash")

    if avg > 1.0:
        print(f"   ⚠ Aviso: Hash está lento (>{avg:.3f}s)")
        print(f"     Isso é normal para bcrypt (segurança > velocidade)")
    else:
        print(f"   ✓ Performance adequada")

except Exception as e:
    print(f"   ✗ Erro ao testar performance: {e}")
    sys.exit(1)
print()

# Resultado final
print("=" * 60)
print("✓ TODOS OS TESTES DE BCRYPT PASSARAM!")
print("=" * 60)
print()
print("O sistema de hash de senhas está funcionando corretamente.")
print()
print("Nota sobre warnings:")
print("- Avisos sobre 'bcrypt version' podem ser ignorados")
print("- O importante é que os testes de hash/verificação funcionem")
print()
print("Próximo passo:")
print("  python test_appwrite_connection.py")
print()

sys.exit(0)
