# Checklist de Implementação - Sistema de Relatórios PDF Expandido

**Responsável:** [Developer]
**Revisor:** John (PM)
**Data limite:** [A definir]

---

## 📋 FASE 1: PREPARAÇÃO

### Análise do Código Existente:
- [ ] Estudar função `create_pdf_report` atual
- [ ] Entender estrutura do `ResumoFinanceiro`
- [ ] Identificar funções auxiliares disponíveis (`_br_number`, `_sanitize_text`)
- [ ] Mapear fluxo de dados do endpoint até PDF

### Setup do Ambiente:
- [ ] Backup da versão atual
- [ ] Criar branch específica para desenvolvimento
- [ ] Configurar ambiente de teste local
- [ ] Preparar dados de teste diversos

---

## 📋 FASE 2: DESENVOLVIMENTO

### Refatoração da Estrutura Principal:
- [ ] Criar função `_create_page_1_intro_destaque()`
- [ ] Criar função `_create_page_2_infograficos()`
- [ ] Criar função `_create_page_3_impacto_conclusao()`
- [ ] Refatorar `create_pdf_report()` para usar novas funções

### Implementação Página 1:
- [ ] Cabeçalho dinâmico com município/UF
- [ ] Saudação formal ao prefeito
- [ ] Texto introdutório estratégico
- [ ] Banner "QUANTO EU DEIXO DE RECEBER ANUALMENTE?"
- [ ] Percentual destacado em fonte grande
- [ ] Resumo financeiro com bullet points

### Implementação Página 2:
- [ ] Layout dividido horizontalmente (50%/50%)
- [ ] Seção superior: Comparativo anual
  - [ ] Títulos "Recurso Atenção Básica atual/potencial"
  - [ ] Valores numéricos em vermelho/azul
  - [ ] Gráfico de barras proporcional
  - [ ] Seta de crescimento azul
  - [ ] Eixo Y em milhões
- [ ] Seção inferior: Análise mensal
  - [ ] Título "Mensal"
  - [ ] Três valores com cores específicas
  - [ ] Frase sublinhada "Acréscimo Mensal de Receita"
  - [ ] Seta azul irregular apontando para cima

### Implementação Página 3:
- [ ] Seção superior: Percentual + símbolo + valor destacado
- [ ] Seção central: Mensagem motivacional
- [ ] Seção inferior: Considerações finais + assinatura

### Funções Auxiliares:
- [ ] `_draw_bar_chart()` para gráfico de barras
- [ ] `_draw_arrow()` para setas de crescimento
- [ ] `_calculate_annual_values()` para valores anualizados

---

## 📋 FASE 3: TESTES

### Testes Funcionais:
- [ ] Testar com valores pequenos (centenas)
- [ ] Testar com valores médios (milhares)
- [ ] Testar com valores grandes (milhões)
- [ ] Testar com nomes de município curtos
- [ ] Testar com nomes de município longos
- [ ] Testar com diferentes UFs

### Testes de Layout:
- [ ] Verificar proporções das barras no gráfico
- [ ] Validar alinhamento de elementos
- [ ] Confirmar quebra de texto adequada
- [ ] Testar em diferentes visualizadores PDF

### Testes de Cálculo:
- [ ] Validar consistência entre página 2 (anual) e página 2 (mensal)
- [ ] Verificar formatação brasileira de números
- [ ] Confirmar precisão matemática

### Testes de Integração:
- [ ] Testar endpoint `/relatorios/pdf` funcionando
- [ ] Verificar frontend gerando PDF corretamente
- [ ] Validar download de arquivo funcionando
- [ ] Confirmar nome do arquivo gerado

---

## 📋 FASE 4: VALIDAÇÃO

### Revisão de Código:
- [ ] Code review com foco em performance
- [ ] Verificação de padrões de código
- [ ] Validação de tratamento de erros
- [ ] Confirmação de documentação adequada

### Testes de Regressão:
- [ ] Sistema de consulta funcionando
- [ ] Edição de municípios funcionando
- [ ] Cache funcionando normalmente
- [ ] Outras funcionalidades inalteradas

### Aprovação Visual:
- [ ] Layout página 1 aprovado pelo PM
- [ ] Layout página 2 aprovado pelo PM
- [ ] Layout página 3 aprovado pelo PM
- [ ] Cores e fontes conforme especificação

---

## 📋 FASE 5: DEPLOY

### Preparação:
- [ ] Merge da branch para main
- [ ] Testes finais em ambiente de produção
- [ ] Backup da versão anterior
- [ ] Documentação de deployment atualizada

### Monitoramento:
- [ ] Verificar logs de erro
- [ ] Monitorar performance de geração
- [ ] Confirmar funcionamento em produção
- [ ] Coletar feedback inicial dos usuários