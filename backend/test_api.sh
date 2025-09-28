#!/bin/bash
# Script para testar endpoints da API papprefeito

echo "=== Testando API papprefeito ==="
echo

# Testar endpoint raiz
echo "1. Testando endpoint raiz:"
curl -s http://localhost:8000/ | python3 -m json.tool
echo

# Testar health check
echo "2. Testando health check:"
curl -s http://localhost:8000/health | python3 -m json.tool
echo

# Testar lista de UFs
echo "3. Testando lista de UFs:"
curl -s http://localhost:8000/api/municipios/ufs | python3 -m json.tool | head -20
echo

# Testar municípios de MG
echo "4. Testando municípios de MG (primeiros 10):"
curl -s http://localhost:8000/api/municipios/municipios/MG | python3 -m json.tool | head -30
echo

# Testar última competência
echo "5. Testando última competência:"
curl -s http://localhost:8000/api/financiamento/competencia/latest | python3 -m json.tool
echo

# Testar conexão com API externa
echo "6. Testando conexão com API externa:"
curl -s http://localhost:8000/api/financiamento/test-connection | python3 -m json.tool
echo

# Testar dados editados (lista vazia inicialmente)
echo "7. Testando lista de dados editados:"
curl -s http://localhost:8000/api/municipios-editados/ | python3 -m json.tool
echo

echo "=== Testes concluídos ==="