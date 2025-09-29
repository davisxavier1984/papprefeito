"""Serviços utilitários para geração do relatório financeiro em PDF usando HTML-to-PDF."""
from __future__ import annotations

import html
import base64
from typing import Any, Dict, Iterable, Optional
from pathlib import Path
import weasyprint

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


def _mix_with_white(color: tuple[int, int, int], factor: float) -> tuple[int, int, int]:
    """Mistura uma cor com branco para gerar tonalidades mais suaves."""
    factor = max(0.0, min(1.0, factor))
    return tuple(int(component + (255 - component) * factor) for component in color)


def _safe_ratio(value: float, total: float) -> float:
    """Garante um valor proporcional entre 0 e 1 evitando divisões inválidas."""
    if total <= 0:
        return 0.0
    ratio = value / total
    return max(0.0, min(1.0, ratio))


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


def _draw_financial_cards(pdf: FPDF, resumo: ResumoFinanceiro):
    """Desenha cards em grade com visual aprimorado para a primeira página."""

    potencial_mensal = resumo.total_recebido + resumo.total_perca_mensal
    potencial_anual = potencial_mensal * 12
    percentual_perda = resumo.percentual_perda_anual

    ratio_perda_mensal = _safe_ratio(resumo.total_perca_mensal, potencial_mensal)
    ratio_diferenca_anual = _safe_ratio(resumo.total_diferenca_anual, potencial_anual)
    ratio_recebimento_atual = _safe_ratio(resumo.total_recebido, potencial_mensal)

    cards_data = [
        {
            'titulo': 'PERDA MENSAL',
            'valor': f'R$ {_br_number(resumo.total_perca_mensal, 0)}',
            'descricao': 'recursos que poderiam melhorar a saúde',
            'detalhe': f'Equivalente a R$ {_br_number(resumo.total_diferenca_anual, 0)} por ano',
            'tag': 'Oportunidade',
            'cor_tema': (231, 76, 60),
            'cor_valor': (192, 57, 43),
            'cor_descricao': (117, 128, 138),
            'ratio': ratio_perda_mensal,
            'indicador': f'{int(round(ratio_perda_mensal * 100))}% do potencial mensal',
        },
        {
            'titulo': 'DIFERENÇA ANUAL',
            'valor': f'R$ {_br_number(resumo.total_diferenca_anual, 0)}',
            'descricao': 'valor total perdido no ano',
            'detalhe': f'Impacto de {percentual_perda:.1f}% do orçamento anual',
            'tag': 'Visão anual',
            'cor_tema': (243, 156, 18),
            'cor_valor': (211, 133, 10),
            'cor_descricao': (117, 128, 138),
            'ratio': ratio_diferenca_anual,
            'indicador': f'{int(round(ratio_diferenca_anual * 100))}% do potencial anual',
        },
        {
            'titulo': 'RECEBIMENTO ATUAL',
            'valor': f'R$ {_br_number(resumo.total_recebido, 0)}',
            'descricao': 'recursos mensais atuais',
            'detalhe': f'Potencial com ajuste: R$ {_br_number(potencial_mensal, 0)}',
            'tag': 'Cenário atual',
            'cor_tema': (46, 204, 113),
            'cor_valor': (39, 174, 96),
            'cor_descricao': (117, 128, 138),
            'ratio': ratio_recebimento_atual,
            'indicador': f'{int(round(ratio_recebimento_atual * 100))}% do potencial mensal',
        }
    ]

    page_width = 210
    margin = 12
    available_width = page_width - (2 * margin)
    cards_per_row = 3
    gap_x = 6
    gap_y = 12
    card_width = (available_width - (gap_x * (cards_per_row - 1))) / cards_per_row
    card_height = 72
    header_height = 22
    shadow_offset = 2.4
    inner_padding = 2.0
    progress_height = 5
    current_y = pdf.get_y() + 12
    icon_symbols = ['!', '+', '$']

    for index, card in enumerate(cards_data):
        row = index // cards_per_row
        column = index % cards_per_row
        card_x = margin + column * (card_width + gap_x)
        card_y = current_y + row * (card_height + gap_y)

        # sombra suave
        pdf.set_fill_color(226, 231, 240)
        pdf.rect(card_x + shadow_offset, card_y + shadow_offset, card_width, card_height, 'F')

        # base com tonalidade do tema
        pdf.set_fill_color(*_mix_with_white(card['cor_tema'], 0.85))
        pdf.rect(card_x, card_y, card_width, card_height, 'F')

        inner_x = card_x + inner_padding
        inner_y = card_y + inner_padding
        inner_width = card_width - (2 * inner_padding)
        inner_height = card_height - (2 * inner_padding)

        # corpo branco com borda temática
        pdf.set_fill_color(255, 255, 255)
        pdf.rect(inner_x, inner_y, inner_width, inner_height, 'F')

        pdf.set_draw_color(*_mix_with_white(card['cor_tema'], 0.6))
        pdf.set_line_width(0.4)
        pdf.rect(inner_x, inner_y, inner_width, inner_height, 'D')

        # faixa superior colorida
        pdf.set_fill_color(*card['cor_tema'])
        pdf.rect(inner_x, inner_y, inner_width, header_height, 'F')

        # selo informativo
        tag_text = _sanitize_text(card['tag'])
        if tag_text:
            tag_width = pdf.get_string_width(tag_text) + 6
            tag_x = inner_x + inner_width - tag_width - 4
            tag_y = inner_y + 4
            pdf.set_fill_color(*_mix_with_white(card['cor_tema'], 0.75))
            pdf.rect(tag_x, tag_y, tag_width, 7, 'F')
            pdf.set_text_color(*card['cor_tema'])
            pdf.set_font('Helvetica', 'B', 7)
            pdf.set_xy(tag_x, tag_y + 1)
            pdf.cell(tag_width, 5, tag_text, align='C')

        # ícone em destaque
        icon_diameter = 14
        icon_box_x = inner_x + 6
        icon_box_y = inner_y + (header_height - icon_diameter) / 2
        pdf.set_fill_color(*_mix_with_white(card['cor_tema'], 0.55))
        pdf.ellipse(icon_box_x, icon_box_y, icon_diameter, icon_diameter, 'F')

        pdf.set_text_color(*card['cor_tema'])
        pdf.set_font('Helvetica', 'B', 11)
        pdf.set_xy(icon_box_x, icon_box_y + 3)
        pdf.cell(icon_diameter, 8, icon_symbols[index], align='C')

        # título centralizado na faixa colorida
        pdf.set_text_color(255, 255, 255)
        pdf.set_font('Helvetica', 'B', 11)
        pdf.set_xy(inner_x + icon_diameter + 14, inner_y + 6)
        pdf.cell(inner_width - icon_diameter - 40, 8, _sanitize_text(card['titulo']), align='L')

        body_start = inner_y + header_height
        body_x = inner_x + 12
        body_width = inner_width - 24

        # valor em destaque
        pdf.set_text_color(*card['cor_valor'])
        pdf.set_font('Helvetica', 'B', 17)
        pdf.set_xy(body_x, body_start + 6)
        pdf.cell(body_width, 10, _sanitize_text(card['valor']), align='L')

        # descrição complementar
        pdf.set_text_color(*card['cor_descricao'])
        pdf.set_font('Helvetica', '', 9)
        pdf.set_xy(body_x, body_start + 22)
        pdf.cell(body_width, 6, _sanitize_text(card['descricao']), align='L')

        # detalhe adicional
        pdf.set_font('Helvetica', '', 8)
        pdf.set_xy(body_x, body_start + 30)
        pdf.cell(body_width, 6, _sanitize_text(card['detalhe']), align='L')

        # indicador visual de progresso
        progress_width = body_width
        progress_y = body_start + 40
        pdf.set_fill_color(237, 242, 250)
        pdf.rect(body_x, progress_y, progress_width, progress_height, 'F')

        progress_fill_width = progress_width * card['ratio']
        if progress_fill_width > 0:
            pdf.set_fill_color(*card['cor_tema'])
            pdf.rect(body_x, progress_y, progress_fill_width, progress_height, 'F')

        pdf.set_text_color(*card['cor_descricao'])
        pdf.set_font('Helvetica', '', 8)
        pdf.set_xy(body_x, progress_y + progress_height + 1)
        pdf.cell(progress_width, 6, _sanitize_text(card['indicador']), align='L')

    rows = (len(cards_data) + cards_per_row - 1) // cards_per_row
    final_y = current_y + (rows * card_height) + ((rows - 1) * gap_y)
    pdf.set_y(final_y)
    pdf.ln(8)

    pdf.set_line_width(0.2)
    pdf.set_text_color(0, 0, 0)
    pdf.set_draw_color(0, 0, 0)


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

    # Cards com métricas financeiras
    _draw_financial_cards(pdf, resumo)


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
    """Cria o relatório em PDF usando templates HTML modernos."""
    return create_html_pdf_report(
        municipio_nome=municipio_nome,
        uf=uf,
        competencia=competencia,
        resumo=resumo
    )


