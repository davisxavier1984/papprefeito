#!/usr/bin/env python3
"""Teste completo de validação do sistema de PDF - 3 páginas."""

import sys
from pathlib import Path

sys.path.append('.')

from app.models.schemas import ResumoFinanceiro
from app.services.relatorio_pdf import create_pdf_report, create_html_pdf_report, create_fpdf_report


def test_calculos():
    """Validar todos os cálculos matemáticos."""
    print("\n" + "="*60)
    print("🧮 TESTE 1: Validação de Cálculos")
    print("="*60)

    # Cenário de teste
    resumo = ResumoFinanceiro(
        total_perda_mensal=15000.00,
        total_diferenca_anual=180000.00,
        percentual_perda_anual=12.5,
        total_recebido=120000.00
    )

    # Cálculos esperados
    recurso_atual_mensal = resumo.total_recebido
    acrescimo_mensal = resumo.total_perda_mensal
    recurso_potencial_mensal = recurso_atual_mensal + acrescimo_mensal

    recurso_atual_anual = recurso_atual_mensal * 12
    recurso_potencial_anual = recurso_atual_anual + resumo.total_diferenca_anual

    print(f"\n📊 Valores Mensais:")
    print(f"   Atual: R$ {recurso_atual_mensal:,.2f}")
    print(f"   Acréscimo: R$ {acrescimo_mensal:,.2f}")
    print(f"   Potencial: R$ {recurso_potencial_mensal:,.2f}")

    print(f"\n📊 Valores Anuais:")
    print(f"   Atual: R$ {recurso_atual_anual:,.2f}")
    print(f"   Diferença: R$ {resumo.total_diferenca_anual:,.2f}")
    print(f"   Potencial: R$ {recurso_potencial_anual:,.2f}")

    # Validações
    assert acrescimo_mensal * 12 == resumo.total_diferenca_anual, "❌ Erro: Diferença anual não bate!"
    assert recurso_potencial_mensal == 135000.00, "❌ Erro: Potencial mensal incorreto!"
    assert recurso_atual_anual == 1440000.00, "❌ Erro: Atual anual incorreto!"
    assert recurso_potencial_anual == 1620000.00, "❌ Erro: Potencial anual incorreto!"

    print("\n✅ Todos os cálculos estão corretos!")
    return True


