---
description: Invoca subagente especializado em frontend para melhorar o visual do PDF detalhado
---

Invoque um subagente usando o Task tool com os seguintes parâmetros:

**subagent_type:** "general-purpose"

**description:** "Melhorar visual do PDF detalhado"

**prompt:**

```
Você é um subagente especializado em frontend e design de documentos PDF.

CONTEXTO:
- Projeto: Sistema de relatórios PDF de financiamento APS
- Template HTML: backend/templates/relatorio_detalhado.html
- Estilos CSS: backend/templates/css/modern-cards.css
- Script de teste: backend/test_pdf_detalhado.py
- Gerador: WeasyPrint (via backend/app/services/relatorio_pdf.py)

OBJETIVO:
Analise e melhore o visual do PDF, focando em:
1. Espaçamento e quebras de página - Evitar elementos cortados, otimizar uso de espaço
2. Tipografia - Tamanhos de fonte, legibilidade, hierarquia visual
3. Cores e contraste - Garantir leitura clara e destaque adequado (WCAG AA)
4. Layout e alinhamento - Grid, espaçamentos consistentes
5. Componentes visuais - Cards, tabelas, badges (aparência profissional)
6. Responsividade para PDF - Layout otimizado para formato A4
7. Consistência visual - Padrão uniforme em todas as páginas

PROCESSO:

1. ANÁLISE
   - Ler completamente backend/templates/relatorio_detalhado.html
   - Ler completamente backend/templates/css/modern-cards.css
   - Gerar PDF de teste: cd backend && python3 test_pdf_detalhado.py
   - Localizar o PDF gerado em /tmp/relatorio_detalhado_*.pdf

2. DIAGNÓSTICO
   Identificar problemas em:
   - Espaçamentos (padding, margin, gaps)
   - Tamanhos de fonte e line-height
   - Contraste de cores
   - Alinhamentos e distribuição
   - Bordas, sombras e decorações
   - Quebras de página inadequadas
   - Elementos que não cabem ou ficam cortados

3. IMPLEMENTAÇÃO
   Aplicar correções em:
   - backend/templates/css/modern-cards.css (ajustes de estilo)
   - backend/templates/relatorio_detalhado.html (ajustes pontuais se necessário)

   IMPORTANTE:
   - NÃO modificar lógica do backend ou estrutura de dados
   - MANTER placeholders: __SAUDE_FAMILIA_CONTENT__, __SAUDE_BUCAL_CONTENT__, __EMULTI_CONTENT__
   - FOCAR apenas em melhorias visuais (CSS/HTML)
   - Usar boas práticas CSS para impressão (@page, page-break-*, orphans, widows)

4. VALIDAÇÃO
   - Gerar novo PDF após mudanças
   - Comparar visualmente antes/depois
   - Verificar todas as 5 páginas do relatório

ENTREGA:
Forneça relatório final com:
1. Problemas Identificados (lista detalhada com localização)
2. Correções Implementadas (mudanças específicas feitas)
3. Localização do PDF (caminho do arquivo gerado)
4. Comparação Visual (principais melhorias alcançadas)
5. Recomendações (melhorias futuras, se houver)

Inicie a análise e implementação das melhorias visuais agora!
```
