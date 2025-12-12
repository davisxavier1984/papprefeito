# Documentação Técnica - Gerador de PDF de Relatórios Financeiros

## Visão Geral

Sistema de geração de relatórios financeiros em PDF para municípios, com análise de projeções de recursos da Atenção Básica. O sistema utiliza templates HTML modernos com CSS avançado e converte para PDF através da biblioteca WeasyPrint.

---

## Arquitetura do Sistema

### Estrutura de Arquivos

```
backend/
├── app/services/relatorio_pdf.py        # Módulo principal de geração
├── templates/
│   ├── relatorio_base.html              # Template HTML principal (3 páginas)
│   ├── css/
│   │   └── modern-cards.css             # Estilos premium com design system
│   └── images/
│       └── Imagem Timbrado.png          # Marca d'água institucional
```

---

## Componentes Principais

### 1. Módulo `relatorio_pdf.py`

**Localização:** [backend/app/services/relatorio_pdf.py](backend/app/services/relatorio_pdf.py)

#### Funções Públicas

##### `create_pdf_report()` - Função Principal
```python
def create_pdf_report(
    *,
    municipio_nome: Optional[str],
    uf: Optional[str],
    competencia: str,
    resumo: ResumoFinanceiro,
) -> bytes
```

**Descrição:** Ponto de entrada principal para geração de relatórios PDF.

**Parâmetros:**
- `municipio_nome`: Nome do município (ex: "Belo Horizonte")
- `uf`: Sigla do estado (ex: "MG")
- `competencia`: Período de referência (ex: "2025-01")
- `resumo`: Objeto `ResumoFinanceiro` com métricas calculadas

**Retorna:** Bytes do PDF gerado

**Implementação:** Atualmente delega para `create_html_pdf_report()`

---

##### `compute_financial_summary()` - Cálculo de Métricas
```python
def compute_financial_summary(
    resumos: Iterable[Dict[str, Any]],
    perdas: Iterable[float]
) -> ResumoFinanceiro
```

**Descrição:** Processa dados brutos e calcula resumo financeiro consolidado.

**Lógica de Cálculo:**
1. **Total Recebido Mensal:** Soma dos `vlEfetivoRepasse` dos resumos
2. **Perda Mensal:** Soma das perdas mensais
3. **Diferença Anual:** `perda_mensal × 12`
4. **Total Real Anual:** `total_recebido × 12`
5. **Percentual de Perda:** `(diferença_anual / total_real_anual) × 100`

**Validações:**
- Normaliza tamanhos de arrays (resumos vs perdas)
- Trata valores nulos como zero
- Evita divisão por zero no cálculo percentual

---

##### `create_html_pdf_report()` - Renderização HTML→PDF
```python
def create_html_pdf_report(
    *,
    municipio_nome: Optional[str],
    uf: Optional[str],
    competencia: str,
    resumo: ResumoFinanceiro,
) -> bytes
```

**Descrição:** Gerador moderno usando templates HTML + WeasyPrint.

**Fluxo de Processamento:**

1. **Carregamento de Assets**
   - Lê template HTML: `relatorio_base.html`
   - Lê estilos CSS: `modern-cards.css`
   - Carrega imagem de timbrado e converte para base64

2. **Processamento de Template**
   - Substitui variáveis Jinja2-like manualmente
   - Injeta CSS inline no `<style>` tag
   - Converte imagem para data URI (base64) para embutir no CSS

3. **Cálculos Auxiliares**
   ```python
   recurso_atual_anual = resumo.total_recebido * 12
   recurso_potencial_anual = recurso_atual_anual + resumo.total_diferenca_anual
   recurso_potencial_mensal = resumo.total_recebido + resumo.total_perda_mensal
   ```

4. **Métricas de Cards (Página 1)**
   - **Ratio Perda Mensal:** `perda_mensal / potencial_mensal`
   - **Ratio Diferença Anual:** `diferença_anual / potencial_anual`
   - **Ratio Recebimento:** `recebido / potencial_mensal`
   - Barras de progresso calculadas como `max(6%, min(100%, ratio × 100))`

5. **Substituições de Template**
   - Valores monetários formatados via `_br_number()`
   - Badges, detalhes e indicadores dos cards
   - Altura proporcional das barras do gráfico (página 2)
   - Eixo Y do gráfico em milhões

