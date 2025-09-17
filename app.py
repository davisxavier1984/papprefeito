# Sistema de Monitoramento de Financiamento da Saúde - papprefeito
import streamlit as st
import pandas as pd
import json
import os
import sys
import plotly.graph_objects as go
from pyUFbr.baseuf import ufbr
from datetime import datetime
import io

# Imports para geração de PDF
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm, inch
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    import plotly.io as pio
    import matplotlib
    matplotlib.use('Agg')  # Backend sem GUI para ambientes de produção
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.ticker import FuncFormatter
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

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









def main():
    st.set_page_config(page_title="Mais Gestor - Landing Page", layout="wide")

    # Logo centralizada
    col_logo1, col_logo2, col_logo3 = st.columns([1, 2, 1])
    with col_logo2:
        st.image("logo_colorida_mg.png", width=400)

    # Container principal para seleções
    with st.container(border=True):
        st.markdown("### 📍 Seleção de Município")

        # Layout de colunas otimizado
        col1, col2 = st.columns(2, gap="medium")

        with col1:
            estados = ufbr.list_uf
            uf_selecionada = st.selectbox(
                "🗺️ Estado",
                options=estados,
                help="Escolha o estado para consultar dados municipais",
                placeholder="Selecione um estado..."
            )

        with col2:
            municipio_selecionado = None
            if uf_selecionada:
                municipios = ufbr.list_cidades(uf_selecionada)
                municipio_selecionado = st.selectbox(
                    "🏛️ Município",
                    options=municipios,
                    help="Escolha o município para análise financeira",
                    placeholder="Selecione um município..."
                )
            else:
                st.selectbox(
                    "🏛️ Município",
                    options=[],
                    help="Primeiro selecione um estado",
                    placeholder="Primeiro selecione um estado...",
                    disabled=True
                )

        # Informações do município (se disponível)
        if uf_selecionada and municipio_selecionado:
            st.markdown("---")
            col3, col4 = st.columns(2, gap="medium")

            with col3:
                estrato_placeholder = st.empty()
                estrato_placeholder.text_input(
                    "📊 Estrato",
                    value="-",
                    disabled=True,
                    key="estrato_default",
                    help="Classificação do município por índice de equidade"
                )

            with col4:
                populacao_placeholder = st.empty()
                populacao_placeholder.text_input(
                    "👥 População",
                    value="-",
                    disabled=True,
                    key="populacao_default",
                    help="População total do município"
                )

    # Competência automática (não exibida)
    competencia = get_latest_competencia()

    # Consultar dados quando município for selecionado
    if uf_selecionada and municipio_selecionado:
        try:
            codigo_ibge = ufbr.get_cidade(municipio_selecionado).codigo
            codigo_ibge = str(int(float(codigo_ibge)))[:-1]

            # Consultar API automaticamente
            dados = consultar_api(codigo_ibge, competencia)

            if dados:
                # Salvar dados na sessão
                st.session_state['dados'] = dados
                st.session_state['municipio_selecionado'] = municipio_selecionado
                st.session_state['uf_selecionada'] = uf_selecionada

                # Atualizar estrato e população
                pagamentos = dados['pagamentos'][0]
                estrato_valor = pagamentos.get('dsFaixaIndiceEquidadeEsfEap', 'N/A')
                populacao_valor = f"{pagamentos.get('qtPopulacao', 0):,}".replace(',', '.')

                estrato_placeholder.text_input("📊 Estrato", value=estrato_valor, disabled=True, key="estrato_updated")
                populacao_placeholder.text_input("👥 População", value=populacao_valor, disabled=True, key="populacao_updated")

                # Espaçamento e separador elegante
                st.markdown("<br>", unsafe_allow_html=True)

                # Chamar função para exibir seções da landing page
                exibir_landing_page(dados)

        except AttributeError:
            st.error("⚠️ Erro ao obter código IBGE do município. Verifique se o município foi selecionado corretamente.")
        except Exception as e:
            st.error(f"❌ Erro ao consultar dados da API: {e}")
            st.info("💡 Tente selecionar outro município ou verifique sua conexão com a internet.")

