# Sistema papprefeito - Consulta e Edição de Dados APS

Sistema simplificado para consulta e edição de dados de financiamento da saúde do Ministério da Saúde.

## 🎯 Funcionalidades

- ✅ Consulta à API de financiamento da saúde
- ✅ Seleção por UF, município e competência
- ✅ Visualização em tabela editável
- ✅ Edição inline dos valores financeiros
- ✅ Sistema CRUD para salvar municípios editados
- ✅ Cache local dos dados consultados

## 🚀 Como Usar

### 1. Instalação
```bash
pip install -r requirements.txt
```

### 2. Execução
```bash
streamlit run app.py
```

### 3. Interface
1. Selecione a UF no sidebar
2. Selecione o município
3. Informe a competência (AAAAMM)
4. Clique em "Consultar"
5. Edite os valores na tabela conforme necessário
6. Salve as edições usando o botão "Salvar Edições"

## 📊 Dados Exibidos

- **Plano Orçamentário**: Tipo do componente
- **Esfera Administrativa**: Esfera responsável
- **Valores**: Integral, Ajuste, Desconto, Efetivo, Implantação

## 💾 Sistema de Persistência

- **Cache de API**: `data_cache_papprefeito.json`
- **Dados Editados**: `municipios_editados.json`

## 🔧 API Utilizada

- **Endpoint**: https://relatorioaps-prd.saude.gov.br/financiamento/pagamento
- **Fonte**: Ministério da Saúde
- **Tipo**: Relatório Completo de Financiamento