6. **Geração PDF**
   ```python
   html_doc = weasyprint.HTML(string=html_content, base_url=base_url)
   pdf_bytes = html_doc.write_pdf()
   ```

**Validações:**
- Verifica se HTML processado tem ≥1000 caracteres
- Valida se PDF gerado tem ≥5000 bytes
- Tratamento de exceções com traceback detalhado

---

##### `create_fpdf_report()` - Versão Legada (FPDF)
```python
def create_fpdf_report(
    *,
    municipio_nome: Optional[str],
    uf: Optional[str],
    competencia: str,
    resumo: ResumoFinanceiro,
) -> bytes
```

**Status:** LEGADO - Mantido para compatibilidade

**Descrição:** Gerador original usando biblioteca FPDF com desenho programático.

**Estrutura:**
- Página 1: `_create_page_1_intro_destaque()`
- Página 2: `_create_page_2_infograficos()`
- Página 3: `_create_page_3_impacto_conclusao()`

**Limitações:**
- Não suporta design moderno com glassmorphism
- Sem suporte a gradientes complexos
- Renderização manual de gráficos com primitivas

---

#### Funções Utilitárias Privadas

##### `_sanitize_text(value: str) -> str`
**Propósito:** Garante compatibilidade Latin-1 para FPDF
**Uso:** Versão legada apenas

##### `_br_number(value: float, decimals: int = 2) -> str`
**Propósito:** Formata números no padrão brasileiro
- Exemplo: `1234567.89` → `"1.234.567,89"`
- Usado em valores monetários

##### `_safe_ratio(value: float, total: float) -> float`
**Propósito:** Calcula proporção segura entre 0.0 e 1.0
- Evita divisão por zero
- Clamp para intervalo válido

##### `_mix_with_white(color: tuple, factor: float) -> tuple`
**Propósito:** Gera tonalidades mais claras de cores
- `factor=0.0` → cor original
- `factor=1.0` → branco
- Usado em degradês de cards (FPDF)

##### `_progress_value(ratio: float) -> int` (inline)
**Propósito:** Converte ratio para percentual de progresso
- Mínimo: 6% (para visualização)
- Máximo: 100%

---

### 2. Template HTML - `relatorio_base.html`

**Localização:** [backend/templates/relatorio_base.html](backend/templates/relatorio_base.html)

#### Estrutura do Documento

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Relatório de Projeção Financeira - {{ municipio_nome }}/{{ uf }}</title>
    <style>{{ css_content }}</style>
</head>
<body>
    <div class="page page-1">...</div>      <!-- Página 1 -->
    <div class="page page-2">...</div>      <!-- Página 2 -->
    <div class="page page-3">...</div>      <!-- Página 3 -->
