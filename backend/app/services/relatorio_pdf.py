"""Serviços utilitários para geração do relatório financeiro em PDF."""
from __future__ import annotations

from typing import Any, Dict, Iterable, Optional

from fpdf import FPDF

from app.models.schemas import ResumoFinanceiro


def _sanitize_text(value: str) -> str:
    """Garantir compatibilidade de caracteres com as fontes padrão do FPDF."""
    return value.encode('latin-1', 'ignore').decode('latin-1')


def _br_number(value: float, decimals: int = 2) -> str:
    """Formata números no padrão brasileiro (ponto como milhar e vírgula decimal)."""
    pattern = f"{{:,.{decimals}f}}"
    formatted = pattern.format(value)
    return formatted.replace(',', 'X').replace('.', ',').replace('X', '.')


def compute_financial_summary(
    resumos: Iterable[Dict[str, Any]],
    percas: Iterable[float]
) -> ResumoFinanceiro:
    """Calcula o resumo financeiro a partir dos resumos e perdas mensais."""
    resumos_list = list(resumos)
    percas_list = list(percas)

    if len(percas_list) < len(resumos_list):
        percas_list.extend([0.0] * (len(resumos_list) - len(percas_list)))
    elif len(percas_list) > len(resumos_list):
        percas_list = percas_list[:len(resumos_list)]

    monthly_received = [float(item.get('vlEfetivoRepasse') or 0.0) for item in resumos_list]
    total_perca_mensal = float(sum(percas_list))
    total_diferenca_anual = total_perca_mensal * 12.0
    total_real_anual = float(sum(monthly_received)) * 12.0
    total_recebido = float(sum(monthly_received))

    percentual = (total_diferenca_anual / total_real_anual * 100.0) if total_real_anual else 0.0

    return ResumoFinanceiro(
        total_perca_mensal=total_perca_mensal,
        total_diferenca_anual=total_diferenca_anual,
        percentual_perda_anual=percentual,
        total_recebido=total_recebido,
    )


def _draw_bar_chart(pdf: FPDF, atual: float, potencial: float, x_base: float, y_base: float, max_height: float = 80):
    """Desenha gráfico de barras proporcional."""
    bar_width = 35

    # Calcular alturas proporcionais
    max_value = potencial
    altura_atual = (atual / max_value) * max_height
    altura_potencial = max_height

    # Posições das barras
    bar1_x = x_base
    bar2_x = x_base + 95

    # Base das barras
    base_y = y_base + max_height

    # Desenhar barra atual (vermelha)
    pdf.set_fill_color(220, 53, 69)
    pdf.rect(bar1_x, base_y - altura_atual, bar_width, altura_atual, 'F')

    # Desenhar barra potencial (azul)
    pdf.set_fill_color(40, 116, 240)
    pdf.rect(bar2_x, base_y - altura_potencial, bar_width, altura_potencial, 'F')

    # Seta de crescimento
    _draw_arrow(pdf, bar1_x + bar_width + 5, bar2_x - 5, base_y - (altura_atual + altura_potencial) / 2)

    # Eixo Y com valores em milhões
    pdf.set_font('Helvetica', '', 8)
    pdf.set_text_color(100, 100, 100)

    for i in range(5):
        y_pos = base_y - (i * max_height / 4)
        value_millions = (max_value * i / 4) / 1000000
        pdf.set_xy(x_base - 20, y_pos - 2)
        pdf.cell(15, 4, f'{value_millions:.1f}mi', align='R')

        # Linha de grade
        pdf.set_draw_color(200, 200, 200)
        pdf.line(x_base - 5, y_pos, x_base + 150, y_pos)


def _draw_arrow(pdf: FPDF, start_x: float, end_x: float, y: float):
    """Desenha seta azul de crescimento."""
    pdf.set_draw_color(40, 116, 240)
    pdf.line(start_x, y, end_x, y)

    # Ponta da seta
    pdf.set_fill_color(40, 116, 240)
    pdf.rect(end_x - 3, y - 2, 3, 4, 'F')
    pdf.rect(end_x - 6, y - 1, 3, 2, 'F')


