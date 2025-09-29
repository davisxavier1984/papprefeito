#!/usr/bin/env python3
"""Script para testar o background da imagem no PDF."""

import sys
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent))

from app.services.relatorio_pdf import create_pdf_report
from app.models.schemas import ResumoFinanceiro


def main():
    print("🧪 Testando PDF com imagem de fundo (Timbrado)...")

    # Verificar se a imagem existe
    img_path = Path(__file__).parent / "templates" / "images" / "Imagem Timbrado.png"
    if img_path.exists():
        print(f"✅ Imagem encontrada: {img_path}")
        print(f"   Tamanho: {img_path.stat().st_size} bytes")
    else:
        print(f"❌ Imagem não encontrada: {img_path}")
        return False

    # Dados de teste
    resumo = ResumoFinanceiro(
        total_perca_mensal=15000.00,
        total_diferenca_anual=180000.00,
        percentual_perda_anual=12.5,
        total_recebido=120000.00
    )

    try:
        # Gerar PDF
        pdf_bytes = create_pdf_report(
            municipio_nome="Teste",
            uf="MG",
            competencia="2025-01",
            resumo=resumo
        )

        # Salvar
        output_path = Path(__file__).parent / "teste_com_timbrado.pdf"
        with open(output_path, "wb") as f:
            f.write(pdf_bytes)

        print(f"\n✅ PDF gerado: {output_path}")
        print(f"📏 Tamanho: {len(pdf_bytes):,} bytes")

        # Análise
        if len(pdf_bytes) > 50000:
            print("✅ Tamanho indica que a imagem foi incluída!")
        else:
            print("⚠️  Tamanho pequeno - imagem pode não estar incluída")
            print("   Verifique o caminho da imagem no CSS")

        return True

    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)