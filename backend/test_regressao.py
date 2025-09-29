#!/usr/bin/env python3
"""Testes de regressão - Validar que funcionalidades existentes não quebraram."""

import sys
from pathlib import Path

sys.path.append('.')

from app.models.schemas import ResumoFinanceiro
from app.services.relatorio_pdf import (
    compute_financial_summary,
    _br_number,
    _sanitize_text,
    _safe_ratio,
    create_fpdf_report,
    create_html_pdf_report,
    create_pdf_report
)


def test_funcoes_auxiliares():
    """Testar funções auxiliares não foram quebradas."""
    print("\n" + "="*60)
    print("🔧 TESTE DE REGRESSÃO 1: Funções Auxiliares")
    print("="*60)

    # Teste 1: Formatação brasileira
    assert _br_number(1234567.89, 2) == "1.234.567,89", "❌ _br_number quebrou!"
    assert _br_number(1000.50, 0) == "1.000", "❌ _br_number (sem decimais) quebrou!"
    print("   ✅ _br_number funcionando")

    # Teste 2: Sanitização de texto
    texto = "São Paulo - Município"
    resultado = _sanitize_text(texto)
    assert len(resultado) > 0, "❌ _sanitize_text quebrou!"
    print("   ✅ _sanitize_text funcionando")

    # Teste 3: Cálculo de razão segura
    assert _safe_ratio(50, 100) == 0.5, "❌ _safe_ratio quebrou!"
    assert _safe_ratio(100, 0) == 0.0, "❌ _safe_ratio (divisão por zero) quebrou!"
    assert _safe_ratio(-10, 100) == 0.0, "❌ _safe_ratio (valor negativo) quebrou!"
    print("   ✅ _safe_ratio funcionando")

    print("\n✅ Todas as funções auxiliares OK!")
    return True


def test_compute_financial_summary():
    """Testar cálculo de resumo financeiro."""
    print("\n" + "="*60)
    print("💰 TESTE DE REGRESSÃO 2: Compute Financial Summary")
    print("="*60)

    # Dados de teste
    resumos = [
        {'vlEfetivoRepasse': 10000.00},
        {'vlEfetivoRepasse': 15000.00},
        {'vlEfetivoRepasse': 12000.00}
    ]
    percas = [1000.00, 1500.00, 1200.00]

    resultado = compute_financial_summary(resumos, percas)

    # Validações
    assert resultado.total_recebido == 37000.00, f"❌ Total recebido errado: {resultado.total_recebido}"
    assert resultado.total_perca_mensal == 3700.00, f"❌ Perda mensal errada: {resultado.total_perca_mensal}"
    assert resultado.total_diferenca_anual == 44400.00, f"❌ Diferença anual errada: {resultado.total_diferenca_anual}"

    print(f"   Total Recebido: R$ {resultado.total_recebido:,.2f} ✅")
    print(f"   Perda Mensal: R$ {resultado.total_perca_mensal:,.2f} ✅")
    print(f"   Diferença Anual: R$ {resultado.total_diferenca_anual:,.2f} ✅")
    print(f"   Percentual: {resultado.percentual_perda_anual:.2f}% ✅")

    print("\n✅ Compute Financial Summary OK!")
    return True


def test_geracao_fpdf_legado():
    """Testar que geração FPDF legada ainda funciona."""
    print("\n" + "="*60)
    print("📄 TESTE DE REGRESSÃO 3: Geração FPDF Legada")
    print("="*60)

    resumo = ResumoFinanceiro(
        total_perca_mensal=10000.00,
        total_diferenca_anual=120000.00,
        percentual_perda_anual=10.0,
        total_recebido=100000.00
    )

    try:
        pdf_bytes = create_fpdf_report(
            municipio_nome="Teste Regressão",
            uf="MG",
            competencia="202501",
            resumo=resumo
        )

        assert len(pdf_bytes) > 1000, "❌ PDF FPDF muito pequeno!"
        assert pdf_bytes[:4] == b'%PDF', "❌ Arquivo não é PDF válido!"

        print(f"   ✅ FPDF validado: {len(pdf_bytes):,} bytes (memória)")
        print("   ✅ Formato PDF válido")
        print("\n✅ FPDF legado OK!")
        return True

    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False


