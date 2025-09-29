# Especificações Técnicas - Sistema de Relatórios PDF

**Versão:** 1.0
**Data:** 2025-01-29
**PM:** John
**Projeto:** MaisPAP - Sistema de Relatórios

---

## 1. VISÃO GERAL

**Objetivo:** Expandir o sistema existente de relatórios PDF de 2 para 3 páginas, incorporando infográficos comparativos e estrutura executiva formal.

**Tecnologias Base:**
- Backend: FastAPI + Python + fpdf2
- Arquivo principal: `backend/app/services/relatorio_pdf.py`
- Endpoint: `/relatorios/pdf` (existente)

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

### Cálculos Necessários:
```python
# Valores mensais (base)
recurso_atual_mensal = resumo.total_recebido
acrescimo_mensal = resumo.total_perca_mensal
recurso_potencial_mensal = recurso_atual_mensal + acrescimo_mensal

# Valores anuais (página 2)
recurso_atual_anual = recurso_atual_mensal * 12
recurso_potencial_anual = recurso_atual_anual + resumo.total_diferenca_anual
```

### Códigos de Cor (RGB):
```python
VERMELHO = (220, 53, 69)    # Valores atuais
AZUL = (40, 116, 240)       # Acréscimos/crescimento
PRETO = (0, 0, 0)          # Valores potenciais
VERDE = (40, 167, 69)      # Mensagens positivas
```

### Fontes e Tamanhos:
```python
TITULO_PRINCIPAL = ('Helvetica', 'B', 18)
SUBTITULO = ('Helvetica', 'B', 14)
TEXTO_NORMAL = ('Helvetica', '', 12)
PERCENTUAL_GRANDE = ('Helvetica', 'B', 46)
PERCENTUAL_MEDIO = ('Helvetica', 'B', 42)
VALORES = ('Helvetica', 'B', 20)
```