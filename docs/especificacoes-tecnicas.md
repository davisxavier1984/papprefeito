# Especificações Técnicas - Sistema de Relatórios PDF

**Versão:** 1.0
**Data:** 2025-01-29
**PM:** John
**Projeto:** MaisPAP - Sistema de Relatórios

---

## 1. VISÃO GERAL

**Objetivo:** Modernizar o sistema de relatórios PDF com design UI/UX avançado, utilizando arquitetura HTML-to-PDF para layouts responsivos e elementos visuais modernos.

**Tecnologias Base:**
- Backend: FastAPI + Python
- Engine PDF: **HTML-to-PDF** (WeasyPrint ou Playwright)
- Templates: HTML + CSS moderno
- Arquivo principal: `backend/app/services/relatorio_pdf.py`
- Endpoint: `/relatorios/pdf` (existente, com nova implementação)

> **📘 Nota de Implementação:** Este documento descreve as especificações planejadas. Para a implementação real e documentação técnica completa, consulte [gerador-pdf-documentacao.md](./gerador-pdf-documentacao.md).

---

## 2. ESTRUTURA DAS 3 PÁGINAS

### PÁGINA 1: Introdução + Destaque Principal

**Layout Superior (30% da página):**
```
Título: "Relatório de Projeção Financeira – Município de {municipio_nome}-{uf}"
Saudação: "Excelentíssimo(a) Senhor(a) Prefeito(a),"
Texto: "Com o objetivo de oferecer uma visão estratégica sobre a evolução dos
recursos do município, apresentamos a seguir uma análise detalhada com base
no cenário atual e projeções futuras."
```

**Layout Inferior (70% da página):**
```
Banner vermelho: "QUANTO EU DEIXO DE RECEBER ANUALMENTE?"
Percentual: {percentual_perda_anual}% (fonte 46px)
Resumo:
• Perda mensal estimada: R$ {total_perca_mensal}
• Diferença anual estimada: R$ {total_diferenca_anual}
• Total recebido mensalmente: R$ {total_recebido}
```

### PÁGINA 2: Infográficos Duplos

**Seção Superior (50% da página) - Comparativo Anual:**
```
Título: "Comparativo de Recursos - Atenção Básica {municipio_nome}"

Layout Horizontal:
┌─────────────────┬─────────────────┐
│ Recurso Atenção │ Recurso Atenção │
│ Básica atual    │ Básica potencial│
│ {atual_anual}   │ {potencial_anual}│
└─────────────────┴─────────────────┘

Gráfico de Barras:
- Barra vermelha (altura proporcional ao valor atual)
- Barra azul (altura proporcional ao valor potencial)
- Seta azul conectando as barras
- Eixo Y em milhões
```

**Seção Inferior (50% da página) - Análise Mensal:**
```
Título: "Mensal"

Valores:
• Recurso Atual: {recurso_atual_mensal} (vermelho)
• Recurso Potencial: {recurso_potencial_mensal} (preto)
• Acréscimo: {acrescimo_mensal} (azul)

Destaque: "Acréscimo Mensal de Receita" (sublinhado) + {acrescimo_mensal}
Seta azul irregular apontando para cima
```

### PÁGINA 3: Impacto + Conclusão

**Seção Superior (40% da página):**
```
Percentual: {percentual_perda_anual}% (fonte 42px)
Símbolo: = (fonte 36px)
Caixa com valor: R$ {total_diferenca_anual} (destacado)
```

**Seção Central (30% da página):**
```
Mensagem: "MAIS RECURSO E UMA MELHOR QUALIDADE DE SAÚDE PARA A POPULAÇÃO!"
```

**Seção Inferior (30% da página):**
```
Título: "4. Considerações Finais"
Texto: "O acompanhamento constante desses indicadores permitirá à administração
tomar decisões mais assertivas, equilibrando gastos e planejando investimentos
futuros com segurança. O avanço até o Cenário Ótimo permitirá à cidade ampliar
a qualidade dos serviços prestados à população e realizar obras de maior impacto
social e econômico.

Estamos à disposição para auxiliar na interpretação dos dados e na definição de
ações estratégicas para maximizar esse crescimento."

Assinatura:
"Atenciosamente,
Mais Gestor
Alysson Ribeiro"
```

