#!/usr/bin/env python3
"""Teste final com implementação corrigida."""

import sys
from pathlib import Path
import weasyprint

sys.path.append('.')
from app.models.schemas import ResumoFinanceiro


def _br_number(value: float, decimals: int = 2) -> str:
    """Formata números no padrão brasileiro (ponto como milhar e vírgula decimal)."""
    pattern = f"{{:,.{decimals}f}}"
    formatted = pattern.format(value)
    return formatted.replace(',', 'X').replace('.', ',').replace('X', '.')


def create_working_pdf(
    municipio_nome: str,
    uf: str,
    competencia: str,
    resumo: ResumoFinanceiro,
) -> bytes:
    """Implementação funcional baseada no debug."""

    # Carregar CSS e HTML
    css_path = Path('templates/css/modern-cards.css')
    template_path = Path('templates/relatorio_base.html')

    css_content = css_path.read_text(encoding='utf-8')
    html_template = template_path.read_text(encoding='utf-8')

    # Calcular valores necessários
    recurso_atual_anual = resumo.total_recebido * 12
    recurso_potencial_anual = recurso_atual_anual + resumo.total_diferenca_anual
    recurso_potencial_mensal = resumo.total_recebido + resumo.total_perca_mensal

    # Substituições básicas
    html_content = html_template.replace('{{ municipio_nome }}', municipio_nome)
    html_content = html_content.replace('{{ uf }}', uf)
    html_content = html_content.replace('{{ css_content }}', css_content)

    # Todas as substituições
    replacements = {
        '{{ "%.2f"|format(resumo.percentual_perda_anual) }}': f"{resumo.percentual_perda_anual:.2f}",
        '{{ "{:,.0f}".format(resumo.total_perca_mensal).replace(\',\', \'.\') }}': _br_number(resumo.total_perca_mensal, 0),
        '{{ "{:,.0f}".format(resumo.total_diferenca_anual).replace(\',\', \'.\') }}': _br_number(resumo.total_diferenca_anual, 0),
        '{{ "{:,.0f}".format(resumo.total_recebido).replace(\',\', \'.\') }}': _br_number(resumo.total_recebido, 0),
        '{{ "{:,.0f}".format(resumo.total_recebido * 12).replace(\',\', \'.\') }}': _br_number(recurso_atual_anual, 0),
        '{{ "{:,.0f}".format((resumo.total_recebido * 12) + resumo.total_diferenca_anual).replace(\',\', \'.\') }}': _br_number(recurso_potencial_anual, 0),
        '{{ "{:,.0f}".format(resumo.total_recebido + resumo.total_perca_mensal).replace(\',\', \'.\') }}': _br_number(recurso_potencial_mensal, 0),
    }

    for old, new in replacements.items():
        html_content = html_content.replace(old, new)

    # Substituir cálculos para gráfico de barras
    if recurso_potencial_anual > 0:
        bar_height_percentage = (recurso_atual_anual / recurso_potencial_anual) * 100
    else:
        bar_height_percentage = 50

    html_content = html_content.replace(
        '{{ (resumo.total_recebido * 12 / ((resumo.total_recebido * 12) + resumo.total_diferenca_anual) * 100) }}',
        f"{bar_height_percentage:.1f}"
    )

    # Substituir valor em milhões
    max_value_millions = recurso_potencial_anual / 1000000
    html_content = html_content.replace(
        '{{ "{:.1f}mi".format(((resumo.total_recebido * 12) + resumo.total_diferenca_anual) / 1000000) }}',
        f"{max_value_millions:.1f}mi"
    )

    # Gerar PDF
    html_doc = weasyprint.HTML(string=html_content)
    return html_doc.write_pdf()


# Teste
resumo = ResumoFinanceiro(
    total_perca_mensal=15000.00,
    total_diferenca_anual=180000.00,
    percentual_perda_anual=12.5,
    total_recebido=120000.00
)

pdf_bytes = create_working_pdf('São Paulo', 'SP', '2025-01', resumo)

# Validar sem salvar em disco
assert len(pdf_bytes) > 0, "PDF não pode estar vazio"
assert pdf_bytes[:4] == b'%PDF', "PDF deve começar com %PDF"

print(f'✅ PDF funcional validado: {len(pdf_bytes)} bytes (não salvo em disco)')