</body>
</html>
```

#### Página 1 - Introdução e Destaque

**Seções:**

1. **Cabeçalho do Relatório** (`.report-header`)
   - Título: "Relatório de Projeção Financeira – Município de {nome}/{uf}"
   - Saudação: "Excelentíssimo(a) Senhor(a) Prefeito(a),"
   - Introdução explicativa

2. **Banner Principal** (`.banner-principal`)
   - Pergunta destaque: "Quanto eu deixo de receber anualmente?"
   - Percentual de perda em fonte grande
   - Gradiente vermelho impactante

3. **Cards Financeiros Premium** (`.financial-cards`)

   **Card 1: Perda Mensal** (`.danger`)
   - Ícone: ⚠ (alerta)
   - Trend: ↓ (queda)
   - Badge: "Oportunidade"
   - Valor: `R$ {total_perda_mensal}`
   - Descrição: "recursos perdidos mensalmente..."
   - Detalhe: "Equivalente a R$ {...} por ano"
   - Barra de progresso: % do potencial mensal

   **Card 2: Impacto Anual** (`.warning`)
   - Ícone: 📊 (gráfico)
   - Trend: Σ (somatório)
   - Badge: "Visão anual"
   - Valor: `R$ {total_diferenca_anual}`
   - Descrição: "valor total de recursos não recebidos..."
   - Detalhe: "Impacto de {...}% do orçamento anual"
   - Barra de progresso: % do potencial anual

   **Card 3: Recursos Atuais** (`.success`)
   - Ícone: 💰 (dinheiro)
   - Trend: ✓ (check)
   - Badge: "Cenário atual"
   - Valor: `R$ {total_recebido}`
   - Descrição: "recursos mensais efetivamente recebidos..."
   - Detalhe: "Potencial com ajuste: R$ {...}"
   - Barra de progresso: % de cobertura atual

---

#### Página 2 - Comparativos e Análise Mensal

**Seção Superior: Comparativo de Recursos** (`.comparison-section`)

1. **Recursos Comparados** (`.resource-comparison`)
   - **Atual (vermelho):** Recurso AB atual anual
   - **Potencial (verde):** Recurso AB potencial anual

2. **Gráfico de Barras CSS** (`.chart-container`)
   - Barra atual: altura proporcional ao valor
   - Barra potencial: 100% de altura
   - Seta de crescimento entre barras
   - Eixo Y: 0 até valor máximo em milhões

**Seção Inferior: Análise Mensal** (`.monthly-analysis`)

1. **Valores Mensais** (`.monthly-values`)
   - Coluna 1: Recurso Atual (vermelho)
   - Coluna 2: Recurso Potencial (preto)
   - Coluna 3: Acréscimo (azul/verde)

2. **Destaque de Acréscimo** (`.monthly-highlight`)
   - Título: "Acréscimo Mensal de Receita"
   - Valor em destaque
   - Seta para cima: ↗

---

#### Página 3 - Impacto e Conclusão

**Seção Superior: Impacto Visual** (`.impact-section`)
- **Percentual Grande:** {percentual_perda_anual}% em fonte 42px (vermelho)
- **Símbolo =:** em verde, tamanho 36px
- **Caixa de Valor:** Box com sombra contendo `R$ {total_diferenca_anual}`

**Seção Central: Mensagem Motivacional** (`.motivational-message`)
- Background gradiente verde
- Texto: "MAIS RECURSO E UMA MELHOR QUALIDADE DE SAÚDE PARA A POPULAÇÃO!"

**Seção Inferior: Considerações Finais** (`.final-considerations`)
- Título: "4. Considerações Finais"
- Texto explicativo sobre acompanhamento de indicadores
- Oferta de suporte técnico
- Assinatura:
  - "Atenciosamente,"
  - "Mais Gestor"
  - "Alysson Ribeiro"

---

### 3. CSS Design System - `modern-cards.css`

**Localização:** [backend/templates/css/modern-cards.css](backend/templates/css/modern-cards.css)

#### Variáveis CSS (`:root`)

**Paleta de Cores Premium:**
```css
--color-danger: #FF3B30        /* Vermelho principal */
--color-danger-dark: #D70015
--color-danger-light: #FF6B6B

--color-warning: #FF9500       /* Laranja/amarelo */
--color-warning-dark: #E8890C
--color-warning-light: #FFB84D

--color-success: #00C896       /* Verde/ciano */
--color-success-dark: #00A578
--color-success-light: #26D0CE
```

**Cores de Texto:**
```css
--color-text: #1A1A1A
--color-text-muted: #6B7280
--color-text-light: #9CA3AF
--color-white: #FFFFFF
```

**Sombras Premium:**
```css
--shadow-soft: 0 1px 3px rgba(0,0,0,0.08)
--shadow-medium: 0 4px 20px rgba(0,0,0,0.12)
--shadow-strong: 0 12px 40px rgba(0,0,0,0.15)
--shadow-premium: 0 20px 60px rgba(0,0,0,0.18)
```

**Bordas e Raios:**
```css
--radius: 16px
--radius-small: 8px
--radius-large: 24px
```

**Gradientes:**
- Danger: 135° de #FF6B6B → #D70015
- Warning: 135° de #FFB84D → #E8890C
- Success: 135° de #26D0CE → #00A578

---

#### Configuração de Página

**Formato A4:**
```css
@page {
    size: A4;
    margin: 0;
}