def _create_page_1_intro_destaque(pdf: FPDF, municipio_label: str, competencia: str, resumo: ResumoFinanceiro):
    """Página 1: Introdução + Destaque Principal."""
    pdf.add_page()

    # Título principal
    pdf.set_font('Helvetica', 'B', 18)
    pdf.set_text_color(14, 53, 102)
    pdf.cell(0, 10, _sanitize_text(f'Relatório de Projeção Financeira – Município de {municipio_label}'), ln=True, align='C')

    pdf.ln(8)

    # Saudação formal
    pdf.set_font('Helvetica', '', 12)
    pdf.set_text_color(51, 65, 85)
    pdf.cell(0, 8, _sanitize_text('Excelentíssimo(a) Senhor(a) Prefeito(a),'), ln=True)

    pdf.ln(4)

    # Texto introdutório
    intro = (
        "Com o objetivo de oferecer uma visão estratégica sobre a evolução dos "
        "recursos do município, apresentamos a seguir uma análise detalhada com base "
        "no cenário atual e projeções futuras."
    )
    pdf.multi_cell(0, 7, _sanitize_text(intro))

    pdf.ln(15)

    # Banner de destaque (mesmo estilo da versão atual)
    banner_y = pdf.get_y()
    pdf.set_fill_color(136, 19, 19)
    pdf.set_draw_color(136, 19, 19)
    pdf.set_x(10)
    pdf.cell(190, 22, '', ln=1, fill=True)

    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_xy(10, banner_y + 6)
    pdf.cell(190, 8, _sanitize_text('QUANTO EU DEIXO DE RECEBER ANUALMENTE?'), align='C')

    # Percentual em destaque
    percent_label = f"{_br_number(resumo.percentual_perda_anual, 2)}%"
    pdf.set_text_color(172, 16, 16)
    pdf.set_font('Helvetica', 'B', 46)
    pdf.set_xy(10, banner_y + 24)
    pdf.cell(190, 16, _sanitize_text(percent_label), align='C')

    pdf.ln(38)

    # Resumo dos valores
    pdf.set_font('Helvetica', '', 11)
    pdf.set_text_color(66, 82, 110)
    resumo_texto = (
        f"• Perda mensal estimada: R$ {_br_number(resumo.total_perca_mensal, 2)}\n"
        f"• Diferença anual estimada: R$ {_br_number(resumo.total_diferenca_anual, 2)}\n"
        f"• Total recebido mensalmente: R$ {_br_number(resumo.total_recebido, 2)}"
    )
    pdf.multi_cell(0, 6, _sanitize_text(resumo_texto))


