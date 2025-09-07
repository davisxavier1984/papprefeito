# Sistema papprefeito - Consulta de Dados

Sistema independente para consulta e visualização de dados de financiamento da saúde do Ministério da Saúde.

## Estrutura do Sistema

```
papprefeito/
├── consulta_dados.py          # Interface principal do sistema
├── api_client.py             # Cliente para API de financiamento
├── formatting.py             # Funções de formatação
├── utils.py                  # Módulo utilitário
├── requirements.txt          # Dependências do sistema
├── __init__.py              # Inicialização do módulo
└── README.md                # Documentação
```

## Funcionalidades

- ✅ Consulta à API de financiamento da saúde
- ✅ Seleção por UF e município
- ✅ Filtro por competência (AAAAMM)
- ✅ Exibição de resumos orçamentários
- ✅ Exibição de dados de pagamentos
- ✅ Formatação automática de valores monetários
- ✅ Cache local dos dados consultados
- ✅ Indicadores extraídos (IED, Classificações)

## Como Usar

### 1. Instalação das Dependências
```bash
cd papprefeito
pip install -r requirements.txt
```

### 2. Execução do Sistema
```bash
streamlit run consulta_dados.py
```

### 3. Uso da Interface
1. Selecione um Estado (UF)
2. Selecione um Município
3. Informe a Competência no formato AAAAMM (ex: 202501)
4. Clique em "Consultar"

## Dados Exibidos

### Resumos dos Planos Orçamentários
- Plano Orçamentário
- Esfera Administrativa  
- Valores: Integral, Ajuste, Desconto, Efetivo Repasse
- Valores de Implantação

### Dados de Pagamentos
- Faixa do Índice de Equidade (IED)
- Classificação de Vínculo
- Classificação de Qualidade
- Quantidade de ESF Credenciadas/Homologadas

## Informações Extraídas
- **IED**: Índice de Equidade em Saúde
- **Classificação Vínculo**: Avaliação do vínculo das equipes
- **Classificação Qualidade**: Avaliação da qualidade dos serviços

## Cache de Dados
Os dados consultados são salvos em `data_cache_papprefeito.json` para reutilização.

## API Utilizada
- **Endpoint**: https://relatorioaps-prd.saude.gov.br/financiamento/pagamento
- **Fonte**: Ministério da Saúde
- **Tipo**: Relatório Completo de Financiamento

## Dependências
- streamlit >= 1.28.0
- pandas >= 2.0.0  
- requests >= 2.31.0
- pyUFbr >= 2.0.0
- urllib3 >= 2.0.0