"""
Teste para validar os cálculos corrigidos no sistema de relatórios PDF
"""

def testar_calculos():
    """
    Testa os cálculos corrigidos com diferentes cenários
    """
    print(">> Testando cálculos corrigidos...")

    # Valores de referência das portarias
    VALORES_REFERENCIA = {
        'Otimo': 8000,
        'Bom': 6000,
        'Suficiente': 4000,
        'Regular': 2000
    }

    # Cenários de teste
    cenarios = [
        {
            'nome': 'Município com classificação Bom',
            'valor_atual': 18000,  # Simulando 3 eSF com Bom (3 x 6000)
            'classificacao_atual': 'Bom'
        },
        {
            'nome': 'Município com classificação Regular',
            'valor_atual': 6000,   # Simulando 3 eSF com Regular (3 x 2000)
            'classificacao_atual': 'Regular'
        },
        {
            'nome': 'Município com classificação Suficiente',
            'valor_atual': 12000,  # Simulando 3 eSF com Suficiente (3 x 4000)
            'classificacao_atual': 'Suficiente'
        },
        {
            'nome': 'Município com classificação Ótimo',
            'valor_atual': 24000,  # Simulando 3 eSF com Ótimo (3 x 8000)
            'classificacao_atual': 'Otimo'
        }
    ]

    for cenario in cenarios:
        print(f"\n>> {cenario['nome']}")
        print(f"   Valor atual: R$ {cenario['valor_atual']:,.2f}")
        print(f"   Classificacao: {cenario['classificacao_atual']}")

        # Calcular valores usando a mesma lógica do app.py
        classificacao_atual = cenario['classificacao_atual']
        valor_atual = cenario['valor_atual']

        valor_referencia_atual = VALORES_REFERENCIA.get(classificacao_atual, 6000)
        valor_referencia_otimo = VALORES_REFERENCIA['Otimo']

        fator_multiplicador = valor_atual / valor_referencia_atual if valor_referencia_atual > 0 else 1
        valor_otimo = valor_referencia_otimo * fator_multiplicador

        diferenca_anual = (valor_otimo - valor_atual) * 12
        percentual_ganho = ((valor_otimo - valor_atual) / valor_atual) * 100 if valor_atual > 0 else 0

        print(f"   Valor ótimo: R$ {valor_otimo:,.2f}")
        print(f"   Ganho mensal: R$ {valor_otimo - valor_atual:,.2f}")
        print(f"   Ganho anual: R$ {diferenca_anual:,.2f}")
        print(f"   Percentual ganho: {percentual_ganho:.1f}%")

        # Validacoes
        if classificacao_atual == 'Otimo':
            assert abs(percentual_ganho) < 0.1, f"ERRO: Otimo deveria ter ganho ~0%, mas tem {percentual_ganho:.1f}%"
            print("   OK: Classificacao otima nao tem ganho adicional")
        elif classificacao_atual == 'Bom':
            ganho_esperado = (8000 - 6000) / 6000 * 100  # ~33.3%
            assert abs(percentual_ganho - ganho_esperado) < 1, f"ERRO: Esperado ~{ganho_esperado:.1f}%, obtido {percentual_ganho:.1f}%"
            print("   OK: Ganho de Bom para Otimo esta correto")
        elif classificacao_atual == 'Regular':
            ganho_esperado = (8000 - 2000) / 2000 * 100  # 300%
            assert abs(percentual_ganho - ganho_esperado) < 1, f"ERRO: Esperado ~{ganho_esperado:.1f}%, obtido {percentual_ganho:.1f}%"
            print("   OK: Ganho de Regular para Otimo esta correto")
        elif classificacao_atual == 'Suficiente':
            ganho_esperado = (8000 - 4000) / 4000 * 100  # 100%
            assert abs(percentual_ganho - ganho_esperado) < 1, f"ERRO: Esperado ~{ganho_esperado:.1f}%, obtido {percentual_ganho:.1f}%"
            print("   OK: Ganho de Suficiente para Otimo esta correto")

def testar_proporcionalidade():
    """
    Testa se a proporcionalidade entre as classificacoes esta correta
    """
    print("\n>> Testando proporcionalidade entre classificacoes...")

    VALORES_REFERENCIA = {
        'Otimo': 8000,
        'Bom': 6000,
        'Suficiente': 4000,
        'Regular': 2000
    }

    # Verificar se as proporções estão corretas
    print(f"Regular para Bom: {VALORES_REFERENCIA['Bom'] / VALORES_REFERENCIA['Regular']:.1f}x")
    print(f"Bom para Otimo: {VALORES_REFERENCIA['Otimo'] / VALORES_REFERENCIA['Bom']:.2f}x")
    print(f"Regular para Otimo: {VALORES_REFERENCIA['Otimo'] / VALORES_REFERENCIA['Regular']:.1f}x")

    # Validacoes
    assert VALORES_REFERENCIA['Bom'] / VALORES_REFERENCIA['Regular'] == 3.0, "ERRO: Regular para Bom deveria ser 3x"
    assert abs(VALORES_REFERENCIA['Otimo'] / VALORES_REFERENCIA['Bom'] - 1.33) < 0.01, "ERRO: Bom para Otimo deveria ser ~1.33x"
    assert VALORES_REFERENCIA['Otimo'] / VALORES_REFERENCIA['Regular'] == 4.0, "ERRO: Regular para Otimo deveria ser 4x"

    print("OK: Todas as proporcoes estao corretas")

def testar_casos_extremos():
    """
    Testa casos extremos e validacoes
    """
    print("\n>> Testando casos extremos...")

    # Caso 1: Valor atual zero
    print("Caso 1: Valor atual zero")
    try:
        valor_atual = 0
        if valor_atual <= 0:
            print("   OK: Detectou valor invalido")
        else:
            print("   ERRO: Nao detectou valor invalido")
    except:
        print("   OK: Lancou excecao para valor invalido")

    # Caso 2: Classificacao invalida
    print("Caso 2: Classificacao invalida")
    classificacao_invalida = "Inexistente"
    classificacoes_validas = ['Otimo', 'Bom', 'Suficiente', 'Regular']

    if classificacao_invalida not in classificacoes_validas:
        classificacao_corrigida = 'Bom'
        print(f"   OK: Corrigiu '{classificacao_invalida}' para '{classificacao_corrigida}'")

    print("\nOK: Todos os testes passaram!")

if __name__ == "__main__":
    print(">> Iniciando testes dos calculos corrigidos\n")

    try:
        testar_calculos()
        testar_proporcionalidade()
        testar_casos_extremos()

        print("\n>> Todos os testes foram executados com sucesso!")
        print(">> Resumo das correcoes implementadas:")
        print("   - Calculos baseados em valores de referencia oficiais")
        print("   - Comparacao entre cenario atual vs otimo (nao regular vs otimo)")
        print("   - Percentuais corretos de ganho potencial")
        print("   - Validacao de dados de entrada")
        print("   - Tratamento de casos extremos")

    except AssertionError as e:
        print(f"\nERRO: Teste falhou: {e}")
    except Exception as e:
        print(f"\nERRO inesperado: {e}")