def _create_page_2_infograficos(pdf: FPDF, municipio_label: str, resumo: ResumoFinanceiro):
    """Página 2: Infográficos Duplos - Comparativo Anual + Análise Mensal."""
    pdf.add_page()

    # Cálculos necessários
    recurso_atual_mensal = resumo.total_recebido
    acrescimo_mensal = resumo.total_perca_mensal
    recurso_potencial_mensal = recurso_atual_mensal + acrescimo_mensal

    recurso_atual_anual = recurso_atual_mensal * 12
    recurso_potencial_anual = recurso_atual_anual + resumo.total_diferenca_anual

    # SEÇÃO SUPERIOR: Comparativo Anual (50% da página)
    pdf.set_font('Helvetica', 'B', 16)
    pdf.set_text_color(14, 53, 102)
    pdf.ln(10)
    pdf.cell(0, 10, _sanitize_text(f'Comparativo de Recursos - Atenção Básica {municipio_label}'), ln=True, align='C')

    pdf.ln(10)

    # Títulos dos recursos
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(51, 51, 51)

    # Título esquerdo
    pdf.set_xy(25, pdf.get_y())
    pdf.cell(80, 8, _sanitize_text('Recurso Atenção Básica atual'), align='C')

    # Título direito
    pdf.set_xy(105, pdf.get_y())
    pdf.cell(80, 8, _sanitize_text('Recurso Atenção Básica potencial'), align='C')

    pdf.ln(15)

    # Valores dos recursos
    pdf.set_font('Helvetica', 'B', 14)
    atual_y = pdf.get_y()

    # Valor atual (esquerda)
    pdf.set_text_color(220, 53, 69)
    pdf.set_xy(25, atual_y)
    pdf.cell(80, 10, _sanitize_text(f'R$ {_br_number(recurso_atual_anual, 0)}'), align='C')

    # Valor potencial (direita)
    pdf.set_text_color(40, 116, 240)
    pdf.set_xy(105, atual_y)
    pdf.cell(80, 10, _sanitize_text(f'R$ {_br_number(recurso_potencial_anual, 0)}'), align='C')

    pdf.ln(20)

    # Gráfico de barras
    chart_y = pdf.get_y()
    _draw_bar_chart(pdf, recurso_atual_anual, recurso_potencial_anual, 40, chart_y, 60)

    pdf.ln(80)

    # SEÇÃO INFERIOR: Análise Mensal (50% da página)
    pdf.set_font('Helvetica', 'B', 16)
    pdf.set_text_color(14, 53, 102)
    pdf.cell(0, 10, _sanitize_text('Mensal'), ln=True, align='C')

    pdf.ln(8)

    # Valores mensais em três colunas
    col_width = 63
    current_y = pdf.get_y()

    # Recurso Atual (vermelho)
    pdf.set_xy(10, current_y)
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(220, 53, 69)
    pdf.cell(col_width, 8, _sanitize_text('Recurso Atual'), align='C')
    pdf.set_xy(10, current_y + 8)
    pdf.set_font('Helvetica', 'B', 16)
    pdf.cell(col_width, 10, _sanitize_text(f'R$ {_br_number(recurso_atual_mensal, 0)}'), align='C')

    # Recurso Potencial (preto)
    pdf.set_xy(73, current_y)
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(col_width, 8, _sanitize_text('Recurso Potencial'), align='C')
    pdf.set_xy(73, current_y + 8)
    pdf.set_font('Helvetica', 'B', 16)
    pdf.cell(col_width, 10, _sanitize_text(f'R$ {_br_number(recurso_potencial_mensal, 0)}'), align='C')

    # Acréscimo (azul)
    pdf.set_xy(136, current_y)
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(40, 116, 240)
    pdf.cell(col_width, 8, _sanitize_text('Acréscimo'), align='C')
    pdf.set_xy(136, current_y + 8)
    pdf.set_font('Helvetica', 'B', 16)
    pdf.cell(col_width, 10, _sanitize_text(f'R$ {_br_number(acrescimo_mensal, 0)}'), align='C')

    pdf.ln(25)

    # Destaque: Acréscimo Mensal de Receita
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(40, 116, 240)
    pdf.cell(0, 10, _sanitize_text('Acréscimo Mensal de Receita'), ln=True, align='C')

    # Linha sublinhada
    underline_y = pdf.get_y() - 2
    pdf.line(50, underline_y, 160, underline_y)

    pdf.ln(5)

    # Valor do acréscimo em destaque
    pdf.set_font('Helvetica', 'B', 20)
    pdf.cell(0, 12, _sanitize_text(f'R$ {_br_number(acrescimo_mensal, 0)}'), ln=True, align='C')

    # Seta irregular para cima (simulada)
    arrow_x = 105
    arrow_y = pdf.get_y() + 5
    pdf.set_fill_color(40, 116, 240)
    # Simular seta irregular com retângulos
    pdf.rect(arrow_x - 1, arrow_y, 2, 15, 'F')  # Haste
    pdf.rect(arrow_x - 4, arrow_y - 3, 8, 3, 'F')  # Ponta


