# Briefing para Equipe de Desenvolvimento

**Sprint:** Próximo disponível
**Prioridade:** Alta
**Estimativa:** 3-5 dias
**Desenvolvedor responsável:** [A definir]

---

## 🎯 CONTEXTO

O sistema atual gera relatórios PDF de 2 páginas para análise de perdas financeiras municipais. Precisamos expandir para **3 páginas** com conteúdo específico solicitado pelos stakeholders.

## 🔧 ARQUIVOS A MODIFICAR

**Principal:**
- `backend/app/services/relatorio_pdf.py` (função `create_pdf_report`)

**Dependências (não modificar):**
- `backend/app/api/endpoints/relatorios.py`
- `backend/app/models/schemas.py`
- Frontend (Dashboard.tsx, api.ts, types/index.ts)

## 🚀 PLANO DE IMPLEMENTAÇÃO

### Passo 1: Refatorar estrutura atual
```python
def create_pdf_report(...) -> bytes:
    # Manter assinatura existente
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=18)

    # NOVA: Página 1 - Introdução + Destaque
    _create_page_1_intro_destaque(pdf, municipio_label, competencia, resumo)

    # NOVA: Página 2 - Infográficos Duplos
    _create_page_2_infograficos(pdf, municipio_label, resumo)

    # NOVA: Página 3 - Impacto + Conclusão
    _create_page_3_impacto_conclusao(pdf, resumo)

    return pdf.output(dest='S')
```

### Passo 2: Implementar funções auxiliares
- `_create_page_1_intro_destaque()`
- `_create_page_2_infograficos()`
- `_create_page_3_impacto_conclusao()`
- `_draw_bar_chart()` (para gráfico de barras)
- `_draw_arrow()` (para setas de crescimento)

### Passo 3: Testar e validar
- Gerar PDF com dados de teste
- Verificar layout em diferentes visualizadores
- Validar cálculos matemáticos
- Testar com diferentes tamanhos de valores

## ⚠️ CUIDADOS ESPECIAIS

### Compatibilidade:
- NÃO modificar assinatura da função `create_pdf_report`
- NÃO alterar parâmetros de entrada
- Manter formatação brasileira existente (`_br_number`)
- Preservar sanitização de texto (`_sanitize_text`)

### Performance:
- Manter geração de PDF < 3 segundos
- Não aumentar uso de memória significativamente

### Layout:
- Testar com nomes de municípios longos
- Verificar quebra de texto adequada
- Manter proporções visuais corretas

## 🧪 CENÁRIOS DE TESTE

```python
# Teste 1: Valores pequenos
resumo = ResumoFinanceiro(
    total_perca_mensal=100.0,
    total_diferenca_anual=1200.0,
    percentual_perda_anual=5.0,
    total_recebido=2000.0
)

# Teste 2: Valores grandes
resumo = ResumoFinanceiro(
    total_perca_mensal=50000.0,
    total_diferenca_anual=600000.0,
    percentual_perda_anual=15.5,
    total_recebido=350000.0
)

# Teste 3: Nome longo
municipio_nome = "Francisco Sá de Oliveira dos Santos"
uf = "MG"
```