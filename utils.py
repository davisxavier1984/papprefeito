"""
Módulo de utilidades para o sistema papprefeito.
Combina as funcionalidades necessárias de formatação e API.
"""

# Importações de formatação - compatível com execução local e do diretório pai
try:
    from .formatting import (
        format_currency,
        parse_currency,
        currency_to_float,
        format_percentage,
        format_number,
        validate_numeric_input
    )
    from .api_client import (
        consultar_api,
        load_data_from_json,
        DATA_FILE
    )
except ImportError:
    from formatting import (
        format_currency,
        parse_currency,
        currency_to_float,
        format_percentage,
        format_number,
        validate_numeric_input
    )
    from api_client import (
        consultar_api,
        load_data_from_json,
        DATA_FILE
    )

# Lista de funções exportadas
__all__ = [
    # Funções de formatação
    "format_currency",
    "parse_currency", 
    "currency_to_float",
    "format_percentage",
    "format_number",
    "validate_numeric_input",
    
    # Funções de API
    "consultar_api",
    "load_data_from_json",
    "DATA_FILE",
    
    # Funções de vínculo e acompanhamento
    "extrair_dados_vinculo_acompanhamento",
    "criar_tabela_vinculo_acompanhamento",
    "criar_tabela_total_por_classificacao"
]

def extrair_dados_vinculo_acompanhamento(dados):
    """
    Extrai dados de classificação e valores de vínculo e acompanhamento para eSF e eAP.
    
    Args:
        dados: Dados completos da API
        
    Returns:
        Dict: Dados estruturados de vínculo e acompanhamento
    """
    import streamlit as st
    
    resultado = {
        'esf': {
            'tem_equipes': False,
            'classificacao_vinculo': None,
            'classificacao_qualidade': None, 
            'valor_vinculo': 0,
            'valor_qualidade': 0,
            'quantidade_equipes': 0
        },
        'eap': {
            'tem_equipes': False,
            'classificacao_vinculo': None,
            'classificacao_qualidade': None,
            'valor_vinculo': 0,
            'valor_qualidade': 0,
            'quantidade_equipes': 0
        }
    }
    
    try:
        pagamentos = dados.get('pagamentos', [])
        if not pagamentos:
            return resultado
            
        primeiro_pagamento = pagamentos[0]
        
        # Dados eSF
        qt_esf = primeiro_pagamento.get('qtEsfCredenciado', 0)
        if qt_esf > 0:
            resultado['esf'].update({
                'tem_equipes': True,
                'classificacao_vinculo': primeiro_pagamento.get('dsClassificacaoVinculoEsfEap'),
                'classificacao_qualidade': primeiro_pagamento.get('dsClassificacaoQualidadeEsfEap'),
                'valor_vinculo': primeiro_pagamento.get('vlVinculoEsf', 0),
                'valor_qualidade': primeiro_pagamento.get('vlQualidadeEsf', 0),
                'quantidade_equipes': qt_esf
            })
        
        # Dados eAP  
        qt_eap = primeiro_pagamento.get('qtEapCredenciadas', 0)
        if qt_eap > 0:
            resultado['eap'].update({
                'tem_equipes': True,
                'classificacao_vinculo': primeiro_pagamento.get('dsClassificacaoVinculoEsfEap'),
                'classificacao_qualidade': primeiro_pagamento.get('dsClassificacaoQualidadeEsfEap'),
                'valor_vinculo': primeiro_pagamento.get('vlVinculoEap', 0),
                'valor_qualidade': primeiro_pagamento.get('vlQualidadeEap', 0),
                'quantidade_equipes': qt_eap
            })
            
    except (KeyError, IndexError, TypeError) as e:
        if 'st' in globals():
            st.warning(f"⚠️ Erro ao extrair dados de vínculo e acompanhamento: {e}")
    
    return resultado

