#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste rápido do gráfico de projeção mensal
"""

import os
import sys
from datetime import datetime

def teste_rapido():
    """Teste rápido"""
    print("Teste rapido - Projecao mensal")
    
    try:
        from pdf_generator import PDFReportGenerator
        
        dados = {
            'pagamentos': [{
                'vlQualidadeEsf': 50000.0,
                'vlPagamentoEmultiQualidade': 15000.0,
                'vlPagamentoEsb40hQualidade': 8000.0,
                'dsClassificacaoQualidadeEsfEap': 'Bom',
                'noMunicipio': 'Teste',
                'sgUf': 'MG'
            }]
        }
        
        gerador = PDFReportGenerator()
        
        inicio = datetime.now()
        pdf_bytes = gerador.gerar_relatorio_pdf("Teste", "MG", dados)
        tempo = (datetime.now() - inicio).total_seconds()
        
        nome_arquivo = "teste_projecao_unico.pdf"
        with open(nome_arquivo, "wb") as f:
            f.write(pdf_bytes)
        
        tamanho_kb = len(pdf_bytes) / 1024
        print(f"OK PDF: {nome_arquivo} ({tamanho_kb:.1f} KB, {tempo:.1f}s)")
        
        return True
        
    except Exception as e:
        print(f"ERRO: {e}")
        return False

if __name__ == "__main__":
    teste_rapido()