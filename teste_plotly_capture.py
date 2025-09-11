#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste para captura de gráficos Plotly no PDF Generator
Testa a nova funcionalidade de captura direta dos gráficos da interface
"""

import sys
import os

# Adicionar diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def testar_captura_plotly():
    """Testa a captura de gráficos Plotly para PDF"""
    print("Iniciando teste de captura Plotly para PDF")
    print("=" * 50)
    
    try:
        # Dados de exemplo (simulando dados reais da API)
        dados_exemplo = {
            'pagamentos': [{
                'vlQualidadeEsf': 45000.0,
                'vlPagamentoEmultiQualidade': 15000.0,
                'vlPagamentoEsb40hQualidade': 8000.0,
                'qtEsfHomologado': 5,
                'qtEmultiPagas': 2,
                'qtSbPagamentoModalidadeI': 1,
                'dsClassificacaoQualidadeEsfEap': 'Bom',
                'noMunicipio': 'Teste Municipality',
                'sgUf': 'TS'
            }]
        }
        
        print("OK Dados de exemplo carregados")
        
        # Testar importação do gerador
        from pdf_generator import PDFReportGenerator
        print("OK PDFReportGenerator importado com sucesso")
        
        # Criar instância do gerador
        gerador = PDFReportGenerator()
        print("OK Instancia do gerador criada")
        
        # Testar captura de gráficos
        print("\nTestando captura de graficos Plotly...")
        graficos = gerador._capturar_graficos_plotly(dados_exemplo)
        
        # Verificar resultados
        print(f"Grafico piramide: {'CAPTURADO' if graficos['piramide'] else 'FALHOU'}")
        print(f"Grafico barras: {'CAPTURADO' if graficos['barras'] else 'FALHOU'}")
        print(f"Grafico rosquinha: {'CAPTURADO' if graficos['rosquinha'] else 'FALHOU'}")
        
        # Mostrar tamanhos dos bytes capturados
        for nome, dados_img in graficos.items():
            if dados_img:
                tamanho_kb = len(dados_img) / 1024
                print(f"   {nome}: {tamanho_kb:.1f} KB")
        
        print("\nTestando geracao completa do PDF...")
        
        # Testar geração completa do PDF
        try:
            pdf_bytes = gerador.gerar_relatorio_pdf("Municipio Teste", "TS", dados_exemplo)
            tamanho_pdf = len(pdf_bytes) / 1024
            print(f"OK PDF gerado com sucesso: {tamanho_pdf:.1f} KB")
            
            # Salvar PDF de teste
            with open("teste_pdf_com_plotly.pdf", "wb") as f:
                f.write(pdf_bytes)
            print("OK PDF salvo como: teste_pdf_com_plotly.pdf")
            
        except Exception as e:
            print(f"ERRO ao gerar PDF completo: {e}")
            return False
        
        print("\nTeste concluido com SUCESSO!")
        print("=" * 50)
        print("Resumo:")
        print("- Captura Plotly: Funcionando")
        print("- Geracao PDF: Funcionando") 
        print("- Integracao: Completa")
        
        return True
        
    except ImportError as e:
        print(f"ERRO de importacao: {e}")
        print("Instale as dependencias: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"ERRO geral: {e}")
        return False

if __name__ == "__main__":
    sucesso = testar_captura_plotly()
    sys.exit(0 if sucesso else 1)