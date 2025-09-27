import streamlit as st
import pandas as pd
import json
from pyUFbr.baseuf import ufbr
import os
from api_client import consultar_api, get_latest_competencia
from formatting import format_currency

# Configuração da página
st.set_page_config(
    page_title="Consulta Dados APS - papprefeito",
    page_icon="🏛️",
    layout="wide"
)

# Cache para dados dos municípios
CACHE_FILE = "data_cache_papprefeito.json"
EDITED_DATA_FILE = "municipios_editados.json"

def load_cache():
    """Carrega dados do cache"""
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_cache(data):
    """Salva dados no cache"""
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_edited_data():
    """Carrega dados editados dos municípios"""
    if os.path.exists(EDITED_DATA_FILE):
        with open(EDITED_DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_edited_data(data):
    """Salva dados editados dos municípios"""
    with open(EDITED_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_municipios(uf):
    """Busca municípios por UF usando a biblioteca pyUFbr"""
    try:
        municipios = ufbr.list_cidades(uf)
        return municipios
    except Exception as e:
        st.error(f"Erro ao buscar municípios: {e}")
        return []

def get_codigo_ibge(municipio_nome):
    """Obtém código IBGE do município"""
    try:
        codigo_ibge = ufbr.get_cidade(municipio_nome).codigo
        # Remove último dígito conforme lógica original
        codigo_ibge = str(int(float(codigo_ibge)))[:-1]
        return codigo_ibge
    except Exception as e:
        st.error(f"Erro ao obter código IBGE: {e}")
        return None

# Função consultar_api agora é importada do api_client.py

# Funções format_currency agora é importada do formatting.py

# Interface Principal
st.title("🏛️ Sistema papprefeito")
st.subheader("Consulta e Edição de Dados de Financiamento APS")

# Sidebar para seleção
st.sidebar.header("Seleção de Parâmetros")

# Seleção de UF usando pyUFbr
ufs = ufbr.list_uf
selected_uf = st.sidebar.selectbox("Selecione a UF:", [""] + sorted(ufs))

# Seleção de Município
selected_municipio = None
cod_municipio = None

if selected_uf:
    with st.spinner(f"Carregando municípios de {selected_uf}..."):
        municipios = get_municipios(selected_uf)

    if municipios:
        selected_municipio = st.sidebar.selectbox(
            "Selecione o Município:",
            [""] + sorted(municipios)
        )

        if selected_municipio:
            cod_municipio = get_codigo_ibge(selected_municipio)
    else:
        st.sidebar.warning("Erro ao carregar municípios")

# Seleção de Competência (usar última disponível por padrão)
competencia_default = get_latest_competencia()
competencia = st.sidebar.text_input("Competência (AAAAMM):", value=competencia_default)

# Botão de consulta
if st.sidebar.button("🔍 Consultar"):
    if selected_uf and cod_municipio and competencia:
        with st.spinner("Consultando dados..."):
            # Criar chave para cache
            cache_key = f"{cod_municipio}_{competencia}"

            # Verificar cache
            cache_data = load_cache()

            if cache_key in cache_data:
                st.info("Dados carregados do cache")
                dados_api = cache_data[cache_key]
            else:
                dados_api = consultar_api(cod_municipio, competencia)
                if dados_api:
                    # Salvar no cache
                    cache_data[cache_key] = dados_api
                    save_cache(cache_data)
                    st.success("Dados consultados e salvos no cache")

            if dados_api:
                st.session_state.dados_api = dados_api
                st.session_state.municipio_info = {
                    'uf': selected_uf,
                    'codigo': cod_municipio,
                    'nome': selected_municipio,
                    'competencia': competencia
                }
    else:
        st.warning("Preencha todos os campos antes de consultar")

# Exibição dos dados
if 'dados_api' in st.session_state and 'municipio_info' in st.session_state:
    municipio_info = st.session_state.municipio_info
    dados_api = st.session_state.dados_api

    st.markdown("---")
    st.subheader(f"📊 Dados: {municipio_info['nome']}/{municipio_info['uf']} - {municipio_info['competencia']}")

    # Exibir dados do cache diretamente se disponíveis
    cache_data = load_cache()
    if cache_data:
        for cache_key, dados in cache_data.items():
            if 'resumosPlanosOrcamentarios' in dados:
                resumos = dados['resumosPlanosOrcamentarios']

                # Extrair dados para métricas dos resumos
                estrato = 'N/A'
                populacao = 0

                # Buscar nos resumos pelos campos necessários
                for resumo in resumos:
                    if 'dsFaixaIndiceEquidadeEsfEap' in resumo:
                        estrato = resumo['dsFaixaIndiceEquidadeEsfEap']
                    if 'qtPopulacao' in resumo:
                        populacao = resumo['qtPopulacao']

                # Buscar nos pagamentos pelos campos de estrato e população (local correto)
                pagamentos = dados.get('pagamentos', [])
                if pagamentos:
                    primeiro_pagamento = pagamentos[0]
                    if 'dsFaixaIndiceEquidadeEsfEap' in primeiro_pagamento:
                        estrato = primeiro_pagamento['dsFaixaIndiceEquidadeEsfEap']
                    if 'qtPopulacao' in primeiro_pagamento:
                        populacao = primeiro_pagamento['qtPopulacao']

                # Cards de métricas
                col1, col2 = st.columns(2)

                with col1:
                    st.metric(
                        label="Estrato",
                        value=estrato
                    )

                with col2:
                    st.metric(
                        label="População",
                        value=f"{populacao:,}".replace(",", ".")
                    )

                # Processar dados para dataframe
                df_resumos = pd.DataFrame(resumos)

                # Selecionar apenas as 2 colunas solicitadas
                colunas_simplificadas = {
                    'dsPlanoOrcamentario': 'Plano Orçamentário',
                    'vlEfetivoRepasse': 'Valor Efetivo Repasse',
                    'vlTotalImplantacao': 'Total Implantação'
                }

                df_exibicao = df_resumos[list(colunas_simplificadas.keys())].copy()
                df_exibicao = df_exibicao.rename(columns=colunas_simplificadas)

                # Exibir dataframe com formatação
                st.dataframe(
                    df_exibicao,
                    column_config={
                        "Valor Efetivo Repasse": st.column_config.NumberColumn(
                            "Valor Efetivo Repasse",
                            format="R$ %.2f"
                        ),
                        "Total Implantação": st.column_config.NumberColumn(
                            "Total Implantação",
                            format="R$ %.2f"
                        )
                    },
                    use_container_width=True
                )

                # Calcular e exibir valor total recebido
                total_recebido = sum(resumo.get('vlEfetivoRepasse', 0) for resumo in resumos)
                st.subheader(f"💰 Valor Total Recebido: {format_currency(total_recebido)}")
                break


# Informações no rodapé
st.markdown("---")
st.markdown("**Sistema papprefeito** - Consulta simplificada de dados de financiamento APS")
st.markdown("*Dados obtidos do Ministério da Saúde via API oficial*")