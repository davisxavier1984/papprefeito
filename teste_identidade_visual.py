#!/usr/bin/env python3
"""
Teste da implementação da identidade visual da Mais Gestor no PDF
User Story US-004
"""

import json
import os
import sys
from datetime import datetime
from pdf_generator import PDFReportGenerator

def criar_dados_teste():
    """Cria dados de teste simulando resposta da API."""
    return {
        "pagamentos": [{
            "vlQualidadeEsf": 150000.00,
            "qtEsfHomologado": 15,
            "vlPagamentoEmultiQualidade": 75000.00,
            "qtEmultiPagas": 5,
            "vlPagamentoEsb40hQualidade": 45000.00,
            "qtSbPagamentoModalidadeI": 8,
        }]
    }

def teste_geracao_pdf():
    """Testa a geração do PDF com formatação simplificada."""
    print("Iniciando teste da formatação simplificada...")
    
    try:
        # Criar dados de teste
        dados_teste = criar_dados_teste()
        
        # Inicializar gerador
        gerador = PDFReportGenerator()
        print("OK: PDFReportGenerator inicializado com sucesso")
        
        # Testar sistema de cores simplificado
        print("Testando sistema de cores simplificado:")
        cores_esperadas = [
            'azul_principal', 'verde_positivo', 'vermelho_alerta', 'cinza_neutro'
        ]
        
        for cor in cores_esperadas:
            if cor in gerador.cores:
                print(f"  OK: {cor}: {gerador.cores[cor]}")
            else:
                print(f"  ERRO: {cor}: NAO ENCONTRADA")
        
        # Testar estilos tipográficos simplificados
        print("\nTestando sistema tipografico simplificado:")
        estilos_esperados = [
            'titulo', 'subtitulo', 'normal', 'destaque'
        ]
        
        for estilo in estilos_esperados:
            if estilo in gerador.estilos:
                print(f"  OK: {estilo}")
            else:
                print(f"  ERRO: {estilo}: NAO ENCONTRADO")
        
        # Gerar PDF de teste
        print("\nGerando PDF de teste...")
        nome_municipio = "Teste - Formatação Simplificada"
        
        # Tentar gerar o PDF
        pdf_bytes = gerador.gerar_relatorio_pdf(nome_municipio, "SP", dados_teste)
        
        if pdf_bytes and len(pdf_bytes) > 0:
            print(f"OK: PDF gerado com sucesso! Tamanho: {len(pdf_bytes)} bytes")
            
            # Salvar arquivo de teste
            nome_arquivo = f"teste_identidade_visual_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            with open(nome_arquivo, 'wb') as f:
                f.write(pdf_bytes)
            print(f"Arquivo PDF salvo como: {nome_arquivo}")
            
            # Verificar tamanho do arquivo
            tamanho_kb = len(pdf_bytes) / 1024
            if tamanho_kb < 200:  # Critério simplificado: <200KB
                print(f"OK: Tamanho otimizado: {tamanho_kb:.1f} KB (< 200KB)")
            else:
                print(f"AVISO: Arquivo pode ser menor: {tamanho_kb:.1f} KB")
            
            return True
        else:
            print("ERRO: Falha na geracao do PDF")
            return False
            
    except Exception as e:
        print(f"ERRO: Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()
        return False

def validar_criterios_aceite():
    """Valida se os critérios da formatação simplificada foram implementados."""
    print("\nValidando criterios da formatação simplificada:")
    
    try:
        gerador = PDFReportGenerator()
        
        criterios = {
            "Sistema de cores simplificado": {
                "azul_principal": 'azul_principal' in gerador.cores and gerador.cores['azul_principal'] is not None,
                "verde_positivo": 'verde_positivo' in gerador.cores and gerador.cores['verde_positivo'] is not None,
                "vermelho_alerta": 'vermelho_alerta' in gerador.cores and gerador.cores['vermelho_alerta'] is not None,
                "cinza_neutro": 'cinza_neutro' in gerador.cores and gerador.cores['cinza_neutro'] is not None
            },
            "Tipografia simplificada": {
                "titulo": 'titulo' in gerador.estilos,
                "subtitulo": 'subtitulo' in gerador.estilos,
                "normal": 'normal' in gerador.estilos,
                "destaque": 'destaque' in gerador.estilos
            },
            "Layout minimalista": {
                "cabecalho_simples": hasattr(gerador, '_criar_cabecalho'),
                "introducao": hasattr(gerador, '_criar_introducao'),
                "tabela_simples": hasattr(gerador, '_criar_tabela_cenarios'),
                "assinatura_limpa": hasattr(gerador, '_criar_assinatura')
            }
        }
        
        for categoria, itens in criterios.items():
            print(f"\n{categoria}:")
            for item, status in itens.items():
                status_text = "OK" if status else "ERRO"
                print(f"  {status_text}: {item}")
        
        # Calcular score geral
        total_itens = sum(len(itens) for itens in criterios.values())
        itens_ok = sum(sum(itens.values()) for itens in criterios.values())
        score = (itens_ok / total_itens) * 100
        
        print(f"\nScore de Implementacao: {score:.1f}% ({itens_ok}/{total_itens})")
        
        return score >= 90  # 90% de implementação considerado sucesso
        
    except Exception as e:
        print(f"ERRO: Erro na validacao: {e}")
        return False

if __name__ == "__main__":
    print("TESTE DA FORMATAÇÃO SIMPLIFICADA PDF - VERSÃO MINIMALISTA")
    print("=" * 60)
    
    # Executar testes
    sucesso_pdf = teste_geracao_pdf()
    sucesso_criterios = validar_criterios_aceite()
    
    print("\n" + "=" * 60)
    print("RESULTADO DOS TESTES:")
    print(f"  Geracao de PDF: {'PASSOU' if sucesso_pdf else 'FALHOU'}")
    print(f"  Criterios de Aceite: {'PASSOU' if sucesso_criterios else 'FALHOU'}")
    
    if sucesso_pdf and sucesso_criterios:
        print("\nFORMATAÇÃO SIMPLIFICADA IMPLEMENTADA COM SUCESSO!")
        sys.exit(0)
    else:
        print("\nALGUNS TESTES FALHARAM - VERIFICAR IMPLEMENTACAO")
        sys.exit(1)