"""Serviços utilitários para geração do relatório financeiro em PDF usando HTML-to-PDF."""
from __future__ import annotations

import html
import base64
from typing import Any, Dict, Iterable, List, Optional
from pathlib import Path
import weasyprint

from fpdf import FPDF

from app.models.schemas import ResumoFinanceiro, DetalhamentoPrograma, ResumoDetalhado
from app.utils.logger import logger


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


def _mapear_programa_info(nome_programa: str) -> tuple[str, str, str]:
    """Mapeia nome do programa para (nome_curto, ícone, cor_tema)."""
    mapeamento = {
        "Equipes de Saúde da Família - eSF e equipes de Atenção Primária - eAP": ("eSF/eAP", "👥", "warning"),
        "Atenção à Saúde Bucal": ("Saúde Bucal", "🦷", "success"),
        "Equipes Multiprofissionais - eMulti": ("eMulti", "🏥", "success"),
        "Agentes Comunitários de Saúde": ("ACS", "🚶", "success"),
        "Demais programas, serviços e equipes da Atenção Primária à Saúde": ("Demais", "⚙️", "muted"),
        "Componente per capita de base populacional": ("Per Capita", "👨‍👩‍👧‍👦", "info"),
    }
    return mapeamento.get(nome_programa, (nome_programa[:20], "⚙️", "muted"))


def compute_detailed_summary(
    resumos_planos: Iterable[Dict[str, Any]]
) -> List[DetalhamentoPrograma]:
    """Processa resumos de planos orçamentários e retorna detalhamento."""
    programas = []

    for plano in resumos_planos:
        nome_completo = plano.get('dsPlanoOrcamentario', 'Sem descrição')
        valor_integral = float(plano.get('vlIntegral') or 0.0)
        valor_ajuste = float(plano.get('vlAjuste') or 0.0)
        valor_desconto = float(plano.get('vlDesconto') or 0.0)
        valor_efetivo = float(plano.get('vlEfetivoRepasse') or 0.0)

        # Calcular percentual de efetivação
        if valor_integral > 0:
            percentual_efetivacao = (valor_efetivo / valor_integral) * 100.0
        else:
            percentual_efetivacao = 0.0

        # Determinar status
        tem_desconto = valor_desconto < 0
        ativo = valor_efetivo > 0

        # Mapear informações do programa
        nome_curto, icone, cor_base = _mapear_programa_info(nome_completo)

        # Ajustar cor se houver desconto
        if tem_desconto:
            cor_tema = "warning" if percentual_efetivacao >= 50 else "danger"
        elif not ativo:
            cor_tema = "muted"
        else:
            cor_tema = cor_base

        programa = DetalhamentoPrograma(
            nome=nome_completo,
            nome_curto=nome_curto,
            valor_integral=valor_integral,
            valor_ajuste=valor_ajuste,
            valor_desconto=valor_desconto,
            valor_efetivo=valor_efetivo,
            percentual_efetivacao=percentual_efetivacao,
            tem_desconto=tem_desconto,
            ativo=ativo,
            icone=icone,
            cor_tema=cor_tema
        )
        programas.append(programa)

    return programas


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


def _get_badge_text(programa: DetalhamentoPrograma) -> str:
    """Retorna o texto do badge baseado no status do programa."""
    if not programa.ativo:
        return "❌ Sem credenciamento"
    elif programa.tem_desconto:
        return "⚠️ Desconto aplicado"
    elif programa.percentual_efetivacao >= 100:
        return "✓ 100% recebido"
    else:
        return "✓ Ativo"


def _generate_program_cards_html(programas: List[DetalhamentoPrograma]) -> str:
    """Gera HTML dos cards de programas."""
    cards_html = []

    for programa in programas:
        badge_text = _get_badge_text(programa)

        # Montar linhas de valores
        value_rows = []
        value_rows.append(f'''
            <div class="value-row">
                <span class="value-label">Integral:</span>
                <span class="value-amount">R$ {_br_number(programa.valor_integral, 0)}</span>
            </div>
        ''')

        if programa.tem_desconto:
            value_rows.append(f'''
                <div class="value-row discount">
                    <span class="value-label">Desconto:</span>
                    <span class="value-amount">R$ {_br_number(programa.valor_desconto, 0)}</span>
                </div>
            ''')

        value_rows.append(f'''
            <div class="value-row total">
                <span class="value-label">Efetivo:</span>
                <span class="value-amount">R$ {_br_number(programa.valor_efetivo, 0)}</span>
            </div>
        ''')

        card_html = f'''
            <div class="program-card {programa.cor_tema}">
                <div class="program-badge">{html.escape(badge_text)}</div>
                <div class="program-header">
                    <div class="program-icon">{programa.icone}</div>
                    <h3 class="program-title">{html.escape(programa.nome_curto)}</h3>
                </div>
                <div class="program-values">
                    {''.join(value_rows)}
                </div>
                <div class="program-progress">
                    <div class="program-progress-bar">
                        <div class="program-progress-fill" style="width: {programa.percentual_efetivacao:.1f}%"></div>
                    </div>
                    <div class="program-progress-label">{programa.percentual_efetivacao:.1f}% do integral</div>
                </div>
            </div>
        '''
        cards_html.append(card_html)

    return '\n'.join(cards_html)


