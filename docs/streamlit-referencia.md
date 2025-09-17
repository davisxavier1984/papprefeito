# Referência Streamlit - Sistema de Monitoramento de Financiamento da Saúde

Este documento serve como referência técnica para desenvolvimento e manutenção do sistema **papprefeito** usando Streamlit.

## 📋 Índice

- [1. Configuração Inicial](#1-configuração-inicial)
- [2. Layout e Estrutura](#2-layout-e-estrutura)
- [3. Widgets de Entrada](#3-widgets-de-entrada)
- [4. Gráficos Plotly](#4-gráficos-plotly)
- [5. Gerenciamento de Estado](#5-gerenciamento-de-estado)
- [6. Componentes de Exibição](#6-componentes-de-exibição)
- [7. Boas Práticas](#7-boas-práticas)
- [8. Troubleshooting](#8-troubleshooting)

---

## 1. Configuração Inicial

### 1.1 Page Config
```python
st.set_page_config(
    page_title="Mais Gestor - Landing Page",
    layout="wide"
)
```

**Parâmetros importantes:**
- `layout="wide"`: Usa toda largura da tela
- `page_title`: Título da aba do navegador
- `initial_sidebar_state`: "expanded" | "collapsed"

### 1.2 Configurações Plotly
```python
PLOTLY_CONFIG = {
    'displayModeBar': True,
    'displaylogo': False,
    'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d'],
    'scrollZoom': True,
    'responsive': True,
    'locale': 'pt-BR'
}
```

---

## 2. Layout e Estrutura

### 2.1 Sistema de Colunas
```python
# 4 colunas para seletores principais
col1, col2, col3, col4 = st.columns(4)

with col1:
    uf_selecionada = st.selectbox("Selecione um Estado", options=estados)

with col2:
    municipio_selecionado = st.selectbox("Selecione um Município", options=municipios)
```

**Dicas:**
- Use `st.columns(spec)` onde `spec` pode ser:
  - Inteiro: `st.columns(4)` (4 colunas iguais)
  - Lista: `st.columns([2, 1, 1])` (larguras proporcionais)
- Parâmetro `gap`: "small", "medium", "large"

### 2.2 Containers
```python
# Container para controlar ordem de renderização
begin = st.container()

# Lógica posterior
if st.button('Clear name'):
    st.session_state.name = ''

# Widget renderizado primeiro visualmente
begin.text_input('Name', key='name')
```

### 2.3 Sidebar
```python
# Adicionar widgets à sidebar
st.sidebar.selectbox("Opções", ["A", "B", "C"])

# Ou usando context manager
with st.sidebar:
    st.slider("Valor", 0, 100)
```

### 2.4 Métricas
```python
# Layout de métricas usado no projeto
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="💰 Recurso Atual",
        value=format_currency(valor_atual),
        help="Classificação Bom"
    )

with col2:
    st.metric(
        label="🚀 Recurso Potencial",
        value=format_currency(valor_otimo),
        help="Classificação Ótimo"
    )

with col3:
    st.metric(
        label="📈 Acréscimo",
        value=format_currency(valor_otimo - valor_atual),
        delta=f"+{((valor_otimo - valor_atual) / valor_atual * 100):.1f}%"
    )
```

---

## 3. Widgets de Entrada

### 3.1 Selectbox com Dependência
```python
# Padrão usado no projeto para UF -> Município
estados = ufbr.list_uf
uf_selecionada = st.selectbox("Selecione um Estado", options=estados)

municipio_selecionado = None
if uf_selecionada:
    municipios = ufbr.list_cidades(uf_selecionada)
    municipio_selecionado = st.selectbox("Selecione um Município", options=municipios)
```

### 3.2 Text Input com Estados
```python
# Placeholder que pode ser atualizado
estrato_placeholder = st.empty()
estrato_placeholder.text_input("Estrato", value="-", disabled=True, key="estrato_default")

# Atualização posterior
estrato_placeholder.text_input("Estrato", value=estrato_valor, disabled=True, key="estrato_updated")
```

### 3.3 Outros Widgets Úteis
```python
# Botões
if st.button('Processar Dados'):
    # Lógica de processamento
    pass

# Checkbox
mostrar_detalhes = st.checkbox('Mostrar detalhes avançados')

# Slider
fator_multiplicador = st.slider('Fator de ajuste', 0.5, 2.0, 1.0, 0.1)

# Number input
valor_customizado = st.number_input('Valor personalizado', min_value=0, max_value=1000000)
```

---

## 4. Gráficos Plotly

### 4.1 Gráfico de Barras Comparativo
```python
def criar_grafico_comparativo(valor_regular, valor_otimo):
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=['Regular', 'Ótimo'],
        y=[valor_regular, valor_otimo],
        marker_color=[CORES_PADRAO['negativo'], CORES_PADRAO['positivo']],
        text=[format_currency(valor_regular), format_currency(valor_otimo)],
        textposition='outside',
        textfont=dict(size=16, color='black', family='Arial Black'),
        name='Valores'
    ))

    # Adicionar anotação para diferença
    diferenca = valor_otimo - valor_regular
    fig.add_annotation(
        x=0.5,
        y=(valor_regular + valor_otimo) / 2,
        text=f"Diferença<br>{format_currency(diferenca)}",
        showarrow=True,
        arrowhead=2,
        arrowcolor=CORES_PADRAO['destaque'],
        bgcolor=CORES_PADRAO['destaque'],
        bordercolor="white",
        borderwidth=2,
        font=dict(size=14, color="white", family="Arial Bold")
    )

    fig.update_layout(
        title="Comparação: Classificação Regular vs Ótimo",
        title_font_size=24,
        showlegend=False,
        height=500,
        template='plotly_white',
        yaxis=dict(
            tickformat=',.0f',
            tickprefix='R$ ',
            title="Valor Total Anual"
        ),
        font=dict(family='Arial, sans-serif')
    )

    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
```

### 4.2 Paleta de Cores Padrão
```python
CORES_PADRAO = {
    'positivo': '#1E8449',    # Verde escuro
    'negativo': '#C0392B',    # Vermelho escuro
    'neutro': '#FFC300',      # Amarelo
    'destaque': '#3498DB',    # Azul
    'secundario': '#95A5A6',  # Cinza
    'sucesso': '#27AE60',     # Verde claro
    'alerta': '#F39C12',      # Laranja
    'erro': '#E74C3C',        # Vermelho claro
    'info': '#5DADE2'         # Azul claro
}
```

### 4.3 Configurações de Exibição
```python
# Usar tema do Streamlit (padrão)
st.plotly_chart(fig, theme="streamlit", use_container_width=True)

# Usar tema nativo do Plotly
st.plotly_chart(fig, theme=None, use_container_width=True)

# Com configurações customizadas
st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
```

### 4.4 Gráficos Interativos
```python
# Para capturar seleções do usuário
fig = px.scatter(df, x="x", y="y", color="categoria")
selected_points = st.plotly_chart(
    fig,
    key="grafico_interativo",
    on_select="rerun",
    selection_mode=['points', 'box']
)

# Acessar dados selecionados
if 'grafico_interativo' in st.session_state:
    selection = st.session_state.grafico_interativo
    st.write("Pontos selecionados:", selection)
```

---

## 5. Gerenciamento de Estado

### 5.1 Session State para Dados
```python
# Verificar existência antes de usar
if 'dados' not in st.session_state:
    st.session_state['dados'] = {}

# Salvar dados na sessão
st.session_state['dados'] = dados
st.session_state['municipio_selecionado'] = municipio_selecionado
st.session_state['uf_selecionada'] = uf_selecionada

# Recuperar dados
municipio = st.session_state.get('municipio_selecionado', '')
uf = st.session_state.get('uf_selecionada', '')
```

### 5.2 Widgets com Keys
```python
# Widget com key para persistir estado
valor = st.slider("Configuração", 0, 100, key="config_slider")

# Acessar valor via session state
if st.session_state.config_slider > 50:
    st.success("Valor alto!")
```

### 5.3 Callbacks com Session State
```python
def processar_dados():
    # Função chamada quando botão é clicado
    st.session_state.processado = True
    st.session_state.timestamp = datetime.now()

st.button("Processar", on_click=processar_dados)

if st.session_state.get('processado', False):
    st.success(f"Processado em {st.session_state.timestamp}")
```

---

## 6. Componentes de Exibição

### 6.1 Markdown Formatado com HTML
```python
# Seção destacada (usada no projeto)
st.markdown("""
<div style="background-color: #E74C3C; padding: 30px; border-radius: 15px; text-align: center; margin: 30px 0;">
    <h2 style="color: white; font-size: 36px; margin-bottom: 10px;">Quanto eu deixo de receber anualmente?</h2>
    <h1 style="color: white; font-size: 60px; margin: 0;">-{:.1f}%</h1>
    <div style="font-size: 80px; margin: 20px 0;">📉</div>
</div>
""".format(percentual_perda), unsafe_allow_html=True)
```

### 6.2 Alertas e Mensagens
```python
# Tipos de alertas
st.success("Operação realizada com sucesso!")
st.error("Erro ao processar dados")
st.warning("Atenção: dados podem estar desatualizados")
st.info("Informação adicional sobre o processo")

# Alert customizado
st.markdown("⚠️ **Atenção:** Verificar consistência dos dados")
```

### 6.3 Progress e Status
```python
# Barra de progresso
progress_bar = st.progress(0)
for i in range(100):
    progress_bar.progress(i + 1)
    time.sleep(0.01)

# Spinner para carregamento
with st.spinner('Carregando dados...'):
    dados = consultar_api(codigo_ibge, competencia)
```

### 6.4 Tabs para Organização
```python
tab1, tab2, tab3 = st.tabs(["Visão Geral", "Detalhes", "Configurações"])

with tab1:
    st.metric("Total", format_currency(total))

with tab2:
    st.dataframe(df_detalhado)

with tab3:
    mostrar_graficos = st.checkbox("Exibir gráficos")
```

---

## 7. Boas Práticas

### 7.1 Performance
```python
# Cache para funções pesadas
@st.cache_data
def carregar_dados_municipios():
    return ufbr.list_cidades()

# Cache para configurações
@st.cache_resource
def carregar_config():
    with open('config.json', 'r') as f:
        return json.load(f)
```

### 7.2 Tratamento de Erros
```python
try:
    codigo_ibge = ufbr.get_cidade(municipio_selecionado).codigo
    codigo_ibge = str(int(float(codigo_ibge)))[:-1]
    dados = consultar_api(codigo_ibge, competencia)

    if dados:
        exibir_dados(dados)
    else:
        st.warning("Nenhum dado encontrado para este município")

except AttributeError:
    st.error("Erro ao obter código IBGE do município")
except Exception as e:
    st.error(f"Erro ao consultar dados: {e}")
```

### 7.3 Formatação de Valores
```python
def format_currency(value):
    """Formatar valores monetários"""
    return f"R$ {value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

def format_percentage(value):
    """Formatar percentuais"""
    return f"{value:.1f}%"

def format_number(value):
    """Formatar números grandes"""
    return f"{value:,}".replace(',', '.')
```

### 7.4 Responsividade
```python
# Usar use_container_width para gráficos
st.plotly_chart(fig, use_container_width=True)

# Colunas se adaptam automaticamente em telas pequenas
col1, col2, col3 = st.columns(3)  # Empilha verticalmente em mobile

# Diferentes layouts para diferentes tamanhos
if st.get_option("browser.serverAddress") == "localhost":
    # Layout para desenvolvimento
    st.columns([1, 2, 1])
else:
    # Layout para produção
    st.columns([1, 3, 1])
```

### 7.5 Acessibilidade
```python
# Sempre usar labels descritivos
st.selectbox("Selecione um Estado (obrigatório)", options=estados)

# Help text para widgets complexos
st.metric(
    label="💰 Recurso Atual",
    value=format_currency(valor_atual),
    help="Valor baseado na classificação 'Bom' do indicador de qualidade"
)

# Alt text implícito para métricas com emojis
st.metric("💰 Receita", "R$ 1.000.000")  # Screen readers lerão "Receita"
```

---

## 8. Troubleshooting

### 8.1 Problemas Comuns

**Widget não atualiza:**
```python
# ❌ Problema: key duplicada
st.text_input("Nome", key="nome")
st.text_input("Sobrenome", key="nome")  # Erro!

# ✅ Solução: keys únicos
st.text_input("Nome", key="nome")
st.text_input("Sobrenome", key="sobrenome")
```

**Session state não persiste:**
```python
# ❌ Problema: não inicializar
if st.button("Incrementar"):
    st.session_state.counter += 1  # Erro se counter não existe

# ✅ Solução: inicializar sempre
if 'counter' not in st.session_state:
    st.session_state.counter = 0

if st.button("Incrementar"):
    st.session_state.counter += 1
```

**Plotly não carrega:**
```python
# ✅ Verificar se figura é válida
if fig and hasattr(fig, 'data') and fig.data:
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Não foi possível gerar o gráfico")
```

### 8.2 Debug
```python
# Mostrar valores de session state
if st.checkbox("Debug Mode"):
    st.write("Session State:", dict(st.session_state))
    st.write("Dados carregados:", 'dados' in st.session_state)
```

### 8.3 Logs
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def consultar_api_com_log(codigo_ibge, competencia):
    logger.info(f"Consultando API para {codigo_ibge}")
    try:
        dados = consultar_api(codigo_ibge, competencia)
        logger.info("Dados obtidos com sucesso")
        return dados
    except Exception as e:
        logger.error(f"Erro na API: {e}")
        return None
```

---

## 📚 Recursos Adicionais

- [Documentação Oficial Streamlit](https://docs.streamlit.io/)
- [Galeria de Componentes](https://streamlit.io/gallery)
- [Plotly Documentation](https://plotly.com/python/)
- [pyUFbr Documentation](https://github.com/GusFurtado/pyUFbr)

---

**Última atualização:** Setembro 2024
**Versão do Streamlit:** 1.x
**Projeto:** Sistema de Monitoramento de Financiamento da Saúde (papprefeito)