def exibir_landing_page(dados):
    """Exibe apenas o botão de geração de PDF"""
    if not dados or 'pagamentos' not in dados:
        return

    municipio = st.session_state.get('municipio_selecionado', '')
    uf = st.session_state.get('uf_selecionada', '')

    # Espaçamento
    st.markdown("<br>", unsafe_allow_html=True)

    # Container destacado para o botão PDF
    with st.container(border=True):
        st.markdown("""
        <div style="text-align: center; margin: 20px 0;">
            <h3 style="color: #2C3E50; font-size: 1.5rem; margin-bottom: 10px;">
                📄 Relatório Detalhado Completo
            </h3>
            <p style="color: #7F8C8D; font-size: 1rem; margin-bottom: 0;">
                Baixe a análise completa em 4 páginas com todos os dados e gráficos
            </p>
        </div>
        """, unsafe_allow_html=True)

        col_pdf1, col_pdf2, col_pdf3 = st.columns([1, 2, 1])

        with col_pdf2:
            if PDF_AVAILABLE:
                if st.button("📥 Gerar Relatório PDF", type="primary", use_container_width=True):
                    with st.spinner('Gerando relatório PDF...'):
                        try:
                            pdf_bytes = gerar_relatorio_pdf(dados, municipio, uf)
                            if pdf_bytes:
                                st.download_button(
                                    label="📄 Download do Relatório PDF",
                                    data=pdf_bytes,
                                    file_name=f"relatorio_financeiro_{municipio}_{uf}_{datetime.now().strftime('%Y%m%d')}.pdf",
                                    mime="application/pdf",
                                    type="secondary",
                                    use_container_width=True
                                )
                                st.success("✅ Relatório gerado com sucesso!")
                            else:
                                st.error("❌ Erro ao gerar relatório PDF")
                        except Exception as e:
                            st.error(f"❌ Erro ao gerar PDF: {str(e)}")
            else:
                st.warning("⚠️ Para gerar PDF, instale as dependências: `pip install reportlab kaleido`")
                st.info("💡 O relatório PDF contém 4 páginas com análise completa dos dados financeiros")


def gerar_grafico_para_pdf(valor_regular, valor_otimo, classificacao_atual='Regular'):
    """Gera o gráfico comparativo usando matplotlib e retorna como bytes para o PDF"""
    if not PDF_AVAILABLE:
        return None

    # Configurar matplotlib para não usar GUI
    plt.ioff()

    # Criar figura
    fig, ax = plt.subplots(figsize=(6.5, 5))

    # Dados para o gráfico
    categorias = ['Regular\n(Base)', 'Ótimo\n(Potencial)']
    valores = [valor_regular, valor_otimo]
    cores = [CORES_PADRAO['alerta'], CORES_PADRAO['positivo']]

    # Criar gráfico de barras
    bars = ax.bar(categorias, valores, color=cores, width=0.6, edgecolor='white', linewidth=2)

    # Adicionar valores nas barras
    for i, (bar, valor) in enumerate(zip(bars, valores)):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + valor * 0.02,
                format_currency(valor),
                ha='center', va='bottom', fontsize=12, fontweight='bold', color='black')

    # Adicionar anotação de diferença
    diferenca = valor_otimo - valor_regular
    y_pos = (valor_regular + valor_otimo) / 2

    # Seta e caixa de texto para diferença
    ax.annotate(f'Diferença\n{format_currency(diferenca)}',
                xy=(0.5, y_pos), xytext=(1.2, y_pos),
                ha='center', va='center',
                bbox=dict(boxstyle="round,pad=0.3", facecolor=CORES_PADRAO['destaque'],
                         edgecolor='white', linewidth=2),
                arrowprops=dict(arrowstyle='->', color=CORES_PADRAO['destaque'], lw=2),
                fontsize=10, fontweight='bold', color='white')

    # Customizar eixos
    ax.set_title('Comparação: Regular vs Ótimo - Potencial de Recursos',
                fontsize=16, fontweight='bold', pad=20, color='#2C3E50')

    ax.set_ylabel('Valor Mensal', fontsize=12, fontweight='bold', color='#2C3E50')

    # Formatador para eixo Y
    def currency_formatter(x, pos):
        return f'R$ {x:,.0f}'.replace(',', '.')

    ax.yaxis.set_major_formatter(FuncFormatter(currency_formatter))

    # Configurar grid e estilo
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)

    # Remover bordas superiores e direitas
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#cccccc')
    ax.spines['bottom'].set_color('#cccccc')

    # Ajustar margem superior para a anotação
    ax.set_ylim(0, max(valores) * 1.15)
    ax.set_xlim(-0.5, 1.8)

    # Configurar layout
    plt.tight_layout()

    # Converter para bytes
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    img_buffer.seek(0)
    img_bytes = img_buffer.getvalue()

    # Fechar figura para liberar memória
    plt.close(fig)

    return img_bytes

