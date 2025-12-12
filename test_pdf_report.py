#!/usr/bin/env python3
"""Script de teste para o relatório PDF expandido."""

import sys
import os

# Adicionar o diretório backend ao Python path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

from app.models.schemas import ResumoFinanceiro
from app.services.relatorio_pdf import create_pdf_report

def test_scenario_1():
    """Teste 1: Valores pequenos."""
    resumo = ResumoFinanceiro(
        total_perda_mensal=100.0,
        total_diferenca_anual=1200.0,
        percentual_perda_anual=5.0,
        total_recebido=2000.0
    )

    pdf_bytes = create_pdf_report(
        municipio_nome="Belo Horizonte",
        uf="MG",
        competencia="Janeiro/2025",
        resumo=resumo
    )

    with open("teste_valores_pequenos.pdf", "wb") as f:
        f.write(pdf_bytes)

    print("✅ Teste 1 (valores pequenos) - PDF gerado: teste_valores_pequenos.pdf")

def test_scenario_2():
    """Teste 2: Valores grandes."""
    resumo = ResumoFinanceiro(
        total_perda_mensal=50000.0,
        total_diferenca_anual=600000.0,
        percentual_perda_anual=15.5,
        total_recebido=350000.0
    )

    pdf_bytes = create_pdf_report(
        municipio_nome="São Paulo",
        uf="SP",
        competencia="Janeiro/2025",
        resumo=resumo
    )

    with open("teste_valores_grandes.pdf", "wb") as f:
        f.write(pdf_bytes)

    print("✅ Teste 2 (valores grandes) - PDF gerado: teste_valores_grandes.pdf")

def test_scenario_3():
    """Teste 3: Nome longo."""
    resumo = ResumoFinanceiro(
        total_perda_mensal=25000.0,
        total_diferenca_anual=300000.0,
        percentual_perda_anual=8.7,
        total_recebido=120000.0
    )

    pdf_bytes = create_pdf_report(
        municipio_nome="Francisco Sá de Oliveira dos Santos",
        uf="MG",
        competencia="Janeiro/2025",
        resumo=resumo
    )

    with open("teste_nome_longo.pdf", "wb") as f:
        f.write(pdf_bytes)

    print("✅ Teste 3 (nome longo) - PDF gerado: teste_nome_longo.pdf")

def test_scenario_4():
    """Teste 4: Sem UF especificada."""
    resumo = ResumoFinanceiro(
        total_perda_mensal=15000.0,
        total_diferenca_anual=180000.0,
        percentual_perda_anual=12.3,
        total_recebido=75000.0
    )

    pdf_bytes = create_pdf_report(
        municipio_nome="Município Teste",
        uf=None,
        competencia="Janeiro/2025",
        resumo=resumo
    )

    with open("teste_sem_uf.pdf", "wb") as f:
        f.write(pdf_bytes)

    print("✅ Teste 4 (sem UF) - PDF gerado: teste_sem_uf.pdf")

if __name__ == "__main__":
    print("🚀 Iniciando testes do sistema de relatórios PDF...")
    print("📄 Gerando PDFs de teste para validação...")

    try:
        test_scenario_1()
        test_scenario_2()
        test_scenario_3()
        test_scenario_4()

        print("\n🎉 Todos os testes executados com sucesso!")
        print("📂 Arquivos PDF gerados na pasta raiz do projeto")
        print("📋 Verifique os PDFs para validar o layout e formatação")

    except Exception as e:
        print(f"❌ Erro durante os testes: {e}")
        import traceback
        traceback.print_exc()