def criar_tabela_vinculo_acompanhamento(dados_vinculo):
    """
    Cria DataFrame formatado com dados de vínculo e acompanhamento para eSF e eAP.
    
    Args:
        dados_vinculo: Dados estruturados de vínculo e acompanhamento
        
    Returns:
        pd.DataFrame: Tabela formatada
    """
    import pandas as pd
    
    linhas = []
    
    # Processar eSF
    if dados_vinculo['esf']['tem_equipes']:
        esf_data = dados_vinculo['esf']
        linhas.append({
            'Tipo de Equipe': 'eSF - Equipes de Saúde da Família',
            'Qtd. Equipes': esf_data['quantidade_equipes'],
            'Classificação Vínculo': esf_data['classificacao_vinculo'] or 'Não informado',
            'Valor Vínculo (R$)': format_currency(esf_data['valor_vinculo']),
            'Classificação Qualidade': esf_data['classificacao_qualidade'] or 'Não informado',
            'Valor Qualidade (R$)': format_currency(esf_data['valor_qualidade']),
            'Total (R$)': format_currency(esf_data['valor_vinculo'] + esf_data['valor_qualidade'])
        })
    
    # Processar eAP
    if dados_vinculo['eap']['tem_equipes']:
        eap_data = dados_vinculo['eap']
        linhas.append({
            'Tipo de Equipe': 'eAP - Equipes de Atenção Primária',
            'Qtd. Equipes': eap_data['quantidade_equipes'],
            'Classificação Vínculo': eap_data['classificacao_vinculo'] or 'Não informado',
            'Valor Vínculo (R$)': format_currency(eap_data['valor_vinculo']),
            'Classificação Qualidade': eap_data['classificacao_qualidade'] or 'Não informado',
            'Valor Qualidade (R$)': format_currency(eap_data['valor_qualidade']),
            'Total (R$)': format_currency(eap_data['valor_vinculo'] + eap_data['valor_qualidade'])
        })
    
    return pd.DataFrame(linhas)

