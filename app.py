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
            # Consultar API (ela já salva naturalmente no JSON)
            dados_api = consultar_api(cod_municipio, competencia)

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

    # Trabalhar com dados do município atual
    if 'resumosPlanosOrcamentarios' in dados_api:
        resumos = dados_api['resumosPlanosOrcamentarios']

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
        pagamentos = dados_api.get('pagamentos', [])
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

        # Selecionar colunas e renomear conforme solicitado
        colunas_simplificadas = {
            'dsPlanoOrcamentario': 'Recurso',
            'vlEfetivoRepasse': 'Recurso Real'
        }

        df_exibicao = df_resumos[list(colunas_simplificadas.keys())].copy()
        df_exibicao = df_exibicao.rename(columns=colunas_simplificadas)

        # Carregar dados editados existentes
        edited_data = load_edited_data()
        municipio_key = f"{municipio_info['codigo']}_{municipio_info['competencia']}"

        # Função para calcular colunas derivadas
        def calcular_colunas_derivadas(df):
            df = df.copy()
            df['Recurso Potencial'] = df['Recurso Real'] + df['Perca Recurso Mensal']
            df['Recurso Real Anual'] = df['Recurso Real'] * 12
            df['Recurso Potencial Anual'] = df['Recurso Potencial'] * 12
            df['Diferença'] = df['Recurso Potencial Anual'] - df['Recurso Real Anual']
            return df

        # Inicializar session state para este município se não existir
        session_key = f"perca_{municipio_key}"
        if session_key not in st.session_state:
            if municipio_key in edited_data:
                st.session_state[session_key] = edited_data[municipio_key].get('perca_recurso_mensal', [0.0] * len(df_exibicao))
            else:
                st.session_state[session_key] = [0.0] * len(df_exibicao)

        # Adicionar coluna Perca Recurso Mensal do session state
        df_exibicao['Perca Recurso Mensal'] = st.session_state[session_key]

        # Calcular colunas derivadas iniciais
        df_exibicao = calcular_colunas_derivadas(df_exibicao)


        # Exibir dataframe editável (apenas a coluna editável)
        df_editado = st.data_editor(
            df_exibicao,
            column_config={
                "Recurso": st.column_config.TextColumn(
                    "Recurso",
                    disabled=True,
                    help="Tipo do recurso/programa"
                ),
                "Recurso Real": st.column_config.NumberColumn(
                    "Recurso Real",
                    format="R$ %.2f",
                    disabled=True,
                    help="Valor mensal recebido do governo"
                ),
                "Perca Recurso Mensal": st.column_config.NumberColumn(
                    "Perca Recurso Mensal",
                    format="R$ %.2f",
                    min_value=0.0,
                    help="💰 EDITÁVEL: Digite o valor perdido mensalmente"
                ),
                "Recurso Potencial": st.column_config.NumberColumn(
                    "Recurso Potencial",
                    format="R$ %.2f",
                    disabled=True,
                    help="Calculado: Recurso Real + Perca Mensal"
                ),
                "Recurso Real Anual": st.column_config.NumberColumn(
                    "Recurso Real Anual",
                    format="R$ %.2f",
                    disabled=True,
                    help="Calculado: Recurso Real × 12"
                ),
                "Recurso Potencial Anual": st.column_config.NumberColumn(
                    "Recurso Potencial Anual",
                    format="R$ %.2f",
                    disabled=True,
                    help="Calculado: Recurso Potencial × 12"
                ),
                "Diferença": st.column_config.NumberColumn(
                    "Diferença",
                    format="R$ %.2f",
                    disabled=True,
                    help="Calculado: Diferença entre Potencial e Real anuais"
                )
            },
            use_container_width=True,
            key=f"data_editor_{municipio_key}"
        )

        # SEMPRE recalcular as colunas derivadas após edição
        df_final = calcular_colunas_derivadas(df_editado)

        # Verificar se houve mudanças comparando com session state
        valores_atuais = df_editado['Perca Recurso Mensal'].tolist()
        dados_alterados = valores_atuais != st.session_state[session_key]

        if dados_alterados:
            # Atualizar session state
            st.session_state[session_key] = valores_atuais

            # Salvar dados editados
            edited_data[municipio_key] = {
                'perca_recurso_mensal': valores_atuais
            }
            save_edited_data(edited_data)

            # Rerun para atualizar instantaneamente
            st.rerun()

        # Exibir totais calculados usando o df_final com cálculos atualizados
        st.markdown("---")
        col1, col2, col3 = st.columns(3)

        with col1:
            total_perca = df_final['Perca Recurso Mensal'].sum()
            st.metric(
                "💸 Total Perca Mensal",
                format_currency(total_perca),
                help="Soma total das perdas mensais"
            )

        with col2:
            total_diferenca = df_final['Diferença'].sum()
            st.metric(
                "📊 Diferença Anual Total",
                format_currency(total_diferenca),
                help="Diferença total anual entre potencial e real"
            )

        with col3:
            if total_diferenca > 0:
                percentual = (total_diferenca / df_final['Recurso Real Anual'].sum()) * 100
                st.metric(
                    "📈 % Perda Anual",
                    f"{percentual:.1f}%",
                    help="Percentual de perda em relação ao recurso real anual"
                )

        # Calcular e exibir valor total recebido
        total_recebido = sum(resumo.get('vlEfetivoRepasse', 0) for resumo in resumos)
        st.subheader(f"💰 Valor Total Recebido: {format_currency(total_recebido)}")


# Informações no rodapé
st.markdown("---")
st.markdown("**Sistema papprefeito** - Consulta simplificada de dados de financiamento APS")
st.markdown("*Dados obtidos do Ministério da Saúde via API oficial*")