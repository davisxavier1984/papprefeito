# Sistema de Monitoramento de Financiamento da Saúde - papprefeito
import streamlit as st
import pandas as pd
import json
import os
import sys
import plotly.graph_objects as go
from pyUFbr.baseuf import ufbr

# Adicionar diretório pai ao path para importar utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from utils import consultar_api, format_currency, get_latest_competencia
except ImportError:
    try:
        # Fallback se não conseguir importar do utils
        from api_client import consultar_api, get_latest_competencia
        from formatting import format_currency
    except ImportError:
        # Fallback com path absoluto
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from api_client import consultar_api, get_latest_competencia
        from formatting import format_currency

# Importar gerador de PDF com tratamento de erro
try:
    from pdf_generator import PDFReportGenerator
    PDF_AVAILABLE = True
except ImportError as e:
    PDF_AVAILABLE = False
    PDF_ERROR = f"Erro ao importar gerador PDF: {e}. Instale as dependências: pip install reportlab Pillow"

# Configurações Plotly otimizadas inline
PLOTLY_CONFIG = {
    'displayModeBar': True,
    'displaylogo': False,
    'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d'],
    'scrollZoom': True,
    'responsive': True,
    'locale': 'pt-BR'
}

CORES_PADRAO = {
    'positivo': '#1E8449',
    'negativo': '#C0392B',
    'neutro': '#FFC300',
    'destaque': '#3498DB',
    'secundario': '#95A5A6',
    'sucesso': '#27AE60',
    'alerta': '#F39C12',
    'erro': '#E74C3C',
    'info': '#5DADE2'
}

