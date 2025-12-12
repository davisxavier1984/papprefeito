#!/usr/bin/env python3
"""Teste de integração do endpoint /relatorios/pdf."""

import sys
import asyncio
from pathlib import Path

sys.path.append('.')

from app.models.schemas import RelatorioPDFRequest, ResumoFinanceiro
from app.services.relatorio_pdf import create_pdf_report


def test_endpoint_simulation():
    """Simular comportamento do endpoint sem servidor rodando."""
    print("\n" + "="*60)
    print("🌐 TESTE DE INTEGRAÇÃO: Endpoint /relatorios/pdf")
    print("="*60)

    # Simular dados de requisição
    request = RelatorioPDFRequest(
        codigo_ibge="3106200",  # Belo Horizonte
        competencia="202412",  # Formato AAAAMM
        municipio_nome="Belo Horizonte",
        uf="MG"
    )

    # Simular resumo financeiro (normalmente viria da API)
    resumo = ResumoFinanceiro(
        total_perda_mensal=45000.00,
        total_diferenca_anual=540000.00,
        percentual_perda_anual=18.5,
        total_recebido=290000.00
    )

    print(f"\n📋 Requisição:")
    print(f"   Município: {request.municipio_nome}/{request.uf}")
    print(f"   IBGE: {request.codigo_ibge}")
    print(f"   Competência: {request.competencia}")

    print(f"\n💰 Resumo Financeiro:")
    print(f"   Recebido: R$ {resumo.total_recebido:,.2f}")
    print(f"   Perda Mensal: R$ {resumo.total_perda_mensal:,.2f}")
    print(f"   Diferença Anual: R$ {resumo.total_diferenca_anual:,.2f}")
    print(f"   Percentual: {resumo.percentual_perda_anual:.2f}%")

    try:
        # Gerar PDF (mesmo fluxo do endpoint)
        pdf_bytes = create_pdf_report(
            municipio_nome=request.municipio_nome,
            uf=request.uf,
            competencia=request.competencia,
            resumo=resumo
        )

        # Nome do arquivo (mesmo padrão do endpoint)
        file_name = f"relatorio_{request.codigo_ibge}_{request.competencia}.pdf"

        print(f"\n✅ PDF gerado com sucesso!")
        print(f"   Tamanho: {len(pdf_bytes):,} bytes ({len(pdf_bytes)/1024:.1f} KB)")
        print(f"   Nome: {file_name} (não salvo - validação em memória)")

        # Validações (sem salvar em disco)
        assert len(pdf_bytes) > 5000, "❌ PDF muito pequeno!"
        assert pdf_bytes[:4] == b'%PDF', "❌ Arquivo não é um PDF válido!"

        print("\n✅ Endpoint funcionando corretamente!")
        return True

    except Exception as e:
        print(f"\n❌ Erro no endpoint: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_validacao_schema():
    """Validar schema de requisição."""
    print("\n" + "="*60)
    print("📝 TESTE: Validação de Schema")
    print("="*60)

    # Teste 1: Requisição válida
    try:
        request = RelatorioPDFRequest(
            codigo_ibge="3550308",
            competencia="202501",  # Formato AAAAMM
            municipio_nome="São Paulo",
            uf="SP"
        )
        print(f"\n✅ Schema válido:")
        print(f"   {request.municipio_nome}/{request.uf} - {request.codigo_ibge}")
    except Exception as e:
        print(f"\n❌ Erro no schema: {e}")
        return False

    # Teste 2: Campos opcionais
    try:
        request2 = RelatorioPDFRequest(
            codigo_ibge="3106200",
            competencia="202411",  # Formato AAAAMM
            municipio_nome=None,
            uf=None
        )
        print(f"\n✅ Schema com campos opcionais OK")
    except Exception as e:
        print(f"\n❌ Erro com campos opcionais: {e}")
        return False

    print("\n✅ Validação de schema completa!")
    return True


def test_diferentes_municipios():
    """Testar endpoint com diferentes municípios."""
    print("\n" + "="*60)
    print("🏙️ TESTE: Múltiplos Municípios")
    print("="*60)

    municipios = [
        {"codigo_ibge": "3550308", "nome": "São Paulo", "uf": "SP"},
        {"codigo_ibge": "3106200", "nome": "Belo Horizonte", "uf": "MG"},
        {"codigo_ibge": "3304557", "nome": "Rio de Janeiro", "uf": "RJ"},
        {"codigo_ibge": "5300108", "nome": "Brasília", "uf": "DF"},
    ]

    resumo = ResumoFinanceiro(
        total_perda_mensal=30000.00,
        total_diferenca_anual=360000.00,
        percentual_perda_anual=14.0,
        total_recebido=215000.00
    )

    for i, mun in enumerate(municipios, 1):
        print(f"\n   {i}. {mun['nome']}/{mun['uf']} (IBGE: {mun['codigo_ibge']})")

        try:
            pdf_bytes = create_pdf_report(
                municipio_nome=mun['nome'],
                uf=mun['uf'],
                competencia="202501",
                resumo=resumo
            )

            # Validar sem salvar em disco
            assert len(pdf_bytes) > 5000, "PDF muito pequeno"
            assert pdf_bytes[:4] == b'%PDF', "Formato inválido"

            print(f"      ✅ PDF validado: {len(pdf_bytes):,} bytes (memória)")

        except Exception as e:
            print(f"      ❌ Erro: {e}")
            return False

    print("\n✅ Todos os municípios testados com sucesso!")
    return True


def main():
    """Executar todos os testes de integração."""
    print("\n" + "="*60)
    print("🧪 TESTES DE INTEGRAÇÃO - ENDPOINT /relatorios/pdf")
    print("="*60)

    resultados = []

    # Executar testes
    resultados.append(("Simulação Endpoint", test_endpoint_simulation()))
    resultados.append(("Validação Schema", test_validacao_schema()))
    resultados.append(("Múltiplos Municípios", test_diferentes_municipios()))

    # Resumo
    print("\n" + "="*60)
    print("📊 RESUMO DOS TESTES DE INTEGRAÇÃO")
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
        print("🎉 ENDPOINT /relatorios/pdf ESTÁ FUNCIONANDO PERFEITAMENTE!")
    else:
        print("⚠️  Alguns testes falharam. Revise os erros acima.")

    return passou == total


if __name__ == '__main__':
    sucesso = main()
    sys.exit(0 if sucesso else 1)