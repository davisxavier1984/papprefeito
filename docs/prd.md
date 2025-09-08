# PRD: Relatório Financeiro da APS para Prefeitos

## 1. Visão Geral

Este documento descreve os requisitos para a funcionalidade de geração de relatórios em PDF no sistema `papprefeito`. O objetivo principal é criar um relatório financeiro personalizado para os prefeitos, demonstrando o valor dos serviços da "Mais Gestor" através da análise de dados de financiamento da saúde.

## 2. Público-alvo

- **Prefeitos**: O principal público do relatório.
- **Secretários de Finanças e Saúde**: Usuários secundários que podem usar o relatório para análise e planejamento.

## 3. Funcionalidades

### 3.1. Geração de Relatório em PDF

O sistema deve ser capaz de gerar um relatório em PDF com base nos dados consultados para um determinado município.

### 3.2. Estrutura do Relatório

O relatório em PDF deve seguir a estrutura do arquivo `Alcobaça.pdf`, contendo as seguintes seções:

1.  **Logo da Mais Gestor**: A logo da "Mais Gestor" (`logo_colorida_mg.png`) deve ser exibida no topo do relatório.
2.  **Cabeçalho**: Título "Relatório de Projeção Financeira – Município de [Nome do Município]".
3.  **Introdução**: Texto de apresentação padrão, o mesmo do `Alcobaça.pdf`.
4.  **Cenário Atual**: O valor correspondente à classificação "Bom" da função `criar_tabela_total_por_classificacao`.
5.  **Classificação por Cenários**: Uma tabela com os valores para os cenários "Regular", "Suficiente", "Bom" e "Ótimo", obtidos da função `criar_tabela_total_por_classificacao`.
6.  **Projeções de Crescimento**: Uma lista com a projeção de crescimento para 12 meses, calculada com base na lógica da função `criar_grafico_piramide_mensal`.
7.  **Considerações Finais**: Texto de encerramento padrão, o mesmo do `Alcobaça.pdf`.
8.  **Assinatura**: "Atenciosamente, Mais Gestor, Alysson Ribeiro".

### 3.3. Manter Funcionalidades Existentes

As funcionalidades existentes da interface Streamlit (consulta de dados, gráficos e tabelas) devem ser mantidas.

## 4. Requisitos Não Funcionais

- O relatório em PDF deve ser gerado de forma rápida e eficiente.
- O layout do PDF deve ser profissional e de fácil leitura, semelhante ao `Alcobaça.pdf`.

## 5. Métricas de Sucesso

- Aumento no número de prefeitos que entram em contato com a "Mais Gestor" após receberem o relatório.
- Feedback positivo dos usuários sobre a clareza e utilidade do relatório.
