# papprefeito Brownfield Architecture Document

## Introduction

This document captures the CURRENT STATE of the papprefeito codebase, including technical debt, workarounds, and real-world patterns. It serves as a reference for AI agents working on enhancements.

### Document Scope

Comprehensive documentation of entire system.

### Change Log

| Date   | Version | Description                 | Author    |
| ------ | ------- | --------------------------- | --------- |
| 2025-09-07 | 1.0     | Initial brownfield analysis | Analyst   |

## Quick Reference - Key Files and Entry Points

### Critical Files for Understanding the System

- **Main Entry**: `consulta_dados.py` (Streamlit application)
- **Configuration**: `config.json`
- **Core Business Logic**: `utils.py`, `api_client.py`
- **API Definitions**: The application communicates with an external API at `https://relatorioaps-prd.saude.gov.br/financiamento/pagamento`
- **Data Formatting**: `formatting.py`

## High Level Architecture

### Technical Summary

`papprefeito` is a Python-based web application that provides a financial analysis report for Brazilian municipalities based on data from the Ministry of Health's primary care funding. The application is built with Streamlit and uses the Plotly library for data visualization. Its main purpose is to show the financial advantages of improving the quality of primary care services, likely to promote the services of "Mais Gestor".

### Actual Tech Stack (from requirements.txt)

| Category  | Technology | Version | Notes                      |
| --------- | ---------- | ------- | -------------------------- |
| Web Framework   | Streamlit  | >= 1.0    | For the user interface          |
| Data Manipulation | pandas    | >= 2.0.0  | For data handling       |
| HTTP Requests | requests | >= 2.31.0      | For API communication |
| HTTP Adapters | urllib3 | >= 2.0.0      | For retry mechanisms |
| Brazilian Geodata | pyUFbr | >= 2.0.0      | For state and city data |

### Repository Structure Reality Check

- Type: Monorepo
- Package Manager: pip
- Notable: The project uses a `.bmad-core` directory, indicating the use of the BMad agent framework.

## Source Tree and Module Organization

### Project Structure (Actual)

```text
papprefeito/
├── __init__.py              # Initialization file
├── .gitignore               # Git ignore file
├── Alcobaça.pdf             # Example PDF report
├── api_client.py            # Robust API client with retries and caching
├── config.json              # Configuration file
├── consulta_dados.py        # Main Streamlit application file
├── dev.md                   # Developer notes
├── formatting.py            # Data formatting utilities
├── plan.txt                 # Plan file
├── README.md                # Project documentation
├── requirements.txt         # Python dependencies
├── timeline.md              # Timeline file
├── utils.py                 # Utility module combining formatting and API calls
├── .bmad-core/              # BMad agent framework files
└── docs/                    # Documentation folder
```

### Key Modules and Their Purpose

- **`consulta_dados.py`**: The main application entry point. It defines the Streamlit UI, handles user input, and orchestrates calls to other modules to fetch, process, and display data.
- **`api_client.py`**: Contains the `APIClient` class responsible for making requests to the external API. It includes features like session management, retry logic, and data caching to a local JSON file (`data_cache_papprefeito.json`).
- **`formatting.py`**: A utility module with functions to format numbers into Brazilian currency, parse currency strings, and format percentages.
- **`utils.py`**: A module that aggregates functions from `api_client.py` and `formatting.py` for easy access. It also contains the core business logic for calculating financial projections based on different quality scenarios.

## Data Models and APIs

### Data Models

The application does not use a traditional database. It fetches data from an external API and processes it in memory using pandas DataFrames. The data is cached locally in `data_cache_papprefeito.json`.

### API Specifications

The application interacts with a single external API endpoint:

- **Endpoint**: `https://relatorioaps-prd.saude.gov.br/financiamento/pagamento`
- **Method**: GET
- **Parameters**:
    - `unidadeGeografica`: "MUNICIPIO"
    - `coUf`: State code
    - `coMunicipio`: Municipality IBGE code
    - `nuParcelaInicio`: Start competence (YYYYMM)
    - `nuParcelaFim`: End competence (YYYYMM)
    - `tipoRelatorio`: "COMPLETO"

## Technical Debt and Known Issues

### Critical Technical Debt

1.  **Lack of Automated Tests**: There are no automated tests in the project, which makes it hard to refactor or add new features without risking regressions.
2.  **Hardcoded Values**: The `utils.py` file contains hardcoded dictionaries (`VINCULO_VALUES`, `QUALITY_VALUES`) that represent the financial values for different quality classifications. These values might change over time and should be managed in a more flexible way (e.g., in the `config.json` file).
3.  **No Error Handling for `ufbr`**: The `consulta_dados.py` file has a `try-except` block for the `ufbr.get_cidade` call, but it just shows an error and returns. It could be more robust.

### Workarounds and Gotchas

- **Fallback Imports**: The `consulta_dados.py` file has a `try-except` block for imports, which suggests that the project might be run from different directories. This can make the project structure confusing.
- **Manual IBGE Code Slicing**: The IBGE code is manually sliced (`codigo_ibge[:-1]`) in `consulta_dados.py`. This is brittle and might fail for some cases.

## Integration Points and External Dependencies

### External Services

| Service  | Purpose  | Integration Type | Key Files                      |
| -------- | -------- | ---------------- | ------------------------------ |
| Ministério da Saúde | Health Financing Data | REST API         | `api_client.py`     |

### Internal Integration Points

- The application is self-contained and does not have internal integration points with other systems.

## Development and Deployment

### Local Development Setup

1.  Install Python and pip.
2.  Create a virtual environment.
3.  Install dependencies: `pip install -r requirements.txt`
4.  Run the application: `streamlit run consulta_dados.py`

### Build and Deployment Process

- The `README.md` file does not specify a build or deployment process. The application is likely run directly from the source code in a server environment.

## Testing Reality

### Current Test Coverage

- There are no automated tests in the project.

### Running Tests

- Not applicable.