def criar_tabela_total_por_classificacao(dados):
    """
    Cria DataFrame com valores totais de vínculo e qualidade agrupados por classificação.
    Inclui eSF, eAP, eSB e eMulti com dados reais do município.
    
    Args:
        dados: Dados completos da API
        
    Returns:
        pd.DataFrame: Tabela com classificação e valor total
    """
    import pandas as pd
    
    # Valores de vínculo e qualidade completos do sistema
    VINCULO_VALUES = {
        'eSF': {'Ótimo': 8000, 'Bom': 6000, 'Suficiente': 4000, 'Regular': 2000},
        'eAP 30h': {'Ótimo': 4000, 'Bom': 3000, 'Suficiente': 2000, 'Regular': 1000},
        'eAP 20h': {'Ótimo': 3000, 'Bom': 2250, 'Suficiente': 1500, 'Regular': 750},
    }
    
    # Valores de qualidade completos (incluindo SB e eMulti)
    QUALITY_VALUES = {
        'eSF': {'Ótimo': 8000, 'Bom': 6000, 'Suficiente': 4000, 'Regular': 2000},
        'eAP 30h': {'Ótimo': 4000, 'Bom': 3000, 'Suficiente': 2000, 'Regular': 1000},
        'eAP 20h': {'Ótimo': 3000, 'Bom': 2250, 'Suficiente': 1500, 'Regular': 750},
        # eMulti values
        'eMULTI Ampl.': {'Ótimo': 9000, 'Bom': 6750, 'Suficiente': 4500, 'Regular': 2250},
        'eMULTI Compl.': {'Ótimo': 6000, 'Bom': 4500, 'Suficiente': 3000, 'Regular': 1500},
        'eMULTI Estrat.': {'Ótimo': 3000, 'Bom': 2250, 'Suficiente': 1500, 'Regular': 750},
        # eSB values
        'eSB Comum I': {'Ótimo': 2449, 'Bom': 1836.75, 'Suficiente': 1224.50, 'Regular': 612.25},
        'eSB Comum II': {'Ótimo': 3267, 'Bom': 2450.25, 'Suficiente': 1633.50, 'Regular': 816.75},
        'eSB Quil. Assent. I': {'Ótimo': 3673.50, 'Bom': 2755.13, 'Suficiente': 1836.75, 'Regular': 918.38},
        'eSB Quil. Assent. II': {'Ótimo': 4900.50, 'Bom': 3675.38, 'Suficiente': 2450.25, 'Regular': 1225.13},
        'eSB 20h': {'Ótimo': 2449, 'Bom': 1836.75, 'Suficiente': 1224.50, 'Regular': 612.25},
        'eSB 30h': {'Ótimo': 3267, 'Bom': 2450.25, 'Suficiente': 1633.50, 'Regular': 816.75}
    }
    
    # Extrair dados reais do município
    try:
        pagamentos = dados.get('pagamentos', [])
        if not pagamentos:
            return pd.DataFrame([{'Classificação': 'Sem dados', 'Valor Total': format_currency(0)}])
            
        primeiro_pagamento = pagamentos[0]
        
        # Extrair quantidades reais
        qtd_esf = primeiro_pagamento.get('qtEsfHomologado', 0)
        qtd_eap_30h = primeiro_pagamento.get('qtEapCredenciadas', 0)  # Assumindo 30h como padrão
        qtd_emulti = primeiro_pagamento.get('qtEmultiPagas', 0)
        qtd_esb = primeiro_pagamento.get('qtSbPagamentoModalidadeI', 0)
        
        # Extrair classificações específicas
        classificacao_esf_eap = primeiro_pagamento.get('dsClassificacaoQualidadeEsfEap', 'Bom')
        classificacao_emulti = primeiro_pagamento.get('dsClassificacaoQualidadeEmulti', 'Bom')
        
    except (KeyError, IndexError, TypeError):
        return pd.DataFrame([{'Classificação': 'Erro nos dados', 'Valor Total': format_currency(0)}])
    
    # Extrair dados de vínculo e acompanhamento para eSF/eAP
    dados_vinculo = extrair_dados_vinculo_acompanhamento(dados)
    
    # Calcular totais por classificação
    classificacoes = ['Ótimo', 'Bom', 'Suficiente', 'Regular']
    resultados = []
    
    for classificacao in classificacoes:
        valor_total = 0
        detalhes = []
        
        # eSF - Vínculo + Qualidade
        if dados_vinculo['esf']['tem_equipes']:
            quantidade_esf = dados_vinculo['esf']['quantidade_equipes']
            valor_vinculo_esf = VINCULO_VALUES['eSF'].get(classificacao, 0) * quantidade_esf
            valor_qualidade_esf = QUALITY_VALUES['eSF'].get(classificacao, 0) * quantidade_esf
            valor_total += valor_vinculo_esf + valor_qualidade_esf
            detalhes.append(f"eSF: {quantidade_esf}x{format_currency(valor_vinculo_esf + valor_qualidade_esf)}")
        
        # eAP - Vínculo + Qualidade (usando dados reais)
        if qtd_eap_30h > 0:
            valor_vinculo_eap = VINCULO_VALUES['eAP 30h'].get(classificacao, 0) * qtd_eap_30h
            valor_qualidade_eap = QUALITY_VALUES['eAP 30h'].get(classificacao, 0) * qtd_eap_30h
            valor_total += valor_vinculo_eap + valor_qualidade_eap
            detalhes.append(f"eAP: {qtd_eap_30h}x{format_currency(valor_vinculo_eap + valor_qualidade_eap)}")
        
        # eMulti - Apenas qualidade (assumindo Ampliada como padrão)
        if qtd_emulti > 0:
            # Usar classificação específica do eMulti
            classif_emulti = classificacao_emulti if classificacao == classificacao_emulti else classificacao
            valor_qualidade_emulti = QUALITY_VALUES['eMULTI Ampl.'].get(classif_emulti, 0) * qtd_emulti
            valor_total += valor_qualidade_emulti
            detalhes.append(f"eMulti: {qtd_emulti}x{format_currency(valor_qualidade_emulti)}")
        
        # eSB - Apenas qualidade (assumindo Comum I como padrão)
        if qtd_esb > 0:
            valor_qualidade_esb = QUALITY_VALUES['eSB Comum I'].get(classificacao, 0) * qtd_esb
            valor_total += valor_qualidade_esb
            detalhes.append(f"eSB: {qtd_esb}x{format_currency(valor_qualidade_esb)}")
        
        resultados.append({
            'Classificação': classificacao,
            'Valor Total': format_currency(valor_total),
            'Detalhes': ' | '.join(detalhes) if detalhes else 'Nenhuma equipe'
        })
    
    return pd.DataFrame(resultados)