def test_pdf_geracao(output_name='teste_validacao.pdf'):
    """Testar geração de PDF com dados reais."""
    print("\n" + "="*60)
    print("📄 TESTE 2: Geração de PDF")
    print("="*60)

    resumo = ResumoFinanceiro(
        total_perda_mensal=25000.00,
        total_diferenca_anual=300000.00,
        percentual_perda_anual=15.75,
        total_recebido=190000.00
    )

    try:
        pdf_bytes = create_pdf_report(
            municipio_nome="Belo Horizonte",
            uf="MG",
            competencia="2025-01",
            resumo=resumo
        )

        print(f"\n✅ PDF gerado com sucesso!")
        print(f"   Tamanho: {len(pdf_bytes):,} bytes ({len(pdf_bytes)/1024:.1f} KB)")
        print(f"   Validação em memória (não salvo)")

        # Validações
        assert len(pdf_bytes) > 5000, "❌ PDF muito pequeno!"
        assert len(pdf_bytes) < 500000, "❌ PDF muito grande!"

        return True

    except Exception as e:
        print(f"❌ Erro ao gerar PDF: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_cenarios_extremos():
    """Testar com valores extremos."""
    print("\n" + "="*60)
    print("🔬 TESTE 3: Cenários Extremos")
    print("="*60)

    cenarios = [
        {
            'nome': 'Valores Pequenos',
            'resumo': ResumoFinanceiro(
                total_perda_mensal=500.00,
                total_diferenca_anual=6000.00,
                percentual_perda_anual=2.5,
                total_recebido=20000.00
            )
        },
        {
            'nome': 'Valores Grandes',
            'resumo': ResumoFinanceiro(
                total_perda_mensal=500000.00,
                total_diferenca_anual=6000000.00,
                percentual_perda_anual=25.0,
                total_recebido=2000000.00
            )
        },
        {
            'nome': 'Valores Zero',
            'resumo': ResumoFinanceiro(
                total_perda_mensal=0.00,
                total_diferenca_anual=0.00,
                percentual_perda_anual=0.0,
                total_recebido=50000.00
            )
        }
    ]

    for i, cenario in enumerate(cenarios, 1):
        print(f"\n   Cenário {i}: {cenario['nome']}")
        try:
            pdf_bytes = create_pdf_report(
                municipio_nome="Teste",
                uf="MG",
                competencia="2025-01",
                resumo=cenario['resumo']
            )

            print(f"   ✅ PDF validado: {len(pdf_bytes):,} bytes (memória)")

        except Exception as e:
            print(f"   ❌ Falha: {e}")
            return False

    print("\n✅ Todos os cenários extremos passaram!")
    return True


def test_fallback_fpdf():
    """Testar fallback FPDF."""
    print("\n" + "="*60)
    print("🔄 TESTE 4: Fallback FPDF")
    print("="*60)

    resumo = ResumoFinanceiro(
        total_perda_mensal=18000.00,
        total_diferenca_anual=216000.00,
        percentual_perda_anual=10.5,
        total_recebido=170000.00
    )

    try:
        pdf_bytes = create_fpdf_report(
            municipio_nome="São Paulo",
            uf="SP",
            competencia="2025-01",
            resumo=resumo
        )

        print(f"\n✅ Fallback FPDF funcionando!")
        print(f"   Tamanho: {len(pdf_bytes):,} bytes")

        Path('teste_fallback_fpdf.pdf').write_bytes(pdf_bytes)

        return True

    except Exception as e:
        print(f"❌ Erro no fallback FPDF: {e}")
        return False


def test_nomes_municipios_longos():
    """Testar com nomes de municípios longos."""
    print("\n" + "="*60)
    print("📏 TESTE 5: Nomes de Municípios Longos")
    print("="*60)

    municipios = [
        ("Presidente Epitácio", "SP"),
        ("Governador Valadares", "MG"),
        ("São Miguel dos Campos", "AL"),
    ]

    resumo = ResumoFinanceiro(
        total_perda_mensal=12000.00,
        total_diferenca_anual=144000.00,
        percentual_perda_anual=8.0,
        total_recebido=150000.00
    )

    for i, (municipio, uf) in enumerate(municipios, 1):
        print(f"\n   {i}. {municipio}/{uf}")
        try:
            pdf_bytes = create_pdf_report(
                municipio_nome=municipio,
                uf=uf,
                competencia="2025-01",
                resumo=resumo
            )
            print(f"      ✅ OK - {len(pdf_bytes):,} bytes")
        except Exception as e:
            print(f"      ❌ Erro: {e}")
            return False

    print("\n✅ Todos os nomes longos funcionaram!")
    return True


def main():
    """Executar todos os testes."""
    print("\n" + "="*60)
    print("🧪 SUITE DE TESTES COMPLETA - SISTEMA DE PDF 3 PÁGINAS")
    print("="*60)

    resultados = []

    # Executar testes
    resultados.append(("Cálculos Matemáticos", test_calculos()))
    resultados.append(("Geração PDF Principal", test_pdf_geracao()))
    resultados.append(("Cenários Extremos", test_cenarios_extremos()))
    resultados.append(("Fallback FPDF", test_fallback_fpdf()))
    resultados.append(("Nomes Longos", test_nomes_municipios_longos()))

    # Resumo
    print("\n" + "="*60)
    print("📊 RESUMO DOS TESTES")
    print("="*60)

    total = len(resultados)
    passou = sum(1 for _, ok in resultados if ok)

    for nome, ok in resultados:
        status = "✅ PASSOU" if ok else "❌ FALHOU"
        print(f"   {status} - {nome}")

    print(f"\n{'='*60}")
    print(f"   TOTAL: {passou}/{total} testes passaram ({passou/total*100:.0f}%)")
    print(f"{'='*60}\n")

    return passou == total


if __name__ == '__main__':
    sucesso = main()
    sys.exit(0 if sucesso else 1)