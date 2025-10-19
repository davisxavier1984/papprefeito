#!/usr/bin/env python3
"""Script simples para visualizar o HTML do relatório detalhado."""

from pathlib import Path
import base64

# Carregar CSS
css_path = Path("backend/templates/css/modern-cards.css")
css_content = css_path.read_text(encoding='utf-8')

# Carregar imagem do timbrado
img_path = Path("backend/templates/images/Imagem Timbrado.png")
if img_path.exists():
    with open(img_path, "rb") as img_file:
        img_data = img_file.read()
        img_base64 = base64.b64encode(img_data).decode('utf-8')
else:
    img_base64 = ""
    print("AVISO: Imagem do timbrado não encontrada")

# Carregar template HTML
template_path = Path("backend/templates/relatorio_detalhado.html")
html_content = template_path.read_text(encoding='utf-8')

# Substituir placeholders
html_content = html_content.replace("{{ css_content }}", css_content)
html_content = html_content.replace("{{ img_base64 }}", img_base64)
html_content = html_content.replace("{{ municipio_nome }}", "Teste")
html_content = html_content.replace("{{ uf }}", "MG")
html_content = html_content.replace("__COMPETENCIA_CNES__", "202501")
html_content = html_content.replace("__PARCELA_PGTO__", "202501")
html_content = html_content.replace("__ESF_CONTENT__", '<div class="detail-section"><p>Conteúdo eSF teste</p></div>')
html_content = html_content.replace("__EAP_CONTENT__", '<div class="detail-section"><p>Conteúdo eAP teste</p></div>')
html_content = html_content.replace("__CEO_CONTENT__", '<div class="detail-section"><p>Conteúdo CEO teste</p></div>')
html_content = html_content.replace("__LRPD_CONTENT__", '<div class="detail-section"><p>Conteúdo LRPD teste</p></div>')
html_content = html_content.replace("__SAUDE_BUCAL_CONTENT__", '<div class="detail-section"><p>Conteúdo de teste</p></div>')
html_content = html_content.replace("__EMULTI_CONTENT__", '<div class="detail-section"><p>Conteúdo de teste</p></div>')

# Valores de resumo
html_content = html_content.replace("{{ \"{:,.0f}\".format(resumo.total_recebido).replace(',', '.') }}", "120.000")
html_content = html_content.replace("{{ \"{:,.0f}\".format(resumo.total_perca_mensal).replace(',', '.') }}", "15.000")
html_content = html_content.replace("{{ \"{:,.0f}\".format(resumo.total_diferenca_anual).replace(',', '.') }}", "180.000")
html_content = html_content.replace('{{ "%.2f"|format(resumo.percentual_perda_anual) }}', "12.50")
html_content = html_content.replace("{{ \"{:,.0f}\".format(resumo.total_recebido + resumo.total_perca_mensal).replace(',', '.') }}", "135.000")

# Salvar HTML
output_path = Path("teste_detalhado_visual.html")
output_path.write_text(html_content, encoding='utf-8')
print(f"✓ HTML gerado: {output_path.absolute()}")
print("Abra este arquivo no navegador para visualizar o resultado")