def _generate_composition_bars_html(programas: List[DetalhamentoPrograma]) -> str:
    """Gera HTML das barras de composição."""
    # Calcular total
    total_efetivo = sum(p.valor_efetivo for p in programas if p.ativo)

    if total_efetivo == 0:
        return '<p>Sem dados para composição</p>'

    bars_html = []
    color_index = 1

    for programa in programas:
        if programa.ativo and programa.valor_efetivo > 0:
            percentual = (programa.valor_efetivo / total_efetivo) * 100

            bar_html = f'''
                <div class="composition-bar-row">
                    <div class="composition-bar-label">{html.escape(programa.nome_curto)}</div>
                    <div class="composition-bar-track">
                        <div class="composition-bar-fill color-{color_index}" style="width: {percentual:.1f}%">
                            {percentual:.1f}%
                        </div>
                    </div>
                    <div class="composition-bar-value">R$ {_br_number(programa.valor_efetivo, 0)}</div>
                </div>
            '''
            bars_html.append(bar_html)
            color_index = (color_index % 6) + 1

    # Adicionar linha de total
    bars_html.append(f'''
        <div class="composition-bar-row" style="margin-top: 10px; padding-top: 10px; border-top: 2px solid #e5e7eb;">
            <div class="composition-bar-label" style="font-weight: 900;">TOTAL</div>
            <div class="composition-bar-track"></div>
            <div class="composition-bar-value" style="font-size: 14px; color: #1A1A1A;">R$ {_br_number(total_efetivo, 0)}</div>
        </div>
    ''')

    return '\n'.join(bars_html)


def _generate_discount_analysis_html(programas: List[DetalhamentoPrograma]) -> str:
    """Gera HTML da análise de descontos se houver programas com desconto."""
    programas_com_desconto = [p for p in programas if p.tem_desconto]

    if not programas_com_desconto:
        return ''

    # Somar todos os descontos
    total_desconto = sum(abs(p.valor_desconto) for p in programas_com_desconto)
    total_desconto_anual = total_desconto * 12

    # Listar programas com desconto
    lista_programas = ', '.join([p.nome_curto for p in programas_com_desconto])

    analysis_html = f'''
        <div class="discount-analysis-box">
            <div class="discount-analysis-title">
                ⚠️ Análise de Descontos Identificados
            </div>
            <div class="discount-analysis-content">
                <p>
                    O(s) programa(s) <strong>{html.escape(lista_programas)}</strong> apresenta(m) desconto(s) aplicado(s).
                </p>
                <div class="discount-highlight">
                    Valor total perdido: R$ {_br_number(total_desconto, 0)}/mês = R$ {_br_number(total_desconto_anual, 0)}/ano
                </div>
                <div class="discount-suggestion">
                    💡 Oportunidade: Este valor pode ser recuperado através da melhoria de indicadores e regularização cadastral das equipes.
                </div>
            </div>
        </div>
    '''

    return analysis_html


