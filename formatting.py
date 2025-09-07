"""
Utilitários de formatação para o sistema papprefeito.
Funções para formatação de moeda, números e porcentagens.
"""
import streamlit as st
from typing import Union

def format_currency(value: Union[str, int, float]) -> str:
    """
    Formata um número como moeda brasileira.
    
    Args:
        value: Valor a ser formatado (float, int ou str)
        
    Returns:
        str: Valor formatado como moeda brasileira
    """
    if value == 'Sem cálculo':
        return value
    
    # Converte para float se necessário
    if isinstance(value, str):
        try:
            # Remove símbolos de moeda e converte separadores
            value = value.replace('R$', '').strip().replace('.', '').replace(',', '.')
            value = float(value)
        except ValueError:
            st.warning(f"Valor inválido para formatação: {value}")
            return "Valor inválido"
    
    try:
        # Formata como moeda brasileira
        return f"R$ {float(value):,.2f}".replace(",", "@").replace(".", ",").replace("@", ".")
    except (ValueError, TypeError):
        return "R$ 0,00"

def parse_currency(value_str: Union[str, int, float]) -> float:
    """
    Converte string de moeda para float.
    
    Args:
        value_str: String representando valor monetário
        
    Returns:
        float: Valor numérico
    """
    try:
        if isinstance(value_str, str):
            return float(value_str.replace('R$ ', '').replace('R$', '').replace('.', '').replace(',', '.').strip())
        return float(value_str)
    except (ValueError, TypeError):
        return 0.0

def currency_to_float(value: Union[str, int, float]) -> float:
    """
    Converte uma string de moeda brasileira (R$) para um número float.
    Função principal para conversão de moeda.
    
    Args:
        value: Valor a converter, pode ser string ou número
        
    Returns:
        float: Valor numérico convertido
    """
    if value == 'Sem cálculo' or not value:
        return 0.0
        
    if isinstance(value, str):
        try:
            # Remove "R$" e espaços, e substitui separadores
            cleaned_value = value.replace('R$', '').strip().replace('.', '').replace(',', '.')
            return float(cleaned_value)
        except ValueError:
            st.warning(f"Valor inválido para conversão: {value}")
            return 0.0
    
    try:
        # Se já for um número, retorna diretamente
        return float(value)
    except (ValueError, TypeError):
        return 0.0

def format_percentage(value: Union[str, int, float], decimals: int = 2) -> str:
    """
    Formata um número como porcentagem.
    
    Args:
        value: Valor a ser formatado
        decimals: Número de casas decimais
        
    Returns:
        str: Valor formatado como porcentagem
    """
    try:
        return f"{float(value):.{decimals}f}%"
    except (ValueError, TypeError):
        return f"0.{'0' * decimals}%"

def format_number(value: Union[str, int, float], decimals: int = 2) -> str:
    """
    Formata um número com separadores de milhares.
    
    Args:
        value: Valor a ser formatado
        decimals: Número de casas decimais
        
    Returns:
        str: Valor formatado
    """
    try:
        return f"{float(value):,.{decimals}f}".replace(",", "@").replace(".", ",").replace("@", ".")
    except (ValueError, TypeError):
        return f"0,{'0' * decimals}"

def validate_numeric_input(value: Union[str, int, float], field_name: str = "Valor") -> float:
    """
    Valida e converte entrada numérica com tratamento de erro robusto.
    
    Args:
        value: Valor a ser validado
        field_name: Nome do campo para mensagens de erro
        
    Returns:
        float: Valor validado ou 0.0 se inválido
    """
    try:
        if value is None or value == "":
            return 0.0
        
        if isinstance(value, str):
            # Remove espaços e caracteres especiais comuns
            cleaned = value.strip().replace('R$', '').replace('.', '').replace(',', '.')
            return float(cleaned)
        
        return float(value)
    except (ValueError, TypeError):
        st.warning(f"⚠️ {field_name} inválido: {value}. Usando 0.0 como valor padrão.")
        return 0.0