def create_fpdf_report(
    *,
    municipio_nome: Optional[str],
    uf: Optional[str],
    competencia: str,
    resumo: ResumoFinanceiro,
) -> bytes:
    """Cria o relatório em PDF com 3 páginas usando FPDF (versão legada)."""
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


def create_html_pdf_report(
    *,
    municipio_nome: Optional[str],
    uf: Optional[str],
    competencia: str,
    resumo: ResumoFinanceiro,
) -> bytes:
    """Cria o relatório em PDF usando templates HTML modernos."""

    templates_root = Path(__file__).resolve().parents[2] / "templates"

    # Carregar CSS
    css_path = templates_root / "css" / "modern-cards.css"
    css_content = ""
    if css_path.exists():
        css_content = css_path.read_text(encoding='utf-8')

    # Carregar imagem do timbrado e converter para base64
    img_path = templates_root / "images" / "Imagem Timbrado.png"
    img_base64 = ""
    if img_path.exists():
        with open(img_path, "rb") as img_file:
            img_data = img_file.read()
            img_base64 = base64.b64encode(img_data).decode('utf-8')
            # Substituir URL relativa por data URI no CSS
            css_content = css_content.replace(
                "url('../images/Imagem Timbrado.png')",
                f"url('data:image/png;base64,{img_base64}')"
            )

    # Carregar template HTML
    template_path = templates_root / "relatorio_base.html"
    html_content = ""
    if template_path.exists():
        html_template = template_path.read_text(encoding='utf-8')
    else:
        raise FileNotFoundError(f"Template HTML não encontrado: {template_path}")

    if html_template:

        # Calcular valores necessários
        recurso_atual_anual = resumo.total_recebido * 12
        recurso_potencial_anual = recurso_atual_anual + resumo.total_diferenca_anual
        recurso_potencial_mensal = resumo.total_recebido + resumo.total_perca_mensal

        # Métricas complementares para os cards
        ratio_perda_mensal = _safe_ratio(resumo.total_perca_mensal, recurso_potencial_mensal)
        ratio_diferenca_anual = _safe_ratio(resumo.total_diferenca_anual, recurso_potencial_anual)
        ratio_recebimento_atual = _safe_ratio(resumo.total_recebido, recurso_potencial_mensal)

        def _progress_value(ratio: float) -> int:
            if ratio <= 0:
                return 0
            return max(6, min(100, int(round(ratio * 100))))

        perda_percent = int(round(ratio_perda_mensal * 100))
        diferenca_percent = int(round(ratio_diferenca_anual * 100))
        recebimento_percent = int(round(ratio_recebimento_atual * 100))

        perda_detalhe = f"Equivalente a R$ {_br_number(resumo.total_diferenca_anual, 0)} por ano"
        diferenca_detalhe = f"Impacto de {resumo.percentual_perda_anual:.1f}% do orçamento anual"
        atual_detalhe = f"Potencial com ajuste: R$ {_br_number(recurso_potencial_mensal, 0)}"

        perda_indicador = f"{perda_percent}% do potencial mensal"
        diferenca_indicador = f"{diferenca_percent}% do potencial anual"
        atual_indicador = f"Cobertura atual de {recebimento_percent}%"

        # Substituir variáveis no template
        html_content = html_template.replace('{{ municipio_nome }}', municipio_nome or 'Município')
        html_content = html_content.replace('{{ uf }}', uf or '')
        html_content = html_content.replace('{{ css_content }}', css_content)

        # Processar todas as substituições de template
        replacements = {
            '{{ "%.2f"|format(resumo.percentual_perda_anual) }}': f"{resumo.percentual_perda_anual:.2f}",
            '{{ "{:,.0f}".format(resumo.total_perca_mensal).replace(\',\', \'.\') }}': _br_number(resumo.total_perca_mensal, 0),
            '{{ "{:,.0f}".format(resumo.total_diferenca_anual).replace(\',\', \'.\') }}': _br_number(resumo.total_diferenca_anual, 0),
            '{{ "{:,.0f}".format(resumo.total_recebido).replace(\',\', \'.\') }}': _br_number(resumo.total_recebido, 0),
            '{{ "{:,.0f}".format(resumo.total_recebido * 12).replace(\',\', \'.\') }}': _br_number(recurso_atual_anual, 0),
            '{{ "{:,.0f}".format((resumo.total_recebido * 12) + resumo.total_diferenca_anual).replace(\',\', \'.\') }}': _br_number(recurso_potencial_anual, 0),
            '{{ "{:,.0f}".format(resumo.total_recebido + resumo.total_perca_mensal).replace(\',\', \'.\') }}': _br_number(recurso_potencial_mensal, 0),
            '__PERDA_BADGE__': html.escape('Oportunidade'),
            '__PERDA_DETALHE__': html.escape(perda_detalhe),
            '__PERDA_PROGRESS__': str(_progress_value(ratio_perda_mensal)),
            '__PERDA_INDICADOR__': html.escape(perda_indicador),
            '__DIFERENCA_BADGE__': html.escape('Visão anual'),
            '__DIFERENCA_DETALHE__': html.escape(diferenca_detalhe),
            '__DIFERENCA_PROGRESS__': str(_progress_value(ratio_diferenca_anual)),
            '__DIFERENCA_INDICADOR__': html.escape(diferenca_indicador),
            '__ATUAL_BADGE__': html.escape('Cenário atual'),
            '__ATUAL_DETALHE__': html.escape(atual_detalhe),
            '__ATUAL_PROGRESS__': str(_progress_value(ratio_recebimento_atual)),
            '__ATUAL_INDICADOR__': html.escape(atual_indicador),
        }

        # Aplicar todas as substituições
        for old_pattern, new_value in replacements.items():
            html_content = html_content.replace(old_pattern, new_value)

        # Substituir cálculos para gráfico de barras (porcentagem de altura)
        if recurso_potencial_anual > 0:
            bar_height_percentage = (recurso_atual_anual / recurso_potencial_anual) * 100
        else:
            bar_height_percentage = 50

        html_content = html_content.replace(
            '{{ (resumo.total_recebido * 12 / ((resumo.total_recebido * 12) + resumo.total_diferenca_anual) * 100) }}',
            f"{bar_height_percentage:.1f}"
        )

        # Substituir valor em milhões para o eixo do gráfico
        max_value_millions = recurso_potencial_anual / 1000000
        html_content = html_content.replace(
            '{{ "{:.1f}mi".format(((resumo.total_recebido * 12) + resumo.total_diferenca_anual) / 1000000) }}',
            f"{max_value_millions:.1f}mi"
        )

    # Gerar PDF com WeasyPrint
    try:
        # Verificar se o HTML foi processado corretamente
        if not html_content or len(html_content) < 1000:
            raise ValueError("HTML template não foi processado corretamente")

        # Configurar base_url para que o WeasyPrint encontre as imagens
        base_url = templates_root.as_uri() + '/'
        html_doc = weasyprint.HTML(string=html_content, base_url=base_url)
        pdf_bytes = html_doc.write_pdf()

        # Verificar se o PDF foi gerado corretamente
        if not pdf_bytes or len(pdf_bytes) < 5000:
            raise ValueError("PDF gerado está muito pequeno")

        return pdf_bytes
    except Exception as e:
        # Propagar erro para diagnóstico
        print(f"❌ Erro ao gerar PDF com HTML-to-PDF: {e}")
        import traceback
        traceback.print_exc()
        raise
