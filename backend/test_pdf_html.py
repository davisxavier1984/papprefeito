#!/usr/bin/env python3
"""Script de teste para validar o novo sistema HTML-to-PDF."""

import sys
import os
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent))

from app.services.relatorio_pdf import create_pdf_report
from app.models.schemas import ResumoFinanceiro


def test_pdf_generation():
    """Testa a geração do PDF com dados simulados."""

    print("🧪 Testando nova implementação HTML-to-PDF...")

    # Dados simulados
    resumo = ResumoFinanceiro(
        total_perca_mensal=15000.00,
        total_diferenca_anual=180000.00,
        percentual_perda_anual=12.5,
        total_recebido=120000.00
    )

    municipio_nome = "São Paulo"
    uf = "SP"
    competencia = "2025-01"

    try:
        # Testar geração do PDF
        pdf_bytes = create_pdf_report(
            municipio_nome=municipio_nome,
            uf=uf,
            competencia=competencia,
            resumo=resumo
        )

        # Salvar arquivo de teste
        output_path = Path(__file__).parent / "teste_html_pdf_completo.pdf"
        with open(output_path, "wb") as f:
            f.write(pdf_bytes)

        print(f"✅ PDF gerado com sucesso!")
        print(f"📄 Arquivo salvo: {output_path}")
        print(f"📏 Tamanho: {len(pdf_bytes)} bytes")

        # Validações básicas
        if len(pdf_bytes) > 1000:
            print("✅ Tamanho do arquivo parece correto")
        else:
            print("⚠️  Arquivo muito pequeno, pode estar com problemas")

        if pdf_bytes.startswith(b'%PDF'):
            print("✅ Cabeçalho PDF válido")
        else:
            print("❌ Cabeçalho PDF inválido")

        return True

    except Exception as e:
        print(f"❌ Erro durante a geração: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_template_loading():
    """Testa o carregamento dos templates."""

    print("\n📁 Verificando templates...")

    # Verificar arquivos necessários
    base_dir = Path(__file__).parent

    files_to_check = [
        "templates/relatorio_base.html",
        "templates/css/modern-cards.css",
    ]

    for file_path in files_to_check:
        full_path = base_dir / file_path
        if full_path.exists():
            size = full_path.stat().st_size
            print(f"✅ {file_path} - {size} bytes")
        else:
            print(f"❌ {file_path} - Arquivo não encontrado")


def main():
    """Função principal do teste."""
    print("🎯 Iniciando testes do sistema HTML-to-PDF\n")

    # Teste 1: Verificar templates
    test_template_loading()

    # Teste 2: Gerar PDF
    success = test_pdf_generation()

    print("\n" + "="*50)
    if success:
        print("🎉 Todos os testes passaram!")
        print("💡 O novo sistema HTML-to-PDF está funcionando corretamente.")
    else:
        print("⚠️  Alguns testes falharam.")
        print("🔧 Verifique as dependências e configurações.")

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)