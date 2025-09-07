# Sistema papprefeito - Informações de Desenvolvimento

## Estrutura Final Criada:

```
papprefeito/
├── consulta_dados.py     # Interface principal com Streamlit
├── api_client.py         # Cliente robusto para API
├── formatting.py         # Formatação de moeda e números  
├── utils.py              # Módulo utilitário unificado
├── __init__.py          # Inicialização do módulo
├── requirements.txt      # Dependências específicas
└── README.md            # Documentação completa
```

## Funcionalidades Incluídas:

✅ **Consulta à API** - Cliente robusto com retry e tratamento de erros  
✅ **Interface Streamlit** - Seleção por UF/município e competência  
✅ **Formatação de dados** - Valores monetários em formato brasileiro  
✅ **Cache independente** - Arquivo `data_cache_papprefeito.json`  
✅ **Documentação** - README com instruções de uso  

## Sistema Independente

O sistema papprefeito foi criado como uma cópia independente do sistema de consulta de dados original (`pages/00_Consulta_Dados.py`) com todas as funcionalidades necessárias:

### Características:
- **Totalmente autônomo** - Não depende de outros módulos do projeto principal
- **Cache próprio** - Utiliza arquivo separado para evitar conflitos
- **Dependências mínimas** - Apenas as bibliotecas essenciais
- **API robusta** - Cliente com tratamento completo de erros e retry
- **Formatação brasileira** - Moeda e números no padrão nacional

### Funcionalidades do Sistema:
1. **Consulta à API de Financiamento da Saúde**
   - Endpoint: https://relatorioaps-prd.saude.gov.br/financiamento/pagamento
   - Parâmetros: UF, Município (código IBGE), Competência (AAAAMM)
   - Relatório completo de financiamento

2. **Interface Web com Streamlit**
   - Seleção de Estado via pyUFbr
   - Seleção de Município baseada no Estado
   - Input de competência no formato AAAAMM
   - Botão de consulta com feedback visual

3. **Exibição de Dados**
   - Resumos dos Planos Orçamentários
   - Dados de Pagamentos das ESF
   - Informações extraídas: IED, Classificações
   - Formatação automática de valores monetários

4. **Gerenciamento de Estado**
   - Session state do Streamlit para persistir dados
   - Cache local em JSON para reutilização
   - Validação de dados da API

## Instruções de Uso:

```bash
# Navegar para a pasta
cd papprefeito

# Instalar dependências
pip install -r requirements.txt

# Executar o sistema
streamlit run consulta_dados.py
```

## Arquivos Criados:

### 1. consulta_dados.py
- Interface principal baseada no arquivo original
- Adaptação das importações para módulos locais
- Mantém toda funcionalidade de consulta e exibição

### 2. api_client.py
- Cliente HTTP robusto com requests
- Estratégia de retry para requisições
- Validação de dados da API
- Progress bar e feedback visual
- Cache em arquivo JSON separado

### 3. formatting.py
- Formatação de moeda brasileira
- Conversão de strings monetárias para float
- Formatação de porcentagens e números
- Validação de inputs numéricos

### 4. utils.py
- Módulo unificador das funcionalidades
- Importa e exporta funções de formatting e api_client
- Interface compatível com o sistema original

### 5. requirements.txt
- streamlit>=1.28.0
- pandas>=2.0.0
- requests>=2.31.0
- pyUFbr>=2.0.0
- urllib3>=2.0.0

### 6. __init__.py
- Inicialização do módulo Python
- Exportação das funções principais
- Informações de versão

### 7. README.md
- Documentação completa do sistema
- Instruções de instalação e uso
- Descrição das funcionalidades
- Informações sobre a API utilizada

## Data de Criação: 2025-09-05

Este sistema foi desenvolvido como uma versão independente e portável do módulo de consulta de dados de financiamento da saúde, mantendo todas as funcionalidades essenciais em uma estrutura autônoma.