.page {
    min-height: 297mm;
    width: 210mm;
    padding: 20mm;
    background-image: url('../images/Imagem Timbrado.png');
    background-size: cover;
}
```

**Overlays para Legibilidade:**
- **Página 1:** `rgba(255, 255, 255, 0.70)` - overlay mais forte
- **Páginas 2 e 3:** `rgba(255, 255, 255, 0.85)` - overlay mais suave
- Z-index: 1 (overlay) vs 2 (conteúdo)

---

#### Componentes de Design

##### Cards Financeiros (`.financial-card`)

**Propriedades Principais:**
```css
background: var(--glass-bg);          /* Glassmorphism */
backdrop-filter: blur(10px);
border-radius: 16px;
box-shadow: var(--shadow-premium);
border-top: 3px solid var(--accent-color);
padding: 24px 20px;
min-height: 180px;
```

**Efeitos Visuais:**
1. **Brilho Superior:** Linha gradiente sutil no topo
2. **Elemento Decorativo:** Canto superior direito com opacidade 10%
3. **Hover (para web):** `translateY(-2px)` + sombra mais forte

**Variantes:**
- `.danger` → vermelho (#FF3B30)
- `.warning` → laranja (#FF9500)
- `.success` → verde (#00C896)

---

##### Ícones de Cards (`.card-icon`)

**Estrutura:**
```css
width: 44px;
height: 44px;
border-radius: 8px;
background: var(--gradient-accent);
box-shadow: 0 4px 16px rgba(cor-tematica, 0.3);
```

**Efeito de Profundidade:**
- `::before` pseudo-elemento com borda interna
- `var(--shadow-inner)` para relevo

---

##### Valores e Tipografia

**Hierarquia de Texto:**
1. **`.card-title`** (10px, upperdase, 800 weight) - cinza
2. **`.card-value`** (28px, 900 weight) - cor temática com gradiente
3. **`.card-description`** (10px, 500 weight) - cinza médio
4. **`.card-detail`** (9px, 500 weight) - cinza claro

**Técnica de Gradiente em Texto:**
```css
background: var(--gradient-accent);
-webkit-background-clip: text;
-webkit-text-fill-color: transparent;
```
(Com fallback para PDF)

---

##### Barras de Progresso (`.card-progress`)

**Estrutura:**
```css
height: 6px;
background: rgba(26, 26, 26, 0.08);    /* Track */
border-radius: 999px;

.card-progress-bar {
    background: var(--gradient-accent);   /* Fill */
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.4);
}
```

**Overlay de Glassmorphism:**
- `::before` com `mix-blend-mode: screen`

---

##### Banner Principal (`.banner-principal`)

```css
background: var(--gradient-danger);
padding: 20px;
border-radius: 16px;
box-shadow: var(--shadow-strong);

.banner-percentage {
    font-size: 48px;
    font-weight: 900;
    text-shadow: 0 2px 4px rgba(0,0,0,0.3);
}
```

---

##### Gráfico de Barras CSS (`.bar-chart`)

**Layout:**
```css
display: flex;
align-items: end;
justify-content: center;
height: 120px;

.bar {
    width: 40px;
    border-radius: 4px 4px 0 0;
    min-height: 20px;
}

.current-bar { background: var(--gradient-danger); }
.potential-bar { background: var(--gradient-success); }
```

**Seta de Crescimento:**
```css
.chart-arrow {
    font-size: 20px;
    color: var(--color-success);
    align-self: center;
}
```

---

#### Animações Premium

**Definidas mas Desabilitadas em PDF:**

1. **`slideInUp`** - Cards surgem de baixo com fade
2. **`fadeInScale`** - Ícones aparecem com escala
3. **`pulseGlow`** - Indicadores de tendência pulsam
4. **`gradientShift`** - Background gradiente animado (400% × 400%)

**Delays Escalonados:**
```css
.financial-card:nth-child(1) { animation-delay: 0.1s; }
.financial-card:nth-child(2) { animation-delay: 0.2s; }
.financial-card:nth-child(3) { animation-delay: 0.3s; }
```

**Desabilitação em Print:**
```css
@media print {
    *, *::before, *::after {
        animation-duration: 0s !important;
        transition-duration: 0s !important;
    }
}
```

---

#### Configurações de Impressão

**Quebras de Página:**
```css
.page { page-break-after: always; }
.page:last-child { page-break-after: avoid; }

