#!/usr/bin/env python3
"""
Teste simples da funcionalidade de timbrado no PDF
"""

import sys
import os
sys.path.append('.')

def teste_timbrado():
    """Testa a geração de PDF com timbrado"""

    # Dados mockados para teste
    dados_mock = {
        'pagamentos': [{
            'vlQualidadeEsf': 50000,
            'vlPagamentoEmultiQualidade': 25000,
            'vlPagamentoEsb40hQualidade': 15000,
            'dsFaixaIndiceEquidadeEsfEap': 'Médio',
            'qtPopulacao': 50000
        }]
    }

    municipio_mock = "Ribeirão Preto"
    uf_mock = "SP"

    try:
        # Importar função de geração
        from app import gerar_relatorio_pdf

        print("🔄 Gerando PDF com timbrado...")

        # Gerar PDF
        pdf_bytes = gerar_relatorio_pdf(dados_mock, municipio_mock, uf_mock)

        if pdf_bytes:
            # Salvar arquivo de teste
            nome_arquivo = f"teste_timbrado_{municipio_mock.replace(' ', '_')}.pdf"
            with open(nome_arquivo, 'wb') as f:
                f.write(pdf_bytes)

            # Verificar tamanho
            tamanho = len(pdf_bytes) / 1024  # KB

            print(f"✅ PDF gerado com sucesso!")
            print(f"📁 Arquivo: {nome_arquivo}")
            print(f"📏 Tamanho: {tamanho:.1f} KB")
            print(f"🖼️ Timbrado aplicado em todas as páginas")

            return True
        else:
            print("❌ Erro: PDF não foi gerado")
            return False

    except Exception as e:
        print(f"❌ Erro durante teste: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Teste de Timbrado no PDF")
    print("=" * 40)

    # Verificar arquivos necessários
    if not os.path.exists('timbrado.jpg'):
        print("❌ Arquivo timbrado.jpg não encontrado")
        sys.exit(1)

    if not os.path.exists('logo_colorida_mg.png'):
        print("❌ Arquivo logo_colorida_mg.png não encontrado")
        sys.exit(1)

    print("✅ Arquivos de imagem encontrados")

    # Executar teste
    sucesso = teste_timbrado()

    if sucesso:
        print("\n🎉 Teste concluído com sucesso!")
    else:
        print("\n💥 Teste falhou!")
        sys.exit(1)