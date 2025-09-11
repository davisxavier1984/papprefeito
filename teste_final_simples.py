#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste final simples da integração de gráficos no PDF
"""

import os
import sys
from datetime import datetime

def teste_simples():
    """Teste simples de integração"""
    print("TESTE FINAL - INTEGRACAO DOS GRAFICOS NO PDF")
    print("=" * 50)
    
    try:
        # Importar componentes
        from pdf_generator import PDFReportGenerator
        print("OK PDFReportGenerator importado")
        
        # Dados de exemplo
        dados_exemplo = {
            'pagamentos': [{
                'vlQualidadeEsf': 85000.0,
                'vlPagamentoEmultiQualidade': 25000.0,
                'vlPagamentoEsb40hQualidade': 15000.0,
                'qtEsfHomologado': 8,
                'qtEmultiPagas': 3,
                'qtSbPagamentoModalidadeI': 2,
                'dsClassificacaoQualidadeEsfEap': 'Bom',
                'noMunicipio': 'Municipio Teste',
                'sgUf': 'MG'
            }]
        }
        
        print("OK Dados carregados")
        
        # Criar gerador e gerar PDF
        gerador = PDFReportGenerator()
        print("OK Gerador criado")
        
        inicio = datetime.now()
        pdf_bytes = gerador.gerar_relatorio_pdf("Municipio Teste", "MG", dados_exemplo)
        tempo = (datetime.now() - inicio).total_seconds()
        
        tamanho_kb = len(pdf_bytes) / 1024
        nome_arquivo = f"teste_final_simples.pdf"
        
        with open(nome_arquivo, "wb") as f:
            f.write(pdf_bytes)
        
        print(f"OK PDF gerado: {nome_arquivo}")
        print(f"   Tamanho: {tamanho_kb:.1f} KB")
        print(f"   Tempo: {tempo:.2f}s")
        
        # Validações básicas
        if tamanho_kb > 150:
            print("OK PDF com graficos (tamanho adequado)")
        else:
            print("AVISO PDF sem graficos (tamanho pequeno)")
            
        print("\nSUCESSO - Integracao completa!")
        return True
        
    except Exception as e:
        print(f"ERRO: {e}")
        return False

if __name__ == "__main__":
    sucesso = teste_simples()
    sys.exit(0 if sucesso else 1)