def test_geracao_html_pdf():
    """Testar geração HTML-to-PDF."""
    print("\n" + "="*60)
    print("🎨 TESTE DE REGRESSÃO 4: Geração HTML-to-PDF")
    print("="*60)

    resumo = ResumoFinanceiro(
        total_perca_mensal=15000.00,
        total_diferenca_anual=180000.00,
        percentual_perda_anual=12.0,
        total_recebido=125000.00
    )

    try:
        pdf_bytes = create_html_pdf_report(
            municipio_nome="Teste HTML",
            uf="SP",
            competencia="202501",
            resumo=resumo
        )

        assert len(pdf_bytes) > 5000, "❌ PDF HTML muito pequeno!"
        assert pdf_bytes[:4] == b'%PDF', "❌ Arquivo não é PDF válido!"

        print(f"   ✅ HTML-to-PDF validado: {len(pdf_bytes):,} bytes (memória)")
        print("   ✅ Formato PDF válido")
        print("\n✅ HTML-to-PDF OK!")
        return True

    except Exception as e:
        print(f"   ❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_funcao_principal_create_pdf():
    """Testar função principal de geração de PDF."""
    print("\n" + "="*60)
    print("🎯 TESTE DE REGRESSÃO 5: Função Principal create_pdf_report")
    print("="*60)

    resumo = ResumoFinanceiro(
        total_perca_mensal=20000.00,
        total_diferenca_anual=240000.00,
        percentual_perda_anual=15.0,
        total_recebido=160000.00
    )

    try:
        # Teste com todos os parâmetros
        pdf_bytes = create_pdf_report(
            municipio_nome="Teste Principal",
            uf="RJ",
            competencia="202501",
            resumo=resumo
        )

        assert len(pdf_bytes) > 5000, "❌ PDF principal muito pequeno!"
        print(f"   ✅ PDF principal validado: {len(pdf_bytes):,} bytes (memória)")

        # Teste com parâmetros opcionais None
        pdf_bytes2 = create_pdf_report(
            municipio_nome=None,
            uf=None,
            competencia="202501",
            resumo=resumo
        )

        assert len(pdf_bytes2) > 5000, "❌ PDF com None muito pequeno!"
        print(f"   ✅ PDF com None validado: {len(pdf_bytes2):,} bytes (memória)")

        print("\n✅ Função principal OK!")
        return True

    except Exception as e:
        print(f"   ❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_compatibilidade_com_dados_reais():
    """Testar com dados próximos aos reais da API."""
    print("\n" + "="*60)
    print("🔍 TESTE DE REGRESSÃO 6: Compatibilidade com Dados Reais")
    print("="*60)

    # Simular dados mais realistas
    resumos_simulados = [
        {'vlEfetivoRepasse': 250000.00},
        {'vlEfetivoRepasse': 180000.00},
        {'vlEfetivoRepasse': 320000.00},
        {'vlEfetivoRepasse': 275000.00}
    ]

    percas_simuladas = [25000.00, 18000.00, 32000.00, 27500.00]

    try:
        resumo = compute_financial_summary(resumos_simulados, percas_simuladas)

        pdf_bytes = create_pdf_report(
            municipio_nome="Município de Grande Porte",
            uf="MG",
            competencia="202412",
            resumo=resumo
        )

        assert len(pdf_bytes) > 5000, "❌ PDF com dados reais muito pequeno!"

        print(f"   Total Recebido: R$ {resumo.total_recebido:,.2f}")
        print(f"   Perda Mensal: R$ {resumo.total_perca_mensal:,.2f}")
        print(f"   Diferença Anual: R$ {resumo.total_diferenca_anual:,.2f}")
        print(f"   PDF validado: {len(pdf_bytes):,} bytes (memória)")

        print("\n✅ Compatibilidade com dados reais OK!")
        return True

    except Exception as e:
        print(f"   ❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Executar todos os testes de regressão."""
    print("\n" + "="*60)
    print("🧪 SUITE DE TESTES DE REGRESSÃO")
    print("="*60)
    print("\n📌 Objetivo: Garantir que nenhuma funcionalidade existente foi quebrada")

    resultados = []

    # Executar testes
    resultados.append(("Funções Auxiliares", test_funcoes_auxiliares()))
    resultados.append(("Compute Financial Summary", test_compute_financial_summary()))
    resultados.append(("FPDF Legado", test_geracao_fpdf_legado()))
    resultados.append(("HTML-to-PDF", test_geracao_html_pdf()))
    resultados.append(("Função Principal", test_funcao_principal_create_pdf()))
    resultados.append(("Dados Reais", test_compatibilidade_com_dados_reais()))

    # Resumo
    print("\n" + "="*60)
    print("📊 RESUMO DOS TESTES DE REGRESSÃO")
    print("="*60)

    total = len(resultados)
    passou = sum(1 for _, ok in resultados if ok)

    for nome, ok in resultados:
        status = "✅ PASSOU" if ok else "❌ FALHOU"
        print(f"   {status} - {nome}")

    print(f"\n{'='*60}")
    print(f"   TOTAL: {passou}/{total} testes passaram ({passou/total*100:.0f}%)")
    print(f"{'='*60}\n")

    if passou == total:
        print("🎉 NENHUMA REGRESSÃO DETECTADA! Sistema estável.")
    else:
        print("⚠️  REGRESSÕES DETECTADAS! Revise os erros acima.")

    return passou == total


if __name__ == '__main__':
    sucesso = main()
    sys.exit(0 if sucesso else 1)