# Carregar dados de configuração
def carregar_config():
    """Carrega os dados do arquivo config.json"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        st.error("Arquivo config.json não encontrado")
        return None
    except json.JSONDecodeError:
        st.error("Erro ao decodificar arquivo config.json")
        return None

def exibir_tabela_quality_values(quality_values):
    """Exibe uma tabela com os valores de qualidade das equipes"""
    st.subheader("📊 Valores de Qualidade por Tipo de Equipe")
    
    if not quality_values:
        st.warning("Dados de qualidade não disponíveis")
        return
    
    # Criar dados para a tabela
    dados_tabela = []
    for equipe, valores in quality_values.items():
        linha = {
            "Tipo de Equipe": equipe,
            "Ótimo": format_currency(valores.get("Ótimo", 0)),
            "Bom": format_currency(valores.get("Bom", 0)),
            "Suficiente": format_currency(valores.get("Suficiente", 0)),
            "Regular": format_currency(valores.get("Regular", 0))
        }
        dados_tabela.append(linha)
    
    # Criar DataFrame
    df_quality = pd.DataFrame(dados_tabela)
    
    # Exibir tabela
    st.dataframe(df_quality, use_container_width=True)
    
    # Informação adicional
    st.info(f"📋 Total de tipos de equipes com valores de qualidade: {len(dados_tabela)}")

def calcular_valores_municipio(quality_values, classificacao_municipio, municipio_nome, uf_nome):
    """Calcula e exibe valores específicos para o município baseado na classificação de qualidade"""
    st.subheader(f"💰 Valores de Qualidade para {municipio_nome} - {uf_nome}")
    
    if not quality_values or not classificacao_municipio:
        st.warning("Dados insuficientes para calcular valores específicos do município")
        return
    
    # Normalizar classificação (caso venha da API com variações)
    classificacao_normalizada = classificacao_municipio.strip().title()
    
    # Verificar se a classificação existe
    classificacoes_validas = ["Ótimo", "Bom", "Suficiente", "Regular"]
    if classificacao_normalizada not in classificacoes_validas:
        st.warning(f"Classificação '{classificacao_municipio}' não reconhecida. Usando 'Bom' como padrão.")
        classificacao_normalizada = "Bom"
    
    # Exibir classificação atual
    st.info(f"🎯 **Classificação atual**: {classificacao_normalizada}")
    
    # Criar tabela com valores específicos para a classificação
    dados_municipio = []
    valor_total = 0
    
    for equipe, valores in quality_values.items():
        if classificacao_normalizada in valores:
            valor_especifico = valores[classificacao_normalizada]
            valor_total += valor_especifico
            
            linha = {
            "Tipo de Equipe": equipe,
            f"Valor ({classificacao_normalizada})": format_currency(valor_especifico)
            }
            dados_municipio.append(linha)
    
    if dados_municipio:
        # Exibir tabela principal
        df_municipio = pd.DataFrame(dados_municipio)
        st.dataframe(df_municipio, use_container_width=True)
        
        # Exibir métricas importantes
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("💵 Valor Total", format_currency(valor_total))
        with col2:
            st.metric("📊 Tipos de Equipes", len(dados_municipio))
        with col3:
            st.metric("⭐ Classificação", classificacao_normalizada)
        
        # Comparação com outras classificações
        if st.expander("📈 Comparação com Outras Classificações"):
            comparacao_dados = []
            for classificacao in classificacoes_validas:
                total_classificacao = 0
                for valores in quality_values.values():
                    if classificacao in valores:
                        total_classificacao += valores[classificacao]
                
                comparacao_dados.append({
                    "Classificação": classificacao,
                    "Valor Total": format_currency(total_classificacao),
                    "Diferença para Atual": format_currency(total_classificacao - valor_total) if classificacao != classificacao_normalizada else "Atual"
                })
            
            df_comparacao = pd.DataFrame(comparacao_dados)
            st.dataframe(df_comparacao, use_container_width=True)
    else:
        st.warning("Nenhum valor encontrado para a classificação atual")

def exibir_valores_reais_municipio(dados):
    """Exibe uma tabela com os valores reais de qualidade das equipes do município"""
    st.subheader("💰 Valores Reais de Qualidade por Equipe")
    
    if not dados or 'pagamentos' not in dados:
        st.warning("Dados de pagamentos não disponíveis")
        return
    
    pagamentos = dados['pagamentos'][0]  # Primeiro registro de pagamentos
    
    # Extrair dados das equipes
    equipes_dados = []
    valor_total_geral = 0
    
    # eSF - Equipes de Saúde da Família
    qt_esf = pagamentos.get('qtEsfHomologado', 0)
    vl_qualidade_esf = pagamentos.get('vlQualidadeEsf', 0)
    if qt_esf > 0:
        vl_unit_esf = vl_qualidade_esf / qt_esf
        equipes_dados.append({
            "Tipo de Equipe": "eSF - Equipes de Saúde da Família",
            "Quantidade": qt_esf,
            "Valor Qualidade/Equipe": format_currency(vl_unit_esf),
            "Valor Total Qualidade": format_currency(vl_qualidade_esf)
        })
        valor_total_geral += vl_qualidade_esf
    
    # eMulti - Equipes Multiprofissionais
    qt_emulti = pagamentos.get('qtEmultiPagas', 0)
    vl_qualidade_emulti = pagamentos.get('vlPagamentoEmultiQualidade', 0)
    if qt_emulti > 0:
        vl_unit_emulti = vl_qualidade_emulti / qt_emulti
        equipes_dados.append({
            "Tipo de Equipe": "eMulti - Equipes Multiprofissionais",
            "Quantidade": qt_emulti,
            "Valor Qualidade/Equipe": format_currency(vl_unit_emulti),
            "Valor Total Qualidade": format_currency(vl_qualidade_emulti)
        })
        valor_total_geral += vl_qualidade_emulti
    
    # eSB - Saúde Bucal
    qt_esb = pagamentos.get('qtSbPagamentoModalidadeI', 0)
    vl_qualidade_esb = pagamentos.get('vlPagamentoEsb40hQualidade', 0)
    if qt_esb > 0:
        vl_unit_esb = vl_qualidade_esb / qt_esb
        equipes_dados.append({
            "Tipo de Equipe": "eSB - Saúde Bucal",
            "Quantidade": qt_esb,
            "Valor Qualidade/Equipe": format_currency(vl_unit_esb),
            "Valor Total Qualidade": format_currency(vl_qualidade_esb)
        })
        valor_total_geral += vl_qualidade_esb
    
    # ACS - Agentes Comunitários de Saúde (se tiver componente qualidade separado)
    qt_acs = pagamentos.get('qtAcsDiretoPgto', 0)
    vl_total_acs = pagamentos.get('vlTotalAcsDireto', 0)
    if qt_acs > 0 and vl_total_acs > 0:
        equipes_dados.append({
            "Tipo de Equipe": "ACS - Agentes Comunitários de Saúde",
            "Quantidade": qt_acs,
            "Valor Qualidade/Equipe": format_currency(vl_total_acs / qt_acs),
            "Valor Total Qualidade": format_currency(vl_total_acs)
        })
        # Note: ACS não tem componente qualidade separado, então não adiciona ao total geral de qualidade
    
    if equipes_dados:
        # Criar DataFrame
        df_equipes = pd.DataFrame(equipes_dados)
        
        # Exibir tabela
        st.dataframe(df_equipes, use_container_width=True)
        
        # Exibir métricas importantes
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("💵 Total Geral Qualidade", format_currency(valor_total_geral))
        with col2:
            st.metric("📊 Tipos de Equipes", len([eq for eq in equipes_dados if "ACS" not in eq["Tipo de Equipe"]]))
        with col3:
            # Encontrar maior valor individual por equipe (excluindo ACS)
            valores_individuais = []
            for eq in equipes_dados:
                if "ACS" not in eq["Tipo de Equipe"]:
                    # Extrair valor numérico da string formatada
                    valor_str = eq["Valor Qualidade/Equipe"].replace("R$", "").replace(".", "").replace(",", ".").strip()
                    try:
                        valores_individuais.append(float(valor_str))
                    except:
                        pass
            
            if valores_individuais:
                maior_valor = max(valores_individuais)
                st.metric("⭐ Maior Valor/Equipe", format_currency(maior_valor))
        
        # Informação adicional
        st.info(f"📋 Valores extraídos dos dados reais do município para a competência {pagamentos.get('nuParcela', 'N/A')}")
        
        # Detalhes adicionais em expander
        if st.expander("📈 Detalhes das Classificações"):
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Classificações do Município:**")
                st.write(f"• IED: {pagamentos.get('dsFaixaIndiceEquidadeEsfEap', 'N/A')}")
                st.write(f"• Qualidade eSF/eAP: {pagamentos.get('dsClassificacaoQualidadeEsfEap', 'N/A')}")
                st.write(f"• Vínculo eSF/eAP: {pagamentos.get('dsClassificacaoVinculoEsfEap', 'N/A')}")
                st.write(f"• Qualidade eMulti: {pagamentos.get('dsClassificacaoQualidadeEmulti', 'N/A')}")
            
            with col2:
                st.write("**Informações Complementares:**")
                st.write(f"• População IBGE: {pagamentos.get('qtPopulacao', 'N/A'):,}")
                st.write(f"• Ano Ref. População: {pagamentos.get('nuAnoRefPopulacaoIbge', 'N/A')}")
                st.write(f"• Teto eSF: {pagamentos.get('qtTetoEsf', 'N/A')}")
                st.write(f"• Teto eMulti: {pagamentos.get('qtTetoEmultiAmpliada', 'N/A')}")
    else:
        st.warning("Nenhum dado de equipe encontrado para cálculo dos valores")

def criar_grafico_piramide_mensal(dados):
    """Cria o gráfico de pirâmide deitado com projeções mensais de ganho e perda (OTIMIZADO)"""
    if not dados or 'pagamentos' not in dados:
        return None
    
    pagamentos = dados['pagamentos'][0]
    
    # Extrair valor atual
    valor_atual = 0
    valor_atual += pagamentos.get('vlQualidadeEsf', 0)
    valor_atual += pagamentos.get('vlPagamentoEmultiQualidade', 0) 
    valor_atual += pagamentos.get('vlPagamentoEsb40hQualidade', 0)
    
    if valor_atual == 0:
        return None
    
    # Calcular cenários usando valores reais da tabela de classificação
    from utils import criar_tabela_total_por_classificacao
    import pandas as pd
    
    # Obter valores reais de cada classificação
    tabela_classificacao = criar_tabela_total_por_classificacao(dados)
    
    # Extrair valores monetários (remover formatação)
    valor_otimo_str = tabela_classificacao[tabela_classificacao['Classificação'] == 'Ótimo']['Valor Total'].iloc[0]
    valor_bom_str = tabela_classificacao[tabela_classificacao['Classificação'] == 'Bom']['Valor Total'].iloc[0]
    valor_regular_str = tabela_classificacao[tabela_classificacao['Classificação'] == 'Regular']['Valor Total'].iloc[0]
    
    # Converter strings formatadas para float
    from utils import currency_to_float
    valor_otimo = currency_to_float(valor_otimo_str)
    valor_bom = currency_to_float(valor_bom_str)  # valor atual = classificação "Bom"
    valor_regular = currency_to_float(valor_regular_str)
    
    # Recalcular valor_atual para ser coerente com "Bom"
    valor_atual = valor_bom
    
    # Calcular ganhos e perdas totais baseados nas diferenças reais
    ganho_total = valor_otimo - valor_bom
    perda_total = valor_bom - valor_regular
    
    # Preparar dados mensais
    from datetime import datetime
    meses_nomes = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
               'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    
    mes_atual = datetime.now().month - 1
    meses = []
    for i in range(12):
        mes_index = (mes_atual + i) % 12
        meses.append(meses_nomes[mes_index])
    
    # Acumulação mensal: cada mês acumula a diferença total
    ganhos_acumulados = [ganho_total * (i+1) for i in range(12)]
    perdas_acumuladas = [-perda_total * (i+1) for i in range(12)]
    
    # Criar figura otimizada
    fig = go.Figure()
    
    # Linha base
    fig.add_hline(
        y=0, 
        line_dash="dash", 
        line_color=CORES_PADRAO['neutro'], 
        line_width=3,
        annotation_text="Valor Atual",
        annotation_position="top right"
    )
    
    # Barras de ganho
    fig.add_trace(go.Bar(
        name='Ganhos Acumulados',
        x=meses,
        y=ganhos_acumulados,
        marker_color=CORES_PADRAO['positivo'],
        marker=dict(
            cornerradius=6,
            line=dict(width=0.8, color='rgba(0,0,0,0.2)')
        ),
        hovertemplate='<b>%{x}</b><br>Ganho: %{customdata}<br><extra></extra>',
        customdata=[format_currency(g) for g in ganhos_acumulados],
        text=[f'+{format_currency(g)}' for g in ganhos_acumulados],
        textposition='outside',
        textfont=dict(size=10, color=CORES_PADRAO['positivo'])
    ))
    
    # Barras de perda
    fig.add_trace(go.Bar(
        name='Perdas Acumuladas',
        x=meses,
        y=perdas_acumuladas,
        marker_color=CORES_PADRAO['negativo'],
        marker=dict(
            cornerradius=6,
            line=dict(width=0.8, color='rgba(0,0,0,0.2)')
        ),
        hovertemplate='<b>%{x}</b><br>Perda: %{customdata}<br><extra></extra>',
        customdata=[format_currency(abs(p)) for p in perdas_acumuladas],
        text=[f'-{format_currency(abs(p))}' for p in perdas_acumuladas],
        textposition='outside',
        textfont=dict(size=10, color=CORES_PADRAO['negativo'])
    ))
    
    # Valores totais são os valores do último mês (dezembro)
    total_ganhos = ganhos_acumulados[-1]  # Último valor da lista de ganhos
    total_perdas = abs(perdas_acumuladas[-1])  # Último valor absoluto da lista de perdas
    
    # Calcular posições dinâmicas para os painéis
    max_ganho = max(ganhos_acumulados)
    min_perda = min(perdas_acumuladas)
    
    # Adicionar painel superior (Ganhos)
    fig.add_annotation(
        text=f"<b>Total de Ganhos</b><br>{format_currency(total_ganhos)}",
        x=5.5,  # Centro horizontal do gráfico
        y=max_ganho * 0.8,  # 80% da altura máxima dos ganhos
        showarrow=False,
        bgcolor=CORES_PADRAO['positivo'],
        bordercolor="rgba(255,255,255,0.8)",
        borderwidth=2,
        font=dict(size=14, color="white", family="Arial"),
        align="center",
        width=200,
        height=60,
        opacity=0.9
    )
    
    # Adicionar painel inferior (Perdas)
    fig.add_annotation(
        text=f"<b>Total de Perdas</b><br>{format_currency(total_perdas)}",
        x=5.5,  # Centro horizontal do gráfico
        y=min_perda * 0.8,  # 80% da altura mínima das perdas
        showarrow=False,
        bgcolor=CORES_PADRAO['negativo'],
        bordercolor="rgba(255,255,255,0.8)",
        borderwidth=2,
        font=dict(size=14, color="white", family="Arial"),
        align="center",
        width=200,
        height=60,
        opacity=0.9
    )
    
    # Layout otimizado
    municipio_nome = st.session_state.get('municipio_selecionado', '')
    uf_nome = st.session_state.get('uf_selecionada', '')
    
    fig.update_layout(
        title=f"Projeção Anual de Ganhos e Perdas - {municipio_nome}, {uf_nome}",
        barmode='relative',
        height=650,
        template='plotly_white',
        margin=dict(r=60, l=60, t=80, b=60),
        xaxis=dict(
            title=dict(text="Meses do Ano", font=dict(size=14, color='#2C3E50')),
            tickfont=dict(size=12, color='#2C3E50')
        ),
        yaxis=dict(
            title=dict(text="Valor Acumulado (R$)", font=dict(size=14, color='#2C3E50')),
            tickfont=dict(size=12, color='#2C3E50'),
            tickformat=',.0f',
            tickprefix='R$ '
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(size=12, color='#2C3E50')
        ),
        font=dict(family='Arial, sans-serif'),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def criar_grafico_barras_horizontais(dados):
    """Cria gráfico de barras horizontais para valores por equipe"""
    if not dados or 'pagamentos' not in dados:
        return None
        
    pagamentos = dados['pagamentos'][0]
    
    # Extrair dados das equipes
    equipes_dados = []
    
    # eSF
    vl_qualidade_esf = pagamentos.get('vlQualidadeEsf', 0)
    if vl_qualidade_esf > 0:
        equipes_dados.append({
            'tipo': 'eSF - Saúde da Família',
            'valor': vl_qualidade_esf,
            'quantidade': pagamentos.get('qtEsfHomologado', 0)
        })
    
    # eMulti
    vl_qualidade_emulti = pagamentos.get('vlPagamentoEmultiQualidade', 0)
    if vl_qualidade_emulti > 0:
        equipes_dados.append({
            'tipo': 'eMulti - Multiprofissionais',
            'valor': vl_qualidade_emulti,
            'quantidade': pagamentos.get('qtEmultiPagas', 0)
        })
    
    # eSB
    vl_qualidade_esb = pagamentos.get('vlPagamentoEsb40hQualidade', 0)
    if vl_qualidade_esb > 0:
        equipes_dados.append({
            'tipo': 'eSB - Saúde Bucal',
            'valor': vl_qualidade_esb,
            'quantidade': pagamentos.get('qtSbPagamentoModalidadeI', 0)
        })
    
    if not equipes_dados:
        return None
    
    # Criar figura horizontal
    fig = go.Figure()
    
    tipos = [eq['tipo'] for eq in equipes_dados]
    valores = [eq['valor'] for eq in equipes_dados]
    quantidades = [eq['quantidade'] for eq in equipes_dados]
    cores = [CORES_PADRAO['positivo'], CORES_PADRAO['destaque'], CORES_PADRAO['info']]
    
    fig.add_trace(go.Bar(
        x=valores,
        y=tipos,
        orientation='h',
        marker=dict(
            color=cores[:len(valores)],
            cornerradius=8,
            line=dict(width=1, color='rgba(0,0,0,0.2)')
        ),
        text=[format_currency(v) for v in valores],
        textposition='outside',
        textfont=dict(size=12, color='#2C3E50'),
        hovertemplate='<b>%{y}</b><br>Valor: %{text}<br>Equipes: %{customdata}<extra></extra>',
        customdata=quantidades
    ))
    
    municipio_nome = st.session_state.get('municipio_selecionado', '')
    uf_nome = st.session_state.get('uf_selecionada', '')
    
    fig.update_layout(
        title=f"Valores de Qualidade por Tipo de Equipe - {municipio_nome}, {uf_nome}",
        xaxis_title="Valor Total (R$)",
        yaxis_title="",
        height=400,
        template='plotly_white',
        margin=dict(r=60, l=200, t=80, b=60),
        showlegend=False,
        font=dict(family='Arial, sans-serif'),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            tickformat=',.0f',
            tickprefix='R$ '
        )
    )
    
    return fig

def criar_grafico_rosquinha(dados):
    """Cria gráfico de rosquinha para mostrar distribuição de valores"""
    if not dados or 'pagamentos' not in dados:
        return None
        
    pagamentos = dados['pagamentos'][0]
    
    # Extrair valores por tipo
    valores = []
    labels = []
    cores = []
    
    vl_esf = pagamentos.get('vlQualidadeEsf', 0)
    if vl_esf > 0:
        valores.append(vl_esf)
        labels.append('eSF')
        cores.append(CORES_PADRAO['positivo'])
    
    vl_emulti = pagamentos.get('vlPagamentoEmultiQualidade', 0)
    if vl_emulti > 0:
        valores.append(vl_emulti)
        labels.append('eMulti')
        cores.append(CORES_PADRAO['destaque'])
    
    vl_esb = pagamentos.get('vlPagamentoEsb40hQualidade', 0)
    if vl_esb > 0:
        valores.append(vl_esb)
        labels.append('eSB')
        cores.append(CORES_PADRAO['info'])
    
    if not valores:
        return None
    
    municipio_nome = st.session_state.get('municipio_selecionado', '')
    uf_nome = st.session_state.get('uf_selecionada', '')
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=valores,
        hole=0.4,
        marker=dict(colors=cores, line=dict(color='#FFFFFF', width=2)),
        textinfo='label+percent+value',
        textfont=dict(size=12),
        hovertemplate='<b>%{label}</b><br>Valor: %{text}<br>Percentual: %{percent}<extra></extra>',
        text=[format_currency(v) for v in valores]
    )])
    
    fig.update_layout(
        title=f"Distribuição de Valores por Tipo de Equipe - {municipio_nome}, {uf_nome}",
        height=500,
        template='plotly_white',
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        font=dict(family='Arial, sans-serif'),
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(r=60, l=60, t=80, b=100)
    )
    
    return fig

def criar_grafico_decisao_estrategica(dados):
    """Cria o gráfico de decisão estratégica para impressão baseado nos dados reais do município (OTIMIZADO)"""
    if not dados or 'pagamentos' not in dados:
        return None
    
    pagamentos = dados['pagamentos'][0]
    
    # Extrair valor atual real do município
    valor_atual = 0
    valor_atual += pagamentos.get('vlQualidadeEsf', 0)
    valor_atual += pagamentos.get('vlPagamentoEmultiQualidade', 0) 
    valor_atual += pagamentos.get('vlPagamentoEsb40hQualidade', 0)
    
    if valor_atual == 0:
        return None
    
    # Extrair classificação atual
    classificacao_atual = pagamentos.get('dsClassificacaoQualidadeEsfEap', 'Bom')
    if not classificacao_atual:
        classificacao_atual = 'Bom'
    
    # Calcular cenários otimizados
    percentual_variacao = 0.25
    valor_otimo = valor_atual * (1 + percentual_variacao)
    valor_regular = valor_atual * (1 - percentual_variacao)
    
    mapeamento_y = {'Regular': 1, 'Atual': 2, 'Ótimo': 3}
    
    # Criar figura otimizada
    fig = criar_figura_otimizada(altura=600)
    
    # Linhas de cenário
    fig.add_trace(go.Scatter(
        x=['Situação Atual', 'Projeção 2026'],
        y=[mapeamento_y['Atual'], mapeamento_y['Ótimo']],
        mode='lines',
        line=dict(color=CORES_PADRAO['positivo'], width=5),
        showlegend=False
    ))
    
    fig.add_trace(go.Scatter(
        x=['Situação Atual', 'Projeção 2026'],
        y=[mapeamento_y['Atual'], mapeamento_y['Regular']],
        mode='lines',
        line=dict(color=CORES_PADRAO['negativo'], width=5),
        showlegend=False
    ))
    
    # Pontos de situação
    fig.add_trace(go.Scatter(
        x=['Situação Atual'],
        y=[mapeamento_y['Atual']],
        mode='markers',
        marker=dict(size=30, color=CORES_PADRAO['neutro'], 
               line=dict(color='black', width=3)),
        showlegend=False
    ))
    
    fig.add_trace(go.Scatter(
        x=['Projeção 2026', 'Projeção 2026'],
        y=[mapeamento_y['Ótimo'], mapeamento_y['Regular']],
        mode='markers',
        marker=dict(size=25, 
               color=[CORES_PADRAO['positivo'], CORES_PADRAO['negativo']],
               line=dict(color='black', width=2)),
        showlegend=False
    ))
    
    # Anotações melhoradas
    ganho = valor_otimo - valor_atual
    perda = valor_atual - valor_regular
    
    fig.add_annotation(
        x='Situação Atual', y=mapeamento_y['Atual'] + 0.15,
        text=f"<b>{classificacao_atual}</b><br>{format_currency(valor_atual)}",
        showarrow=False,
        font=dict(size=16, color='black'),
        bgcolor='rgba(255,255,255,0.9)', bordercolor='black', borderwidth=2
    )
    
    fig.add_annotation(
        x='Projeção 2026', y=mapeamento_y['Ótimo'],
        text=f"<b>Cenário Ótimo</b><br>{format_currency(valor_otimo)}<br><span style='color:white'>+{format_currency(ganho)} (+25%)</span>",
        showarrow=False,
        font=dict(size=14, color='white'),
        bgcolor=CORES_PADRAO['positivo'], borderwidth=1, xshift=120
    )
    
    fig.add_annotation(
        x='Projeção 2026', y=mapeamento_y['Regular'],
        text=f"<b>Cenário Regular</b><br>{format_currency(valor_regular)}<br><span style='color:white'>-{format_currency(perda)} (-25%)</span>",
        showarrow=False,
        font=dict(size=14, color='white'),
        bgcolor=CORES_PADRAO['negativo'], borderwidth=1, xshift=120
    )
    
    # Layout otimizado
    fig.update_layout(
        title="Encruzilhada Financeira: O Futuro do Município em 2026",
        showlegend=False,
        margin=dict(r=280, l=50, t=80, b=50),
        xaxis=dict(
            tickmode='array',
            tickvals=['Situação Atual', 'Projeção 2026'],
            ticktext=['<b>Situação Atual</b>', '<b>Projeção 2026</b>'],
            showline=False
        ),
        yaxis=dict(
            tickmode='array',
            tickvals=[1, 2, 3],
            ticktext=['<b>Regular (-25%)</b>', f'<b>{classificacao_atual} (Atual)</b>', '<b>Ótimo (+25%)</b>'],
            range=[0.5, 3.5], showline=False
        )
    )
    
    # Aplicar tema do município
    municipio_nome = st.session_state.get('municipio_selecionado', '')
    uf_nome = st.session_state.get('uf_selecionada', '')
    aplicar_tema_municipio(fig, municipio_nome, uf_nome)
    
    return fig

def exibir_tabelas(titulo, dados, colunas):
    """Exibe uma tabela formatada com os dados."""
    st.subheader(titulo)
    
    if dados:
        # Filtrar apenas as colunas que existem nos dados
        colunas_existentes = []
        for coluna in colunas:
            if any(coluna in item for item in dados):
                colunas_existentes.append(coluna)
        
        # Criar DataFrame
        df_dados = []
        for item in dados:
            linha = {}
            for coluna in colunas_existentes:
                valor = item.get(coluna, "")
                # Formatar valores monetários
                if coluna.startswith('vl') and isinstance(valor, (int, float)) and valor != 0:
                    linha[coluna] = format_currency(valor)
                else:
                    linha[coluna] = valor
            df_dados.append(linha)
        
        df = pd.DataFrame(df_dados)
        
        # Mapear nomes das colunas para português
        mapeamento_colunas = {
            "sgUf": "UF",
            "coMunicipioIbge": "Código IBGE",
            "noMunicipio": "Município",
            "nuCompCnes": "Competência CNES",
            "nuParcela": "Parcela",
            "dsPlanoOrcamentario": "Plano Orçamentário",
            "dsEsferaAdministrativa": "Esfera Administrativa",
            "vlIntegral": "Valor Integral",
            "vlAjuste": "Valor Ajuste",
            "vlDesconto": "Valor Desconto",
            "vlEfetivoRepasse": "Valor Efetivo Repasse",
            "vlImplantacao": "Valor Implantação",
            "vlAjusteImplantacao": "Ajuste Implantação",
            "vlDescontoImplantacao": "Desconto Implantação",
            "vlTotalImplantacao": "Total Implantação"
        }
        
        # Renomear colunas
        df = df.rename(columns=mapeamento_colunas)
        
        # Exibir DataFrame
        st.dataframe(df, use_container_width=True)
        
        # Mostrar resumo
        st.info(f"📊 Total de registros: {len(df)}")
    else:
        st.warning("Nenhum dado encontrado.")

def main():
    st.set_page_config(page_title="Sistema de Monitoramento - Saúde")
    st.title("📊 Sistema de Monitoramento de Financiamento da Saúde")
    st.header("🔍 Consulta de Dados Municipais")
    
    # Carregar configurações
    config_data = carregar_config()

    with st.expander("🔍 Parâmetros de Consulta", expanded=True):
        estados = ufbr.list_uf
        uf_selecionada = st.selectbox("Selecione um Estado", options=estados)
        
        # Competência automática (não exibida)
        competencia = get_latest_competencia()

        if uf_selecionada:
            municipios = ufbr.list_cidades(uf_selecionada)
            municipio_selecionado = st.selectbox("Selecione um Município", options=municipios)

            try:
                codigo_ibge = ufbr.get_cidade(municipio_selecionado).codigo
                codigo_ibge = str(int(float(codigo_ibge)))[:-1]
            except AttributeError:
                st.error("Erro ao obter código IBGE do município")
                return

    if st.button("Consultar"):
        if not (uf_selecionada and municipio_selecionado):
            st.error("Por favor, selecione um estado e município.")
            return

        with st.spinner("Consultando dados da API..."):
            dados = consultar_api(codigo_ibge, competencia)

        if dados:
            # Salvar dados na sessão
            st.session_state['dados'] = dados
            st.session_state['municipio_selecionado'] = municipio_selecionado
            st.session_state['uf_selecionada'] = uf_selecionada
            st.session_state['competencia'] = competencia
            
            # Extrair e salvar população dos dados
            try:
                if "pagamentos" in dados and dados["pagamentos"]:
                    populacao = dados['pagamentos'][0].get('qtPopulacao', 0)
                    if populacao > 0:
                        st.session_state['populacao'] = populacao
            except (KeyError, IndexError, TypeError):
                pass
            
            st.success(f"✅ Dados carregados com sucesso para {municipio_selecionado} - {uf_selecionada}!")

            # Exibir dados
            resumos = dados.get('resumosPlanosOrcamentarios', [])
            pagamentos = dados.get('pagamentos', [])

            # Colunas para resumos orçamentários
            colunas_resumos = [
                "sgUf", "coMunicipioIbge", "noMunicipio", "nuCompCnes", "nuParcela",
            "dsPlanoOrcamentario", "dsEsferaAdministrativa", "vlIntegral", "vlAjuste",
            "vlDesconto", "vlEfetivoRepasse", "vlImplantacao", "vlAjusteImplantacao",
            "vlDescontoImplantacao", "vlTotalImplantacao"
            ]

            # Colunas para pagamentos
            colunas_pagamentos = [
            "sgUf", "noMunicipio", "coMunicipioIbge", "nuCompCnes", "nuParcela",
            "dsFaixaIndiceEquidadeEsfEap", "dsClassificacaoVinculoEsfEap", 
            "dsClassificacaoQualidadeEsfEap", "qtEsfCredenciado", "qtEsfHomologado"
            ]

            st.subheader("📊 Valor Total por Classificação - Cenários Completos")
            try:
                from utils import criar_tabela_total_por_classificacao
                
                tabela_classificacao = criar_tabela_total_por_classificacao(dados)
                st.dataframe(tabela_classificacao, use_container_width=True)
                
                        
            except ImportError as e:
                st.error(f"Erro ao importar função de classificação: {e}")
            except Exception as e:
                st.error(f"Erro ao gerar tabela por classificação: {e}")
            
            # Dashboard de Gráficos Otimizados
            st.markdown("---")
            st.header(f"📊 Dashboard Visual - {municipio_selecionado}, {uf_selecionada}")
            
            # Criar tabs para organizar os gráficos
            tab1, tab2, tab3 = st.tabs(["📈 Projeção Anual", "📊 Por Equipe", "🍩 Distribuição"])
            
            with tab1:
                st.write("**Projeção mensal acumulada de ganhos e perdas baseada na classificação atual**")
                fig_piramide = criar_grafico_piramide_mensal(dados)
                if fig_piramide:
                    st.plotly_chart(fig_piramide, use_container_width=True, theme="streamlit", config=PLOTLY_CONFIG)
                else:
                    st.warning("⚠️ Não foi possível gerar o gráfico. Dados de qualidade insuficientes.")
            
            with tab2:
                st.write("**Valores de qualidade por tipo de equipe**")
                fig_horizontal = criar_grafico_barras_horizontais(dados)
                if fig_horizontal:
                    st.plotly_chart(fig_horizontal, use_container_width=True, theme="streamlit", config=PLOTLY_CONFIG)
                else:
                    st.info("🚧 Gráfico de barras horizontais em desenvolvimento")
            
            with tab3:
                st.write("**Distribuição de valores entre tipos de equipe**")
                fig_rosquinha = criar_grafico_rosquinha(dados)
                if fig_rosquinha:
                    st.plotly_chart(fig_rosquinha, use_container_width=True, theme="streamlit", config=PLOTLY_CONFIG)
                else:
                    st.info("🚧 Gráfico de distribuição em desenvolvimento")
            
            # Extrair valores para métricas destacadas (fora das tabs)
            pagamentos = dados['pagamentos'][0]
            valor_atual = pagamentos.get('vlQualidadeEsf', 0) + pagamentos.get('vlPagamentoEmultiQualidade', 0) + pagamentos.get('vlPagamentoEsb40hQualidade', 0)
            valor_otimo = valor_atual * 1.25
            valor_regular = valor_atual * 0.75
            ganho_mensal = valor_otimo - valor_atual
            perda_mensal = valor_atual - valor_regular
            ganho_anual = ganho_mensal * 12
            perda_anual = perda_mensal * 12
            
            
            
            
        else:
            st.error("❌ Nenhum dado encontrado para os parâmetros informados.")
            st.info("💡 Verifique se o código IBGE está correto.")

    # Seção de geração de relatório PDF - FORA do bloco condicional para evitar loop
    if 'dados' in st.session_state and 'municipio_selecionado' in st.session_state:
        st.markdown("---")
        st.header("📄 Relatório PDF Profissional")
        
        if not PDF_AVAILABLE:
            st.error(f"❌ {PDF_ERROR}")
            st.info("💡 Execute: pip install reportlab Pillow")
        else:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🎯 Gerar Relatório PDF", type="primary", use_container_width=True):
                    try:
                        with st.spinner("Gerando relatório PDF..."):
                            # Usar dados do session_state
                            dados_sessao = st.session_state['dados']
                            municipio_sessao = st.session_state['municipio_selecionado']
                            uf_sessao = st.session_state.get('uf_selecionada', 'BR')
                            
                            # Criar gerador e gerar PDF
                            gerador = PDFReportGenerator()
                            pdf_bytes = gerador.gerar_relatorio_pdf(municipio_sessao, uf_sessao, dados_sessao)
                            nome_arquivo = gerador.criar_nome_arquivo(municipio_sessao)
                            
                            # Disponibilizar download
                            st.download_button(
                                label="⬇️ Baixar Relatório PDF",
                                data=pdf_bytes,
                                file_name=nome_arquivo,
                                mime="application/pdf",
                                type="primary",
                                use_container_width=True
                            )
                            
                            st.success(f"✅ Relatório gerado com sucesso!")
                            st.info(f"📊 Arquivo: {nome_arquivo}")
                            
                    except Exception as e:
                        st.error(f"❌ Erro ao gerar relatório: {str(e)}")
                        st.info("💡 Verifique se todas as dependências estão instaladas: pip install reportlab Pillow")
            
            st.markdown("""
            **📋 O relatório PDF inclui:**
            - ✅ Análise do cenário financeiro atual
            - ✅ Tabela completa de cenários (Ótimo, Bom, Suficiente, Regular)
            - ✅ Projeções anuais de ganhos e perdas
            - ✅ Layout profissional com logo da Mais Gestor
            - ✅ Formato ideal para apresentações e tomada de decisões
            """)

if __name__ == "__main__":
    main()