def create_pdf_report(
    *,
    municipio_nome: Optional[str],
    uf: Optional[str],
    competencia: str,
    resumo: ResumoFinanceiro,
    resumos_planos: Optional[List[Dict[str, Any]]] = None,
) -> bytes:
    """Cria o relatório em PDF usando templates HTML modernos."""
    return create_html_pdf_report(
        municipio_nome=municipio_nome,
        uf=uf,
        competencia=competencia,
        resumo=resumo,
        resumos_planos=resumos_planos
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
    resumos_planos: Optional[List[Dict[str, Any]]] = None,
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

        # Processar Página 4: Detalhamento por Programa
        if resumos_planos:
            programas = compute_detailed_summary(resumos_planos)

            # Extrair competências dos dados
            comp_cnes = resumos_planos[0].get('nuCompCnes', competencia) if resumos_planos else competencia
            parcela_pgto = resumos_planos[0].get('nuParcela', competencia) if resumos_planos else competencia

            # Substituir competências
            html_content = html_content.replace('__COMPETENCIA_CNES__', str(comp_cnes))
            html_content = html_content.replace('__PARCELA_PGTO__', str(parcela_pgto))

            # Gerar HTML dos cards de programas
            program_cards_html = _generate_program_cards_html(programas)
            html_content = html_content.replace('__PROGRAM_CARDS__', program_cards_html)

            # Gerar HTML das barras de composição
            composition_bars_html = _generate_composition_bars_html(programas)
            html_content = html_content.replace('__COMPOSITION_BARS__', composition_bars_html)

            # Gerar HTML da análise de descontos (se houver)
            discount_analysis_html = _generate_discount_analysis_html(programas)
            html_content = html_content.replace('__DISCOUNT_ANALYSIS__', discount_analysis_html)
        else:
            # Se não houver dados de programas, remover placeholders
            html_content = html_content.replace('__COMPETENCIA_CNES__', competencia)
            html_content = html_content.replace('__PARCELA_PGTO__', competencia)
            html_content = html_content.replace('__PROGRAM_CARDS__', '<p>Dados não disponíveis</p>')
            html_content = html_content.replace('__COMPOSITION_BARS__', '')
            html_content = html_content.replace('__DISCOUNT_ANALYSIS__', '')

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


def _processar_saude_familia_detalhado(pagamentos: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Processa dados detalhados de Saúde da Família (eSF e eAP) a partir dos pagamentos."""
    if not pagamentos or len(pagamentos) == 0:
        return None

    try:
        pagamento = pagamentos[0]  # Pegar primeiro pagamento
    except (IndexError, TypeError):
        return None

    if not isinstance(pagamento, dict):
        return None

    esf = {
        'equipes': {
            'credenciadas': pagamento.get('qtEsfCredenciado', 0) or 0,
            'homologadas': pagamento.get('qtEsfHomologado', 0) or 0,
            'total_pgto': pagamento.get('qtEsfTotalPgto', 0) or 0,
        },
        'pagamento_percentual': {
            'pc100': pagamento.get('qtEsf100pcPgto', 0) or 0,
            'pc75': pagamento.get('qtEsf75pcPgto', 0) or 0,
            'pc50': pagamento.get('qtEsf50pcPgto', 0) or 0,
            'pc25': pagamento.get('qtEsf25pcPgto', 0) or 0,
        },
        'valores': {
            'fixo': float(pagamento.get('vlFixoEsf', 0) or 0),
            'vinculo': float(pagamento.get('vlVinculoEsf', 0) or 0),
            'qualidade': float(pagamento.get('vlQualidadeEsf', 0) or 0),
            'total': float(pagamento.get('vlTotalEsf', 0) or 0),
            'implantacao': float(pagamento.get('vlPagamentoImplantacaoEsf', 0) or 0),
        },
        'classificacoes': {
            'equidade': pagamento.get('dsFaixaIndiceEquidadeEsfEap', 'Não informado'),
            'vinculo': pagamento.get('dsClassificacaoVinculoEsfEap', 'Não informado'),
            'qualidade': pagamento.get('dsClassificacaoQualidadeEsfEap', 'Não informado'),
        }
    }

    eap = {
        'equipes': {
            'credenciadas': pagamento.get('qtEapCredenciadas', 0) or 0,
            'homologadas': pagamento.get('qtEapHomologado', 0) or 0,
            'total_pgto': pagamento.get('qtEapTotalPgto', 0) or 0,
        },
        'carga_horaria': {
            'ch20_completas': pagamento.get('qtEap20hCompletas', 0) or 0,
            'ch20_incompletas': pagamento.get('qtEap20hIncompletas', 0) or 0,
            'ch30_completas': pagamento.get('qtEap30hCompletas', 0) or 0,
            'ch30_incompletas': pagamento.get('qtEap30hIncompletas', 0) or 0,
        },
        'valores': {
            'fixo': float(pagamento.get('vlFixoEap', 0) or 0),
            'vinculo': float(pagamento.get('vlVinculoEap', 0) or 0),
            'qualidade': float(pagamento.get('vlQualidadeEap', 0) or 0),
            'total': float(pagamento.get('vlTotalEap', 0) or 0),
            'implantacao': float(pagamento.get('vlPagamentoImplantacaoEap', 0) or 0),
        }
    }

    vl_total = esf['valores']['total'] + eap['valores']['total']
    qt_total_equipes = esf['equipes']['credenciadas'] + eap['equipes']['credenciadas']

    return {
        'esf': esf,
        'eap': eap,
        'totais': {
            'vlTotal': vl_total,
            'qtTotalEquipes': qt_total_equipes
        }
    }


def _gerar_html_saude_familia_detalhado(dados: Optional[Dict[str, Any]]) -> str:
    """Gera HTML para seção de Saúde da Família (eSF e eAP) detalhada."""
    if not dados:
        return '''
        <div class="detail-section" style="background: #fef3c7; border-left-color: #f59e0b;">
            <p style="color: #92400e; margin: 0;">
                ⚠️ Nenhum dado de Saúde da Família (eSF/eAP) disponível para esta competência.
                Isso pode ocorrer se o município não possui equipes cadastradas ou se os dados
                ainda não foram processados pelo Ministério da Saúde.
            </p>
        </div>
        '''

    esf = dados.get('esf', {})
    eap = dados.get('eap', {})
    totais = dados.get('totais', {})

    # Escapar classificações antes de usar nas f-strings
    equidade = html.escape(str(esf.get('classificacoes', {}).get('equidade', 'N/A')))
    vinculo = html.escape(str(esf.get('classificacoes', {}).get('vinculo', 'N/A')))
    qualidade = html.escape(str(esf.get('classificacoes', {}).get('qualidade', 'N/A')))

    resultado_html = f'''
    <div class="detail-section">
        <h3 style="color: #f59e0b; margin-top: 0;">eSF - Equipes de Saúde da Família</h3>

        <div class="subsection-title">Equipes</div>
        <div class="detail-grid">
            <div class="detail-item">
                <span class="detail-label">Credenciadas</span>
                <span class="detail-value">{esf.get('equipes', {}).get('credenciadas', 0)}</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Homologadas</span>
                <span class="detail-value">{esf.get('equipes', {}).get('homologadas', 0)}</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Total com Pagamento</span>
                <span class="detail-value">{esf.get('equipes', {}).get('total_pgto', 0)}</span>
            </div>
        </div>

        <div class="subsection-title">Pagamento por Percentual</div>
        <div class="detail-grid">
            <div class="detail-item">
                <span class="detail-label">100% do Valor</span>
                <span class="detail-value">{esf.get('pagamento_percentual', {}).get('pc100', 0)}</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">75% do Valor</span>
                <span class="detail-value">{esf.get('pagamento_percentual', {}).get('pc75', 0)}</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">50% do Valor</span>
                <span class="detail-value">{esf.get('pagamento_percentual', {}).get('pc50', 0)}</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">25% do Valor</span>
                <span class="detail-value">{esf.get('pagamento_percentual', {}).get('pc25', 0)}</span>
            </div>
        </div>

        <div class="subsection-title">Classificações</div>
        <div class="detail-grid">
            <div class="detail-item">
                <span class="detail-label">Índice de Equidade</span>
                <span class="detail-value">{equidade}</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Classificação Vínculo</span>
                <span class="detail-value">{vinculo}</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Classificação Qualidade</span>
                <span class="detail-value">{qualidade}</span>
            </div>
        </div>

        <div class="subsection-title">Valores Financeiros eSF</div>
        <table class="valores-table">
            <thead>
                <tr>
                    <th>Componente</th>
                    <th style="text-align: right;">Valor</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Valor Fixo</td>
                    <td style="text-align: right;">R$ {_br_number(esf.get('valores', {}).get('fixo', 0), 2)}</td>
                </tr>
                <tr>
                    <td>Valor Vínculo</td>
                    <td style="text-align: right;">R$ {_br_number(esf.get('valores', {}).get('vinculo', 0), 2)}</td>
                </tr>
                <tr>
                    <td>Valor Qualidade</td>
                    <td style="text-align: right;">R$ {_br_number(esf.get('valores', {}).get('qualidade', 0), 2)}</td>
                </tr>
                <tr>
                    <td>Implantação</td>
                    <td style="text-align: right;">R$ {_br_number(esf.get('valores', {}).get('implantacao', 0), 2)}</td>
                </tr>
                <tr style="font-weight: 600; background: #f3f4f6;">
                    <td>Total eSF</td>
                    <td style="text-align: right;">R$ {_br_number(esf.get('valores', {}).get('total', 0), 2)}</td>
                </tr>
            </tbody>
        </table>
    </div>
    '''

    # Seção eAP
    if eap.get('equipes', {}).get('credenciadas', 0) > 0:
        resultado_html += f'''
        <div class="detail-section" style="border-left-color: #fb923c;">
            <h3 style="color: #fb923c; margin-top: 0;">eAP - Equipes de Atenção Primária</h3>

            <div class="subsection-title">Equipes</div>
            <div class="detail-grid">
                <div class="detail-item">
                    <span class="detail-label">Credenciadas</span>
                    <span class="detail-value">{eap.get('equipes', {}).get('credenciadas', 0)}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Homologadas</span>
                    <span class="detail-value">{eap.get('equipes', {}).get('homologadas', 0)}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Total com Pagamento</span>
                    <span class="detail-value">{eap.get('equipes', {}).get('total_pgto', 0)}</span>
                </div>
            </div>

            <div class="subsection-title">Carga Horária</div>
            <div class="detail-grid">
                <div class="detail-item">
                    <span class="detail-label">20h Completas</span>
                    <span class="detail-value">{eap.get('carga_horaria', {}).get('ch20_completas', 0)}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">20h Incompletas</span>
                    <span class="detail-value">{eap.get('carga_horaria', {}).get('ch20_incompletas', 0)}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">30h Completas</span>
                    <span class="detail-value">{eap.get('carga_horaria', {}).get('ch30_completas', 0)}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">30h Incompletas</span>
                    <span class="detail-value">{eap.get('carga_horaria', {}).get('ch30_incompletas', 0)}</span>
                </div>
            </div>

            <div class="subsection-title">Valores Financeiros eAP</div>
            <table class="valores-table">
                <thead>
                    <tr>
                        <th>Componente</th>
                        <th style="text-align: right;">Valor</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Valor Fixo</td>
                        <td style="text-align: right;">R$ {_br_number(eap.get('valores', {}).get('fixo', 0), 2)}</td>
                    </tr>
                    <tr>
                        <td>Valor Vínculo</td>
                        <td style="text-align: right;">R$ {_br_number(eap.get('valores', {}).get('vinculo', 0), 2)}</td>
                    </tr>
                    <tr>
                        <td>Valor Qualidade</td>
                        <td style="text-align: right;">R$ {_br_number(eap.get('valores', {}).get('qualidade', 0), 2)}</td>
                    </tr>
                    <tr>
                        <td>Implantação</td>
                        <td style="text-align: right;">R$ {_br_number(eap.get('valores', {}).get('implantacao', 0), 2)}</td>
                    </tr>
                    <tr style="font-weight: 600; background: #f3f4f6;">
                        <td>Total eAP</td>
                        <td style="text-align: right;">R$ {_br_number(eap.get('valores', {}).get('total', 0), 2)}</td>
                    </tr>
                </tbody>
            </table>
        </div>
        '''

    # Totais
    resultado_html += f'''
    <div class="highlight-box">
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
            <div>
                <p style="margin: 0; font-size: 12px; color: #6b7280;">Total de Equipes (eSF + eAP)</p>
                <div class="value" style="font-size: 32px; color: #f59e0b;">{totais.get('qtTotalEquipes', 0)}</div>
            </div>
            <div>
                <p style="margin: 0; font-size: 12px; color: #6b7280;">Valor Total eSF + eAP</p>
                <div class="value" style="font-size: 28px;">R$ {_br_number(totais.get('vlTotal', 0), 2)}</div>
            </div>
        </div>
    </div>
    '''

    return resultado_html


def _processar_saude_bucal_detalhado(pagamentos: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Processa dados detalhados de Saúde Bucal a partir dos pagamentos."""
    if not pagamentos or len(pagamentos) == 0:
        return None

    try:
        pagamento = pagamentos[0]  # Pegar primeiro pagamento
    except (IndexError, TypeError):
        return None

    if not isinstance(pagamento, dict):
        return None

    esb = {
        'modalidade40h': {
            'credenciadas': pagamento.get('qtSb40hCredenciada', 0) or 0,
            'homologadas': pagamento.get('qtSb40hHomologado', 0) or 0,
            'modalidadeI': pagamento.get('qtSbPagamentoModalidadeI', 0) or 0,
            'modalidadeII': pagamento.get('qtSbPagamentoModalidadeII', 0) or 0,
        },
        'chDiferenciada': {
            'credenciadas': pagamento.get('qtSb40hDifCredenciada', 0) or 0,
            'homologadas': pagamento.get('qtSbChDifHomologado', 0) or 0,
            'modalidade20h': pagamento.get('qtSbPagamentoDifModalidade20Horas', 0) or 0,
            'modalidade30h': pagamento.get('qtSbPagamentoDifModalidade30Horas', 0) or 0,
        },
        'quilombolasAssentamentos': {
            'modalidadeI': pagamento.get('qtSbEqpQuilombAssentModalI', 0) or 0,
            'modalidadeII': pagamento.get('qtSbEqpQuilombAssentModalII', 0) or 0,
        },
        'implantacao': pagamento.get('qtSbEquipeImplantacao', 0) or 0,
        'valores': {
            'pagamento': float(pagamento.get('vlPagamentoEsb40h', 0) or 0),
            'qualidade': float(pagamento.get('vlPagamentoEsb40hQualidade', 0) or 0),
            'chDiferenciada': float(pagamento.get('vlPagamentoEsbChDiferenciada', 0) or 0),
            'implantacao': float(pagamento.get('vlPagamentoImplantacaoEsb40h', 0) or 0),
        }
    }

    uom = {
        'credenciadas': pagamento.get('qtUomCredenciada', 0) or 0,
        'homologadas': pagamento.get('qtUomHomologado', 0) or 0,
        'pagas': pagamento.get('qtUomPgto', 0) or 0,
        'valores': {
            'pagamento': float(pagamento.get('vlPagamentoUom', 0) or 0),
            'implantacao': float(pagamento.get('vlPagamentoUomImplantacao', 0) or 0),
        }
    }

    ceo = {
        'municipal': float(pagamento.get('vlPagamentoCeoMunicipal', 0) or 0),
        'estadual': float(pagamento.get('vlPagamentoCeoEstadual', 0) or 0),
    }

    lrpd = {
        'municipal': float(pagamento.get('vlPagamentoLrpdMunicipal', 0) or 0),
        'estadual': float(pagamento.get('vlPagamentoLrpdEstadual', 0) or 0),
    }

    vl_total = (
        esb['valores']['pagamento'] +
        esb['valores']['qualidade'] +
        esb['valores']['chDiferenciada'] +
        esb['valores']['implantacao'] +
        uom['valores']['pagamento'] +
        uom['valores']['implantacao'] +
        ceo['municipal'] +
        ceo['estadual'] +
        lrpd['municipal'] +
        lrpd['estadual']
    )

    qt_total_equipes = (
        esb['modalidade40h']['credenciadas'] +
        esb['chDiferenciada']['credenciadas'] +
        esb['quilombolasAssentamentos']['modalidadeI'] +
        esb['quilombolasAssentamentos']['modalidadeII'] +
        uom['credenciadas']
    )

    return {
        'esb': esb,
        'uom': uom,
        'ceo': ceo,
        'lrpd': lrpd,
        'totais': {
            'vlTotal': vl_total,
            'qtTotalEquipes': qt_total_equipes
        }
    }


def _gerar_html_saude_bucal_detalhado(dados: Optional[Dict[str, Any]]) -> str:
    """Gera HTML para seção de Saúde Bucal detalhada."""
    if not dados:
        return '''
        <div class="detail-section" style="background: #dbeafe; border-left-color: #0ea5e9;">
            <p style="color: #075985; margin: 0;">
                ⚠️ Nenhum dado de Saúde Bucal disponível para esta competência.
                Isso pode ocorrer se o município não possui Equipes de Saúde Bucal (ESB),
                Unidades Odontológicas Móveis (UOM), CEO ou LRPD cadastrados.
            </p>
        </div>
        '''

    esb = dados.get('esb', {})
    uom = dados.get('uom', {})
    ceo = dados.get('ceo', {})
    lrpd = dados.get('lrpd', {})
    totais = dados.get('totais', {})

    resultado_html = f'''
    <div class="detail-section">
        <h3 style="color: #0ea5e9; margin-top: 0;">ESB - Equipes de Saúde Bucal</h3>

        <div class="subsection-title">Modalidade 40h</div>
        <div class="detail-grid">
            <div class="detail-item">
                <span class="detail-label">Credenciadas</span>
                <span class="detail-value">{esb.get('modalidade40h', {}).get('credenciadas', 0)}</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Homologadas</span>
                <span class="detail-value">{esb.get('modalidade40h', {}).get('homologadas', 0)}</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Modalidade I</span>
                <span class="detail-value">{esb.get('modalidade40h', {}).get('modalidadeI', 0)}</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Modalidade II</span>
                <span class="detail-value">{esb.get('modalidade40h', {}).get('modalidadeII', 0)}</span>
            </div>
        </div>

        <div class="subsection-title">Carga Horária Diferenciada</div>
        <div class="detail-grid">
            <div class="detail-item">
                <span class="detail-label">Credenciadas</span>
                <span class="detail-value">{esb.get('chDiferenciada', {}).get('credenciadas', 0)}</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Homologadas</span>
                <span class="detail-value">{esb.get('chDiferenciada', {}).get('homologadas', 0)}</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">20 horas</span>
                <span class="detail-value">{esb.get('chDiferenciada', {}).get('modalidade20h', 0)}</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">30 horas</span>
                <span class="detail-value">{esb.get('chDiferenciada', {}).get('modalidade30h', 0)}</span>
            </div>
        </div>

        <div class="subsection-title">Valores Financeiros ESB</div>
        <table class="valores-table">
            <thead>
                <tr>
                    <th>Componente</th>
                    <th style="text-align: right;">Valor</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Pagamento ESB 40h</td>
                    <td style="text-align: right;">R$ {_br_number(esb.get('valores', {}).get('pagamento', 0), 2)}</td>
                </tr>
                <tr>
                    <td>Qualidade</td>
                    <td style="text-align: right;">R$ {_br_number(esb.get('valores', {}).get('qualidade', 0), 2)}</td>
                </tr>
                <tr>
                    <td>CH Diferenciada</td>
                    <td style="text-align: right;">R$ {_br_number(esb.get('valores', {}).get('chDiferenciada', 0), 2)}</td>
                </tr>
                <tr>
                    <td>Implantação</td>
                    <td style="text-align: right;">R$ {_br_number(esb.get('valores', {}).get('implantacao', 0), 2)}</td>
                </tr>
            </tbody>
        </table>
    </div>
    '''

    # UOM
    if uom.get('credenciadas', 0) > 0:
        resultado_html += f'''
        <div class="detail-section" style="border-left-color: #8b5cf6;">
            <h3 style="color: #8b5cf6; margin-top: 0;">UOM - Unidade Odontológica Móvel</h3>
            <div class="detail-grid">
                <div class="detail-item">
                    <span class="detail-label">Credenciadas</span>
                    <span class="detail-value">{uom.get('credenciadas', 0)}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Homologadas</span>
                    <span class="detail-value">{uom.get('homologadas', 0)}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Pagas</span>
                    <span class="detail-value">{uom.get('pagas', 0)}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Valor Pagamento</span>
                    <span class="detail-value">R$ {_br_number(uom.get('valores', {}).get('pagamento', 0), 2)}</span>
                </div>
            </div>
        </div>
        '''

    # CEO
    if ceo.get('municipal', 0) > 0 or ceo.get('estadual', 0) > 0:
        resultado_html += f'''
        <div class="detail-section" style="border-left-color: #3b82f6;">
            <h3 style="color: #3b82f6; margin-top: 0;">CEO - Centro de Especialidades Odontológicas</h3>
            <div class="detail-grid">
                <div class="detail-item">
                    <span class="detail-label">CEO Municipal</span>
                    <span class="detail-value">R$ {_br_number(ceo.get('municipal', 0), 2)}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">CEO Estadual</span>
                    <span class="detail-value">R$ {_br_number(ceo.get('estadual', 0), 2)}</span>
                </div>
            </div>
        </div>
        '''

    # LRPD
    if lrpd.get('municipal', 0) > 0 or lrpd.get('estadual', 0) > 0:
        resultado_html += f'''
        <div class="detail-section" style="border-left-color: #10b981;">
            <h3 style="color: #10b981; margin-top: 0;">LRPD - Laboratório Regional de Prótese Dentária</h3>
            <div class="detail-grid">
                <div class="detail-item">
                    <span class="detail-label">LRPD Municipal</span>
                    <span class="detail-value">R$ {_br_number(lrpd.get('municipal', 0), 2)}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">LRPD Estadual</span>
                    <span class="detail-value">R$ {_br_number(lrpd.get('estadual', 0), 2)}</span>
                </div>
            </div>
        </div>
        '''

    # Totais
    resultado_html += f'''
    <div class="highlight-box">
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
            <div>
                <p style="margin: 0; font-size: 12px; color: #6b7280;">Total de Equipes</p>
                <div class="value" style="font-size: 32px; color: #0ea5e9;">{totais.get('qtTotalEquipes', 0)}</div>
            </div>
            <div>
                <p style="margin: 0; font-size: 12px; color: #6b7280;">Valor Total Saúde Bucal</p>
                <div class="value" style="font-size: 28px;">R$ {_br_number(totais.get('vlTotal', 0), 2)}</div>
            </div>
        </div>
    </div>
    '''

    return resultado_html


def _processar_emulti_detalhado(pagamentos: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Processa dados detalhados de eMulti a partir dos pagamentos."""
    if not pagamentos or len(pagamentos) == 0:
        return None

    try:
        pagamento = pagamentos[0]  # Pegar primeiro pagamento
    except (IndexError, TypeError):
        return None

    if not isinstance(pagamento, dict):
        return None

    emulti = {
        'equipes': {
            'credenciadas': pagamento.get('qtEmultiCredenciadas', 0) or 0,
            'homologadas': pagamento.get('qtEmultiHomologado', 0) or 0,
            'pagas': pagamento.get('qtEmultiPagas', 0) or 0,
        },
        'tipos': {
            'ampliada': pagamento.get('qtEmultiPagamentoAmpliada', 0) or 0,
            'intermunicipal': pagamento.get('qtEmultiPagamentoIntermunicipal', 0) or 0,
            'complementar': pagamento.get('qtEmultiPagamentoComplementar', 0) or 0,
            'estrategica': pagamento.get('qtEmultiPagamentoEstrategica', 0) or 0,
        },
        'atend_remoto': {
            'equipes': pagamento.get('qtEmultiPagasAtendRemoto', 0) or 0,
            'valor': float(pagamento.get('vlPagamentoEmultiAtendimentoRemoto', 0) or 0),
        },
        'valores': {
            'custeio': float(pagamento.get('vlPagamentoEmultiCusteio', 0) or 0),
            'qualidade': float(pagamento.get('vlPagamentoEmultiQualidade', 0) or 0),
            'atend_remoto': float(pagamento.get('vlPagamentoEmultiAtendimentoRemoto', 0) or 0),
            'implantacao': float(pagamento.get('vlPagamentoEmultiImplantacao', 0) or 0),
            'total': float(pagamento.get('vlTotalEmulti', 0) or 0),
        },
        'classificacao_qualidade': pagamento.get('dsClassificacaoQualidadeEmulti', 'Não informado'),
    }

    return {
        'emulti': emulti,
        'totais': {
            'vlTotal': emulti['valores']['total'],
            'qtTotalEquipes': emulti['equipes']['credenciadas']
        }
    }


def _gerar_html_emulti_detalhado(dados: Optional[Dict[str, Any]]) -> str:
    """Gera HTML para seção de eMulti detalhada."""
    if not dados:
        return '''
        <div class="detail-section" style="background: #d1fae5; border-left-color: #22c55e;">
            <p style="color: #065f46; margin: 0;">
                ⚠️ Nenhum dado de Equipes Multiprofissionais (eMulti) disponível para esta competência.
                Isso pode ocorrer se o município não possui equipes multiprofissionais cadastradas
                ou se os dados ainda não foram processados.
            </p>
        </div>
        '''

    emulti = dados.get('emulti', {})
    totais = dados.get('totais', {})

    # Escapar classificação de qualidade antes de usar na f-string
    classificacao_qualidade = html.escape(str(emulti.get('classificacao_qualidade', 'N/A')))

    resultado_html = f'''
    <div class="detail-section">
        <h3 style="color: #22c55e; margin-top: 0;">eMulti - Equipes Multiprofissionais</h3>

        <div class="subsection-title">Equipes</div>
        <div class="detail-grid">
            <div class="detail-item">
                <span class="detail-label">Credenciadas</span>
                <span class="detail-value">{emulti.get('equipes', {}).get('credenciadas', 0)}</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Homologadas</span>
                <span class="detail-value">{emulti.get('equipes', {}).get('homologadas', 0)}</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Pagas</span>
                <span class="detail-value">{emulti.get('equipes', {}).get('pagas', 0)}</span>
            </div>
        </div>

        <div class="subsection-title">Tipos de Equipes eMulti</div>
        <div class="detail-grid">
            <div class="detail-item">
                <span class="detail-label">Ampliada</span>
                <span class="detail-value">{emulti.get('tipos', {}).get('ampliada', 0)}</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Intermunicipal</span>
                <span class="detail-value">{emulti.get('tipos', {}).get('intermunicipal', 0)}</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Complementar</span>
                <span class="detail-value">{emulti.get('tipos', {}).get('complementar', 0)}</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Estratégica</span>
                <span class="detail-value">{emulti.get('tipos', {}).get('estrategica', 0)}</span>
            </div>
        </div>

        <div class="subsection-title">Atendimento Remoto</div>
        <div class="detail-grid">
            <div class="detail-item">
                <span class="detail-label">Equipes com Atendimento Remoto</span>
                <span class="detail-value">{emulti.get('atend_remoto', {}).get('equipes', 0)}</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Valor Atendimento Remoto</span>
                <span class="detail-value">R$ {_br_number(emulti.get('atend_remoto', {}).get('valor', 0), 2)}</span>
            </div>
        </div>

        <div class="subsection-title">Classificação</div>
        <div class="detail-grid">
            <div class="detail-item">
                <span class="detail-label">Classificação de Qualidade</span>
                <span class="detail-value">{classificacao_qualidade}</span>
            </div>
        </div>

        <div class="subsection-title">Valores Financeiros eMulti</div>
        <table class="valores-table">
            <thead>
                <tr>
                    <th>Componente</th>
                    <th style="text-align: right;">Valor</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Custeio</td>
                    <td style="text-align: right;">R$ {_br_number(emulti.get('valores', {}).get('custeio', 0), 2)}</td>
                </tr>
                <tr>
                    <td>Qualidade</td>
                    <td style="text-align: right;">R$ {_br_number(emulti.get('valores', {}).get('qualidade', 0), 2)}</td>
                </tr>
                <tr>
                    <td>Atendimento Remoto</td>
                    <td style="text-align: right;">R$ {_br_number(emulti.get('valores', {}).get('atend_remoto', 0), 2)}</td>
                </tr>
                <tr>
                    <td>Implantação</td>
                    <td style="text-align: right;">R$ {_br_number(emulti.get('valores', {}).get('implantacao', 0), 2)}</td>
                </tr>
                <tr style="font-weight: 600; background: #f3f4f6;">
                    <td>Total eMulti</td>
                    <td style="text-align: right;">R$ {_br_number(emulti.get('valores', {}).get('total', 0), 2)}</td>
                </tr>
            </tbody>
        </table>
    </div>
    '''

    # Totais
    resultado_html += f'''
    <div class="highlight-box" style="background: #ecfdf5; border-color: #22c55e;">
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
            <div>
                <p style="margin: 0; font-size: 12px; color: #6b7280;">Total de Equipes eMulti</p>
                <div class="value" style="font-size: 32px; color: #22c55e;">{totais.get('qtTotalEquipes', 0)}</div>
            </div>
            <div>
                <p style="margin: 0; font-size: 12px; color: #6b7280;">Valor Total eMulti</p>
                <div class="value" style="font-size: 28px; color: #22c55e;">R$ {_br_number(totais.get('vlTotal', 0), 2)}</div>
            </div>
        </div>
    </div>
    '''

    return resultado_html


def create_detailed_pdf_report(
    *,
    municipio_nome: Optional[str],
    uf: Optional[str],
    competencia: str,
    resumo: ResumoFinanceiro,
    pagamentos: Optional[List[Dict[str, Any]]] = None,
) -> bytes:
    """Cria relatório PDF detalhado com separação por temas e detalhamento de Saúde Bucal."""

    templates_root = Path(__file__).resolve().parents[2] / "templates"

    # Carregar CSS
    css_path = templates_root / "css" / "modern-cards.css"
    css_content = ""
    if css_path.exists():
        css_content = css_path.read_text(encoding='utf-8')

    # Carregar imagem do timbrado e converter para base64
    img_path = templates_root / "images" / "Imagem Timbrado.png"
    if img_path.exists():
        with open(img_path, "rb") as img_file:
            img_data = img_file.read()
            img_base64 = base64.b64encode(img_data).decode('utf-8')
            css_content = css_content.replace(
                "url('../images/Imagem Timbrado.png')",
                f"url('data:image/png;base64,{img_base64}')"
            )

    # Carregar template HTML detalhado
    template_path = templates_root / "relatorio_detalhado.html"
    if not template_path.exists():
        raise FileNotFoundError(f"Template HTML detalhado não encontrado: {template_path}")

    html_template = template_path.read_text(encoding='utf-8')

    # Validar e garantir que pagamentos seja uma lista válida
    pagamentos_validos = pagamentos if pagamentos and isinstance(pagamentos, list) and len(pagamentos) > 0 else []

    if not pagamentos_validos:
        logger.warning(
            f"Nenhum dado de pagamento disponível para relatório detalhado - "
            f"Município: {municipio_nome}/{uf}, Competência: {competencia}"
        )
    else:
        logger.info(
            f"Gerando relatório detalhado - Município: {municipio_nome}/{uf}, "
            f"Competência: {competencia}, Pagamentos: {len(pagamentos_validos)}"
        )

    # Processar dados detalhados de Saúde Bucal
    saude_bucal_dados = _processar_saude_bucal_detalhado(pagamentos_validos)
    saude_bucal_html = _gerar_html_saude_bucal_detalhado(saude_bucal_dados)
    if not saude_bucal_dados:
        logger.debug("Nenhum dado de Saúde Bucal processado")

    # Processar dados detalhados de Saúde da Família (eSF/eAP)
    saude_familia_dados = _processar_saude_familia_detalhado(pagamentos_validos)
    saude_familia_html = _gerar_html_saude_familia_detalhado(saude_familia_dados)
    if not saude_familia_dados:
        logger.debug("Nenhum dado de Saúde da Família processado")

    # Processar dados detalhados de eMulti
    emulti_dados = _processar_emulti_detalhado(pagamentos_validos)
    emulti_html = _gerar_html_emulti_detalhado(emulti_dados)
    if not emulti_dados:
        logger.debug("Nenhum dado de eMulti processado")

    # Substituir variáveis básicas
    html_content = html_template.replace('{{ municipio_nome }}', municipio_nome or 'Município')
    html_content = html_content.replace('{{ uf }}', uf or '')
    html_content = html_content.replace('{{ css_content }}', css_content)

    # Substituir competências
    if pagamentos and len(pagamentos) > 0:
        comp_cnes = pagamentos[0].get('nuCompCnes', competencia)
        parcela_pgto = pagamentos[0].get('nuParcela', competencia)
    else:
        comp_cnes = competencia
        parcela_pgto = competencia

    html_content = html_content.replace('__COMPETENCIA_CNES__', str(comp_cnes))
    html_content = html_content.replace('__PARCELA_PGTO__', str(parcela_pgto))

    # Substituir conteúdos das seções
    html_content = html_content.replace('__SAUDE_FAMILIA_CONTENT__', saude_familia_html)
    html_content = html_content.replace('__SAUDE_BUCAL_CONTENT__', saude_bucal_html)
    html_content = html_content.replace('__EMULTI_CONTENT__', emulti_html)

    # Substituir valores do resumo financeiro
    replacements = {
        '{{ "{:,.0f}".format(resumo.total_recebido).replace(\',\', \'.\') }}': _br_number(resumo.total_recebido, 0),
        '{{ "{:,.0f}".format(resumo.total_perca_mensal).replace(\',\', \'.\') }}': _br_number(resumo.total_perca_mensal, 0),
        '{{ "{:,.0f}".format(resumo.total_diferenca_anual).replace(\',\', \'.\') }}': _br_number(resumo.total_diferenca_anual, 0),
        '{{ "%.2f"|format(resumo.percentual_perda_anual) }}': f"{resumo.percentual_perda_anual:.2f}",
        '{{ "{:,.0f}".format(resumo.total_recebido + resumo.total_perca_mensal).replace(\',\', \'.\') }}': _br_number(resumo.total_recebido + resumo.total_perca_mensal, 0),
    }

    for old_pattern, new_value in replacements.items():
        html_content = html_content.replace(old_pattern, new_value)

    # Gerar PDF
    try:
        base_url = templates_root.as_uri() + '/'
        html_doc = weasyprint.HTML(string=html_content, base_url=base_url)
        pdf_bytes = html_doc.write_pdf()

        if not pdf_bytes or len(pdf_bytes) < 5000:
            logger.error(f"PDF detalhado gerado é muito pequeno: {len(pdf_bytes) if pdf_bytes else 0} bytes")
            raise ValueError("PDF gerado está muito pequeno, possível erro na geração")

        logger.info(
            f"PDF detalhado gerado com sucesso - Município: {municipio_nome}/{uf}, "
            f"Tamanho: {len(pdf_bytes)} bytes"
        )
        return pdf_bytes
    except ValueError as e:
        logger.error(f"Erro de validação ao gerar PDF detalhado: {e}")
        raise
    except Exception as e:
        logger.error(
            f"Erro inesperado ao gerar PDF detalhado - "
            f"Município: {municipio_nome}/{uf}, Competência: {competencia}: {e}",
            exc_info=True
        )
        raise