.financial-card { page-break-inside: avoid; }
.chart-container { page-break-inside: avoid; }
.impact-section { page-break-inside: avoid; }
```

**Preservação de Cores:**
```css
body {
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
    color-adjust: exact;
}
```

---

## Fluxo de Dados Completo

### 1. Entrada de Dados
```python
# Dados brutos da API/banco
resumos = [
    {"vlEfetivoRepasse": 150000.00, ...},
    {"vlEfetivoRepasse": 152000.00, ...},
    # ... 12 meses
]
perdas = [5000.00, 5200.00, ...]  # Perdas mensais
```

### 2. Processamento
```python
# Cálculo de métricas
resumo = compute_financial_summary(resumos, perdas)
# ResumoFinanceiro(
#     total_recebido=151000.00,         # Média mensal
#     total_perda_mensal=5100.00,
#     total_diferenca_anual=61200.00,   # 5100 × 12
#     percentual_perda_anual=3.34       # (61200 / 1830000) × 100
# )
```

### 3. Geração de Template
```python
# Substituições no HTML
"{{ municipio_nome }}" → "Belo Horizonte"
"{{ uf }}" → "MG"
"{{ resumo.total_recebido }}" → "151.000"
"__PERDA_PROGRESS__" → "33"  # 33% de progresso
```

### 4. Renderização PDF
```python
# WeasyPrint processa HTML + CSS
html_doc = weasyprint.HTML(string=html_content)
pdf_bytes = html_doc.write_pdf()
```

### 5. Entrega
```python
# Retorna bytes do PDF (tipicamente 200-500KB)
return pdf_bytes  # Pronto para download ou envio
```

---

## Dependências e Requisitos

### Bibliotecas Python

```python
# requirements.txt
weasyprint>=60.0     # HTML→PDF rendering
fpdf2>=2.7           # [LEGADO] Geração FPDF
```

**Dependências do WeasyPrint:**
- Cairo (renderização gráfica)
- Pango (renderização de texto)
- GdkPixbuf (processamento de imagens)

### Assets Necessários

1. **Imagem de Timbrado** (obrigatório)
   - Caminho: `backend/templates/images/Imagem Timbrado.png`
   - Formato: PNG
   - Uso: Background institucional de todas as páginas
   - Processamento: Convertido para base64 e embutido no CSS

2. **Template HTML** (obrigatório)
   - Caminho: `backend/templates/relatorio_base.html`
   - Encoding: UTF-8

3. **Stylesheet CSS** (obrigatório)
   - Caminho: `backend/templates/css/modern-cards.css`
   - Encoding: UTF-8

---

## Tratamento de Erros

### Validações Implementadas

**No `create_html_pdf_report()`:**

1. **Asset Missing:**
   ```python
   if not template_path.exists():
       raise FileNotFoundError(f"Template HTML não encontrado: {template_path}")
   ```

2. **HTML Malformado:**
   ```python
   if not html_content or len(html_content) < 1000:
       raise ValueError("HTML template não foi processado corretamente")
   ```

3. **PDF Inválido:**
   ```python
   if not pdf_bytes or len(pdf_bytes) < 5000:
       raise ValueError("PDF gerado está muito pequeno")
   ```

4. **Exceções Gerais:**
   ```python
   except Exception as e:
       print(f"❌ Erro ao gerar PDF com HTML-to-PDF: {e}")
       traceback.print_exc()
       raise
   ```

### Casos de Borda

**Divisão por Zero:**
- `_safe_ratio()` retorna 0.0 se `total <= 0`
- `percentual_perda_anual` retorna 0.0 se `total_real_anual == 0`

**Arrays Desalinhados:**
- `compute_financial_summary()` normaliza tamanhos:
  - Preenche perdas com zeros se `len(perdas) < len(resumos)`
  - Trunca perdas se `len(perdas) > len(resumos)`

**Valores Nulos:**
- `float(item.get('vlEfetivoRepasse') or 0.0)` trata `None` como 0

**Encoding:**
- Template lido com `encoding='utf-8'`
- FPDF legado usa `_sanitize_text()` para Latin-1

---

## Otimizações e Performance

### Escolhas de Design

1. **Base64 Inline para Imagens**
   - **Prós:** PDF auto-contido, sem dependências externas
   - **Contras:** Aumenta tamanho do HTML intermediário (~30%)
   - **Justificativa:** WeasyPrint precisa de acesso direto aos assets

2. **CSS Embutido**
   - Evita requisições de arquivo externo
   - Facilita processamento do WeasyPrint

3. **Substituições Manuais vs Template Engine**
   - Não usa Jinja2 para evitar dependência extra
   - Substituições simples com `.replace()`
   - Trade-off: menos flexibilidade, mais controle

### Métricas Típicas

- **Tempo de Geração:** 500-800ms
- **Tamanho do PDF:** 200-500KB (depende da imagem de timbrado)
- **Resolução:** 96 DPI (padrão WeasyPrint)

---

## Manutenção e Extensão

### Como Adicionar Novos Cards

1. **No Template HTML** (`relatorio_base.html`):
   ```html
   <div class="financial-card success">
       <div class="card-trend">➚</div>
       <div class="card-badge">__NOVO_BADGE__</div>
       <div class="card-header">
           <div class="card-icon">🎯</div>
           <h3 class="card-title">Novo Card</h3>
       </div>
       <div class="card-value">R$ __NOVO_VALOR__</div>
       <p class="card-description">Descrição do novo card</p>
       <div class="card-progress">
           <div class="card-progress-bar" style="width: __NOVO_PROGRESS__%"></div>
       </div>
   </div>
   ```

2. **No Código Python** (`relatorio_pdf.py:create_html_pdf_report()`):
   ```python
   replacements = {
       # ... existentes
       '__NOVO_BADGE__': html.escape('Nova Métrica'),
       '__NOVO_VALOR__': _br_number(novo_calculo, 0),
       '__NOVO_PROGRESS__': str(_progress_value(novo_ratio)),
   }
   ```

---

### Como Adicionar Nova Página

1. **No Template HTML:**
   ```html
   <div class="page page-4" style="page-break-before: always;">
       <!-- Conteúdo da nova página -->
   </div>
   ```

2. **No CSS** (se necessário overlay customizado):
   ```css
   .page-4::before {
       background: rgba(255, 255, 255, 0.90);
   }
   ```

3. **Adicionar Estilos Específicos:**
   ```css
   .custom-section {
       padding: 20px;
       /* ... */
   }
   ```

---

### Como Alterar Cores do Design System

**Modificar variáveis CSS** em `modern-cards.css`:
```css
:root {
    /* Mudar paleta danger para roxo */
    --color-danger: #9B51E0;
    --color-danger-dark: #7B2CBF;
    --color-danger-light: #BB6BD9;

    /* Atualizar gradientes */
    --gradient-danger: linear-gradient(135deg, #BB6BD9 0%, #9B51E0 50%, #7B2CBF 100%);
}
```

Todas as instâncias de `.danger` atualizarão automaticamente.

---

### Como Adicionar Nova Fonte

1. **Incluir fonte no CSS:**
   ```css
   @font-face {
       font-family: 'CustomFont';
       src: url('data:font/woff2;base64,<base64-data>') format('woff2');
   }

   body {
       font-family: 'CustomFont', 'Segoe UI', sans-serif;
   }
   ```

2. **Considerações:**
   - WeasyPrint suporta: WOFF, WOFF2, TTF, OTF
   - Embutir fonte em base64 para portabilidade
   - Verificar licença da fonte para embedding

---

## Troubleshooting

### Problema: PDF Gerado Está Vazio/Branco

**Causas Possíveis:**
1. Imagem de timbrado não encontrada
2. CSS não carregado corretamente
3. Z-index incorreto (overlay cobrindo conteúdo)

**Solução:**
```python
# Adicionar logs de debug
print(f"CSS length: {len(css_content)}")
print(f"HTML length: {len(html_content)}")
print(f"Imagem base64 length: {len(img_base64)}")
```

---

### Problema: Formatação de Números Incorreta

**Causa:** Locale diferente ou caracteres especiais

**Solução:**
```python
# Verificar se _br_number() está sendo usado
assert _br_number(1234.56, 2) == "1.234,56"

# Verificar substituições no HTML
print(html_content.count('R$'))  # Deve ser múltiplo de cards/valores
```

---

### Problema: WeasyPrint Crashes

**Causas Comuns:**
1. Dependências do sistema faltando (Cairo, Pango)
2. HTML malformado
3. CSS inválido

**Diagnóstico:**
```bash
# Verificar instalação
python -c "import weasyprint; print(weasyprint.__version__)"

# Testar com HTML mínimo
python -c "
from weasyprint import HTML
HTML(string='<h1>Test</h1>').write_pdf('/tmp/test.pdf')
"
```

---

### Problema: Cards Não Quebram Linha

**Causa:** CSS flexbox não respeitado pelo WeasyPrint

**Solução:**
```css
.financial-cards {
    display: flex;
    flex-wrap: wrap;  /* Essencial */
    gap: 16px;
}

.financial-card {
    flex: 1 1 30%;  /* Base width + grow/shrink */
    min-width: 150px;
}
```

---

## Segurança

### Validações de Input

**Sanitização:**
- `html.escape()` usado em `__BADGE__`, `__DETALHE__`, etc.
- Previne injeção de HTML/JavaScript

**Validação de Paths:**
```python
templates_root = Path(__file__).resolve().parents[2] / "templates"
# Usa paths absolutos para evitar path traversal
```

### Dados Sensíveis

**Atualmente Não Há:**
- Nenhum dado pessoal identificável (PII) além do nome do município
- Valores financeiros são agregados/públicos

**Recomendação para Futuro:**
- Adicionar watermark com "CONFIDENCIAL" se necessário
- Implementar controle de acesso no endpoint que chama `create_pdf_report()`

---

## Testes Recomendados

### Testes Unitários

```python
def test_br_number_formatting():
    assert _br_number(1234.56, 2) == "1.234,56"
    assert _br_number(1000000, 0) == "1.000.000"

def test_safe_ratio():
    assert _safe_ratio(50, 100) == 0.5
    assert _safe_ratio(150, 100) == 1.0  # Clamped
    assert _safe_ratio(10, 0) == 0.0      # Divisão por zero

def test_compute_financial_summary():
    resumos = [{"vlEfetivoRepasse": 100000}] * 12
    perdas = [5000] * 12
    result = compute_financial_summary(resumos, perdas)
    assert result.total_recebido == 100000
    assert result.total_perda_mensal == 5000 * 12
```

### Testes de Integração

```python
def test_pdf_generation():
    resumo = ResumoFinanceiro(
        total_recebido=150000,
        total_perda_mensal=5000,
        total_diferenca_anual=60000,
        percentual_perda_anual=3.3
    )
    pdf_bytes = create_pdf_report(
        municipio_nome="Teste",
        uf="MG",
        competencia="2025-01",
        resumo=resumo
    )
    assert len(pdf_bytes) > 5000
    assert pdf_bytes[:4] == b'%PDF'  # Assinatura PDF
```

### Testes Visuais (Manual)

1. **Renderização em Diferentes Navegadores:**
   - Salvar HTML intermediário
   - Abrir em Chrome, Firefox, Safari
   - Verificar consistência visual

2. **Checklist de Qualidade:**
   - [ ] Cards alinhados corretamente
   - [ ] Valores monetários formatados (1.234,56)
   - [ ] Cores temáticas aplicadas
   - [ ] Barras de progresso proporcionais
   - [ ] Gráfico de barras com altura correta
   - [ ] Timbrado visível mas não obstrusivo
   - [ ] Quebras de página adequadas
   - [ ] Assinatura na página 3

---

## Changelog e Versões

### Versão Atual (HTML + WeasyPrint)
**Implementado em:** 2025-01
**Features:**
- Design moderno com glassmorphism
- Gradientes CSS3 complexos
- Animações (desabilitadas em PDF)
- Template HTML flexível
- Imagem embutida em base64

### Versão Legada (FPDF)
**Status:** Mantida para fallback
**Limitações:**
- Design programático (menos flexível)
- Sem gradientes complexos
- Fonte limitada (Helvetica)
- Renderização manual de gráficos

---

## Referências Técnicas

### Documentação Externa
- [WeasyPrint Documentation](https://doc.courtbouillon.org/weasyprint/)
- [CSS Paged Media Module](https://www.w3.org/TR/css-page-3/)
- [FPDF Documentation](http://www.fpdf.org/en/doc/index.php)

### Padrões Utilizados
- **CSS3:** Flexbox, Gradientes, Variáveis, Animações
- **HTML5:** Estrutura semântica
- **Encoding:** UTF-8 (HTML/CSS), Latin-1 (FPDF fallback)
- **Locale:** pt-BR (formatação de números)

---

## Autoria e Manutenção

**Módulo Principal:** `backend/app/services/relatorio_pdf.py`
**Templates:** `backend/templates/`
**Projeto:** Sistema de Análise Financeira Municipal - Atenção Básica
**Licença:** (Especificar conforme projeto)

---

**Última Atualização:** 2025-01-29
**Versão da Documentação:** 1.0