def _adicionar_timbrado_background(canvas, doc):
    """Adiciona timbrado como fundo da página"""
    try:
        # Verificar se o arquivo timbrado existe
        timbrado_path = 'timbrado.jpg'
        if os.path.exists(timbrado_path):
            # Desenhar timbrado cobrindo toda a página A4
            canvas.drawImage(timbrado_path,
                           x=0, y=0,
                           width=A4[0], height=A4[1],
                           preserveAspectRatio=True,
                           anchor='c')
    except Exception as e:
        # Se houver erro, continuar sem timbrado
        print(f"Aviso: Não foi possível carregar timbrado: {e}")

def criar_dashboard_primeira_pagina(municipio, uf, pagamentos):
    """Cria dashboard visual para primeira página do PDF"""
    if not PDF_AVAILABLE:
        return []

    # Extrair dados
    estrato_valor = pagamentos.get('dsFaixaIndiceEquidadeEsfEap', 'N/A')
    populacao_valor = f"{pagamentos.get('qtPopulacao', 0):,}".replace(',', '.')
    competencia = get_latest_competencia()

    # Determinar cor do estrato baseada no valor
    if 'alto' in estrato_valor.lower():
        cor_estrato = colors.HexColor('#27AE60')  # Verde - positivo
    elif 'médio' in estrato_valor.lower() or 'medio' in estrato_valor.lower():
        cor_estrato = colors.HexColor('#F39C12')  # Laranja - neutro
    elif 'baixo' in estrato_valor.lower():
        cor_estrato = colors.HexColor('#E74C3C')  # Vermelho - negativo
    else:
        cor_estrato = colors.HexColor('#95A5A6')  # Cinza - neutro

    # Estilo para os cards
    card_style = ParagraphStyle(
        'CardStyle',
        fontSize=12,
        textColor=colors.white,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    value_style = ParagraphStyle(
        'ValueStyle',
        fontSize=16,
        textColor=colors.white,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        spaceAfter=5
    )

    # Dados dos cards em formato de tabela 2x2
    dashboard_data = [
        [
            # Card Município
            [
                Paragraph("🏛️ MUNICÍPIO", card_style),
                Paragraph(f"{municipio}", value_style),
                Paragraph(f"{uf}", card_style)
            ],
            # Card População
            [
                Paragraph("👥 POPULAÇÃO", card_style),
                Paragraph(f"{populacao_valor}", value_style),
                Paragraph("habitantes", card_style)
            ]
        ],
        [
            # Card Estrato
            [
                Paragraph("📊 ESTRATO", card_style),
                Paragraph(f"{estrato_valor}", value_style),
                Paragraph("classificação", card_style)
            ],
            # Card Competência
            [
                Paragraph("📅 COMPETÊNCIA", card_style),
                Paragraph(f"{competencia}", value_style),
                Paragraph("período", card_style)
            ]
        ]
    ]

    # Criar tabela dashboard
    dashboard_table = Table(dashboard_data, colWidths=[2.5*inch, 2.5*inch], rowHeights=[1.2*inch, 1.2*inch])
    dashboard_table.setStyle(TableStyle([
        # Card Município (azul)
        ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#3498DB')),
        ('VALIGN', (0, 0), (0, 0), 'MIDDLE'),
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),

        # Card População (verde)
        ('BACKGROUND', (1, 0), (1, 0), colors.HexColor('#27AE60')),
        ('VALIGN', (1, 0), (1, 0), 'MIDDLE'),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),

        # Card Estrato (cor dinâmica)
        ('BACKGROUND', (0, 1), (0, 1), cor_estrato),
        ('VALIGN', (0, 1), (0, 1), 'MIDDLE'),
        ('ALIGN', (0, 1), (0, 1), 'CENTER'),

        # Card Competência (cinza)
        ('BACKGROUND', (1, 1), (1, 1), colors.HexColor('#95A5A6')),
        ('VALIGN', (1, 1), (1, 1), 'MIDDLE'),
        ('ALIGN', (1, 1), (1, 1), 'CENTER'),

        # Espaçamento entre cards
        ('LEFTPADDING', (0, 0), (-1, -1), 15),
        ('RIGHTPADDING', (0, 0), (-1, -1), 15),
        ('TOPPADDING', (0, 0), (-1, -1), 15),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 15),

        # Remover bordas da tabela
        ('GRID', (0, 0), (-1, -1), 0, colors.white),
    ]))

    return [dashboard_table]

