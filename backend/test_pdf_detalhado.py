#!/usr/bin/env python3
"""
Script para testar a geração do relatório PDF detalhado
"""
import sys
import os
import asyncio

# Adicionar o diretório backend ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.relatorio_pdf import create_detailed_pdf_report, compute_financial_summary
from app.services.api_client import SaudeAPIClient

async def main_async():
    """Gera um PDF de teste do relatório detalhado."""

    # Município de teste: Ribeirão/PE (261180)
    codigo_municipio = "261180"
    municipio_nome = "Ribeirão"
    uf = "PE"
    competencia = "202509"

    print(f"Gerando relatório detalhado para {municipio_nome}/{uf} ({codigo_municipio}), competência {competencia}...")

    try:
        # Buscar dados da API
        print("Buscando dados da API de Saúde...")
        saude_api = SaudeAPIClient()
        dados = await saude_api.consultar_financiamento(codigo_municipio, competencia)

        if not dados or not dados.get('resumosPlanosOrcamentarios'):
            print("❌ Dados de financiamento não encontrados")
            return 1

        resumos = dados.get('resumosPlanosOrcamentarios', [])
        pagamentos = dados.get('pagamentos', [])

        print(f"Dados encontrados: {len(resumos)} resumos, {len(pagamentos)} pagamentos")

        # Calcular resumo financeiro
        perdas = [0.0] * len(resumos)  # Sem dados de perda para teste
        resumo = compute_financial_summary(resumos, perdas)

        print(f"Resumo: Total recebido R$ {resumo.total_recebido:,.2f}")

        # Gerar PDF
        print("Gerando PDF...")
        pdf_bytes = create_detailed_pdf_report(
            municipio_nome=municipio_nome,
            uf=uf,
            competencia=competencia,
            resumo=resumo,
            pagamentos=pagamentos
        )

        # Salvar PDF
        output_file = f"relatorio_detalhado_teste.pdf"
        with open(output_file, "wb") as f:
            f.write(pdf_bytes)

        print(f"✅ PDF gerado com sucesso: {output_file}")
        print(f"   Tamanho: {len(pdf_bytes):,} bytes")

        return 0

    except Exception as e:
        print(f"❌ Erro ao gerar PDF: {e}")
        import traceback
        traceback.print_exc()
        return 1

def main():
    """Wrapper síncrono para main_async."""
    return asyncio.run(main_async())

if __name__ == "__main__":
    sys.exit(main())