---

## 3. ESPECIFICAÇÕES TÉCNICAS

### Arquitetura HTML-to-PDF:

**Dependências:**
```bash
pip install weasyprint
# ou alternativa:
pip install playwright pdfkit
```

**Estrutura de Templates (Planejada):**
```
backend/templates/
├── relatorio_base.html        # Template base
├── css/
│   ├── modern-cards.css       # Estilos dos cards UI/UX
│   ├── charts.css             # Gráficos com CSS
│   └── print.css              # Otimizações para PDF
└── components/
    ├── financial-cards.html    # Cards das métricas
    ├── charts.html            # Componentes de gráfico
    └── footer.html            # Assinatura e rodapé
```

> **📘 Implementação Real:** A estrutura foi simplificada para um template monolítico:
> ```
> backend/templates/
> ├── relatorio_base.html        # Template HTML completo (3 páginas)
> ├── css/
> │   └── modern-cards.css       # CSS Design System completo
> └── images/
>     └── Imagem Timbrado.png    # Background institucional
> ```
> Todos os componentes foram integrados no `relatorio_base.html` para melhor manutenibilidade.

### Design System CSS:

**Paleta de Cores (Planejada):**
```css
:root {
  --color-danger: #e74c3c;      /* Perdas - Vermelho */
  --color-warning: #f39c12;     /* Diferença - Laranja */
  --color-success: #2ecc71;     /* Recebimento - Verde */
  --color-text: #2c3e50;        /* Texto principal */
  --color-text-muted: #7f8c8d;  /* Texto secundário */
  --shadow: 0 4px 12px rgba(0,0,0,0.1);
  --radius: 12px;
  --gradient-danger: linear-gradient(135deg, #e74c3c, #c0392b);
  --gradient-warning: linear-gradient(135deg, #f39c12, #d68910);
  --gradient-success: linear-gradient(135deg, #2ecc71, #27ae60);
}
```

> **📘 Paleta Real Implementada:** A paleta foi refinada para tons mais premium:
> ```css
> --color-danger: #FF3B30        /* Vermelho mais vibrante */
> --color-warning: #FF9500       /* Laranja mais vivo */
> --color-success: #00C896       /* Verde/ciano moderno */
> --shadow-premium: 0 20px 60px rgba(0,0,0,0.18)
> --radius: 16px                 /* Bordas mais arredondadas */
> ```
> Veja a paleta completa em [gerador-pdf-documentacao.md](./gerador-pdf-documentacao.md#variáveis-css-root).

**Tipografia Moderna:**
```css
.card-title { font-size: 12px; font-weight: 700; text-transform: uppercase; }
.card-value { font-size: 24px; font-weight: 800; }
.card-description { font-size: 10px; color: var(--color-text-muted); }
.percentage-large { font-size: 48px; font-weight: 900; }
```

**Cards Premium:**
```css
.financial-card {
  background: white;
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  border-left: 4px solid var(--accent-color);
  padding: 20px;
  margin: 8px 0;
}
```

### Cálculos Necessários (Mantidos):
```python
# Valores mensais (base)
recurso_atual_mensal = resumo.total_recebido
acrescimo_mensal = resumo.total_perca_mensal
recurso_potencial_mensal = recurso_atual_mensal + acrescimo_mensal

# Valores anuais (página 2)
recurso_atual_anual = recurso_atual_mensal * 12
recurso_potencial_anual = recurso_atual_anual + resumo.total_diferenca_anual
```

### Implementação:
```python
def create_html_pdf_report(
    municipio_nome: str,
    uf: str,
    competencia: str,
    resumo: ResumoFinanceiro,
) -> bytes:
    """Gera relatório PDF usando templates HTML modernos."""
    html_content = render_template('relatorio_base.html', {
        'municipio_nome': municipio_nome,
        'uf': uf,
        'resumo': resumo,
        'competencia': competencia
    })

    return weasyprint.HTML(string=html_content).write_pdf()
```