def gerar_relatorio_pdf(dados, municipio, uf):
    """Gera relatório PDF de 4 páginas com análise financeira"""
    if not PDF_AVAILABLE:
        st.error("Bibliotecas necessárias para PDF não estão instaladas. Execute: pip install reportlab")
        return None

    if not dados or 'pagamentos' not in dados:
        st.error("Dados não disponíveis para gerar relatório")
        return None

    pagamentos = dados['pagamentos'][0]

    # Validar e extrair dados
    try:
        # Calcular valores corrigidos com validação
        vlQualidadeEsf = float(pagamentos.get('vlQualidadeEsf', 0))
        vlPagamentoEmulti = float(pagamentos.get('vlPagamentoEmultiQualidade', 0))
        vlPagamentoEsb = float(pagamentos.get('vlPagamentoEsb40hQualidade', 0))

        valor_atual = vlQualidadeEsf + vlPagamentoEmulti + vlPagamentoEsb

        # Validar se há valores válidos
        if valor_atual <= 0:
            st.error("❌ Erro: Valores de financiamento não encontrados ou inválidos")
            return None

    except (ValueError, TypeError) as e:
        st.error(f"❌ Erro ao processar valores financeiros: {e}")
        return None

    # Obter classificação atual com validação
    classificacao_atual = pagamentos.get('dsClassificacaoQualidadeEsfEap', 'Bom')
    classificacoes_validas = ['Ótimo', 'Bom', 'Suficiente', 'Regular']

    if classificacao_atual not in classificacoes_validas:
        classificacao_atual = 'Bom'  # Valor padrão seguro

    # Valores de referência baseados nas portarias oficiais
    # Assumindo principalmente eSF que representa a maior parte dos recursos
    VALORES_REFERENCIA = {
        'Ótimo': 8000,
        'Bom': 6000,
        'Suficiente': 4000,
        'Regular': 2000
    }

    # Calcular valores baseados na proporção real entre classificações
    valor_referencia_atual = VALORES_REFERENCIA.get(classificacao_atual, 6000)
    valor_referencia_otimo = VALORES_REFERENCIA['Ótimo']
    valor_referencia_regular = VALORES_REFERENCIA['Regular']

    # Calcular valores proporcionais mantendo a base atual
    try:
        fator_multiplicador = valor_atual / valor_referencia_atual if valor_referencia_atual > 0 else 1
        valor_otimo = valor_referencia_otimo * fator_multiplicador
        valor_regular = valor_referencia_regular * fator_multiplicador

        # Validar se os valores calculados são razoáveis
        if valor_otimo <= 0 or valor_regular < 0:
            st.error("❌ Erro: Valores calculados são inválidos")
            return None

        # Calcular diferença anual do Regular para o Ótimo
        diferenca_anual = (valor_otimo - valor_regular) * 12

        # Calcular percentual de ganho do Regular para o Ótimo
        if valor_regular > 0:
            percentual_ganho = ((valor_otimo - valor_regular) / valor_regular) * 100
        else:
            percentual_ganho = 0

        # Validar percentual razoável (máximo 400% que seria de Regular para Ótimo)
        if percentual_ganho > 500:
            st.warning("⚠️ Aviso: Percentual de ganho muito alto, verifique os dados")

    except (ZeroDivisionError, ValueError) as e:
        st.error(f"❌ Erro nos cálculos de projeção: {e}")
        return None

    # Configurar PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=144, bottomMargin=18)
    story = []
    styles = getSampleStyleSheet()

    # Estilos customizados
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#2C3E50')
    )

    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=20,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#34495E')
    )

    highlight_style = ParagraphStyle(
        'Highlight',
        parent=styles['Normal'],
        fontSize=36,
        spaceAfter=20,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#E74C3C'),
        fontName='Helvetica-Bold'
    )

    # PÁGINA 1 - CAPA

    story.append(Spacer(1, 20))
    story.append(Paragraph("Relatório de Análise Financeira", title_style))
    story.append(Paragraph("Sistema de Monitoramento de Financiamento da Saúde", subtitle_style))

    story.append(Spacer(1, 40))

    # Dashboard visual da primeira página
    dashboard_elements = criar_dashboard_primeira_pagina(municipio, uf, pagamentos)
    for element in dashboard_elements:
        story.append(element)

    story.append(Spacer(1, 30))

    # Informações adicionais
    info_data = [
        ['Data do Relatório:', datetime.now().strftime('%d/%m/%Y')],
    ]

    info_table = Table(info_data, colWidths=[2*inch, 3*inch])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    story.append(info_table)
    story.append(PageBreak())

    # PÁGINA 2 - ANÁLISE DE POTENCIAL
    story.append(Paragraph("Análise de Potencial de Recursos", title_style))
    story.append(Spacer(1, 30))

    story.append(Paragraph("Potencial de aumento de recursos da classificação Regular para Ótimo:", subtitle_style))
    story.append(Spacer(1, 20))

    story.append(Paragraph(f"+{percentual_ganho:.1f}%", highlight_style))
    story.append(Spacer(1, 30))

    story.append(Paragraph(f"Este percentual corresponde a <b>{format_currency(diferenca_anual)}</b> anuais que poderiam ser recebidos evoluindo da classificação Regular para Ótimo.", styles['Normal']))
    story.append(Spacer(1, 20))

    story.append(Paragraph("Este valor adicional poderia fazer uma diferença significativa na gestão da saúde do município, permitindo:", styles['Normal']))
    story.append(Spacer(1, 10))

    beneficios = [
        "• Ampliação dos serviços de atenção básica",
        "• Melhoria da infraestrutura das unidades de saúde",
        "• Contratação de mais profissionais",
        "• Investimento em equipamentos e tecnologia",
        "• Programas de prevenção e promoção da saúde"
    ]

    for beneficio in beneficios:
        story.append(Paragraph(beneficio, styles['Normal']))
        story.append(Spacer(1, 5))

    story.append(PageBreak())

    # PÁGINA 3 - GRÁFICO E MÉTRICAS
    story.append(Paragraph("Comparativo de Recursos e Métricas", title_style))
    story.append(Spacer(1, 20))

    # Adicionar gráfico
    try:
        grafico_img = gerar_grafico_para_pdf(valor_regular, valor_otimo, 'Regular')
        if grafico_img:
            img_buffer = io.BytesIO(grafico_img)
            graph_img = Image(img_buffer, width=5*inch, height=3.2*inch)
            graph_img.hAlign = 'CENTER'
            story.append(graph_img)
    except Exception as e:
        story.append(Paragraph(f"Erro ao gerar gráfico: {str(e)}", styles['Normal']))

    story.append(Spacer(1, 30))

    # Tabela de métricas
    metricas_data = [
        ['Métrica', 'Valor', 'Descrição'],
        ['Recurso Atual', format_currency(valor_atual), f'Classificação "{classificacao_atual}"'],
        ['Recurso Base (Regular)', format_currency(valor_regular), 'Classificação "Regular"'],
        ['Recurso Potencial (Ótimo)', format_currency(valor_otimo), 'Classificação "Ótimo"'],
        ['Acréscimo Possível', format_currency(valor_otimo - valor_regular), f'+{percentual_ganho:.1f}%'],
        ['Ganho Potencial Anual', format_currency(diferenca_anual), 'Valor adicional anual (Regular → Ótimo)']
    ]

    metricas_table = Table(metricas_data, colWidths=[2*inch, 1.5*inch, 2.5*inch])
    metricas_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498DB')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    story.append(metricas_table)
    story.append(PageBreak())

    # PÁGINA 4 - CONCLUSÕES E RECOMENDAÇÕES
    story.append(Paragraph("Conclusões e Recomendações", title_style))
    story.append(Spacer(1, 30))

    story.append(Paragraph("Resumo Executivo", subtitle_style))
    story.append(Paragraph(f"O município de {municipio}/{uf} tem potencial para aumentar seus recursos em <b>{format_currency(valor_otimo - valor_regular)}</b> mensais, representando um acréscimo de <b>{percentual_ganho:.1f}%</b> evoluindo da classificação Regular para Ótimo.", styles['Normal']))
    story.append(Spacer(1, 20))

    story.append(Paragraph("Benefícios Esperados", subtitle_style))
    story.append(Paragraph("• <b>Mais recursos:</b> Aumento significativo no financiamento da saúde", styles['Normal']))
    story.append(Paragraph("• <b>Melhor qualidade:</b> Elevação dos indicadores de qualidade da atenção básica", styles['Normal']))
    story.append(Paragraph("• <b>População beneficiada:</b> Melhoria no atendimento para toda a população", styles['Normal']))
    story.append(Spacer(1, 20))

    story.append(Paragraph("Recomendações", subtitle_style))
    story.append(Paragraph("1. Implementar ações para melhoria dos indicadores de qualidade", styles['Normal']))
    story.append(Paragraph("2. Investir na capacitação das equipes de saúde", styles['Normal']))
    story.append(Paragraph("3. Modernizar os processos e sistemas de gestão", styles['Normal']))
    story.append(Paragraph("4. Monitorar continuamente os indicadores", styles['Normal']))
    story.append(Spacer(1, 40))

    story.append(Paragraph("Sistema de Monitoramento de Financiamento da Saúde", subtitle_style))

    # Construir PDF com timbrado de fundo
    doc.build(story,
             onFirstPage=_adicionar_timbrado_background,
             onLaterPages=_adicionar_timbrado_background)
    buffer.seek(0)
    return buffer.getvalue()

if __name__ == "__main__":
    main()