def _create_page_3_impacto_conclusao(pdf: FPDF, resumo: ResumoFinanceiro):
    """Página 3: Impacto + Conclusão."""
    pdf.add_page()

    # SEÇÃO SUPERIOR: Impacto visual (40% da página)
    pdf.ln(15)

    # Percentual grande
    percent_label = f"{_br_number(resumo.percentual_perda_anual, 2)}%"
    pdf.set_text_color(172, 16, 16)
    pdf.set_font('Helvetica', 'B', 42)
    pdf.cell(0, 18, _sanitize_text(percent_label), align='C', ln=True)

    # Símbolo de igualdade
    pdf.set_text_color(14, 98, 175)
    pdf.set_font('Helvetica', 'B', 36)
    pdf.ln(4)
    pdf.cell(0, 16, _sanitize_text('='), align='C', ln=True)

    # Caixa com valor destacado
    diferenca_label = _br_number(round(resumo.total_diferenca_anual), 0)
    box_width = 160
    box_height = 42
    x_start = (210 - box_width) / 2
    y_start = pdf.get_y() + 6

    pdf.set_fill_color(207, 213, 225)
    pdf.rect(x_start + 3, y_start + 3, box_width, box_height, 'F')

    pdf.set_fill_color(255, 255, 255)
    pdf.rect(x_start, y_start, box_width, box_height, 'F')

    pdf.set_text_color(14, 98, 175)
    pdf.set_font('Helvetica', 'B', 34)
    pdf.set_xy(x_start, y_start + 10)
    pdf.cell(box_width, 18, _sanitize_text(f'R$ {diferenca_label}'), align='C')

    pdf.ln(box_height + 25)

    # SEÇÃO CENTRAL: Mensagem motivacional (30% da página)
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(40, 167, 69)
    pdf.cell(0, 10, _sanitize_text('MAIS RECURSO E UMA MELHOR QUALIDADE DE SAÚDE PARA A POPULAÇÃO!'), align='C', ln=True)

    pdf.ln(15)

    # SEÇÃO INFERIOR: Considerações finais (30% da página)
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(14, 53, 102)
    pdf.cell(0, 10, _sanitize_text('4. Considerações Finais'), ln=True)

    pdf.ln(5)

    # Texto das considerações
    pdf.set_font('Helvetica', '', 11)
    pdf.set_text_color(51, 65, 85)
    consideracoes = (
        "O acompanhamento constante desses indicadores permitirá à administração "
        "tomar decisões mais assertivas, equilibrando gastos e planejando investimentos "
        "futuros com segurança. O avanço até o Cenário Ótimo permitirá à cidade ampliar "
        "a qualidade dos serviços prestados à população e realizar obras de maior impacto "
        "social e econômico."
    )
    pdf.multi_cell(0, 6, _sanitize_text(consideracoes))

    pdf.ln(8)

    # Texto de suporte
    pdf.multi_cell(0, 6, _sanitize_text(
        "Estamos à disposição para auxiliar na interpretação dos dados e na definição de "
        "ações estratégicas para maximizar esse crescimento."
    ))

    pdf.ln(15)

    # Assinatura
    pdf.set_font('Helvetica', '', 11)
    pdf.cell(0, 6, _sanitize_text('Atenciosamente,'), ln=True)
    pdf.ln(2)
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 6, _sanitize_text('Mais Gestor'), ln=True)
    pdf.cell(0, 6, _sanitize_text('Alysson Ribeiro'), ln=True)


def create_pdf_report(
    *,
    municipio_nome: Optional[str],
    uf: Optional[str],
    competencia: str,
    resumo: ResumoFinanceiro,
) -> bytes:
    """Cria o relatório em PDF com 3 páginas conforme especificações do épico brownfield."""
    municipio_label = municipio_nome or 'Município'
    if uf:
        municipio_label = f"{municipio_label}/{uf.upper()}"

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=18)

    # PÁGINA 1: Introdução + Destaque Principal
    _create_page_1_intro_destaque(pdf, municipio_label, competencia, resumo)

    # PÁGINA 2: Infográficos Duplos (Comparativo Anual + Análise Mensal)
    _create_page_2_infograficos(pdf, municipio_label, resumo)

    # PÁGINA 3: Impacto + Conclusão
    _create_page_3_impacto_conclusao(pdf, resumo)

    buffer = pdf.output(dest='S')
    return buffer
