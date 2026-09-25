"""Configuração do módulo SIAPS — cliente da API pública apisiaps.saude.gov.br.

Fonte: portal SIAPS (Relatórios Públicos da APS), https://siaps.saude.gov.br/publico —
SPA Angular sustentada pela API REST pública abaixo. Sem JSF/ViewState.
"""

from __future__ import annotations

BASE_URL = "https://apisiaps.saude.gov.br"

# Lista de competências/quadrimestres disponíveis (valida o período pedido).
URL_COMPETENCIAS = f"{BASE_URL}/api/public/filtros/competencias"

# Municípios de uma UF (resolve nome do município a partir do IBGE). {uf} = sigla.
URL_MUNICIPIOS = f"{BASE_URL}/uf/{{uf}}/municipios"

# Dado principal: classificação final das equipes nos componentes CVAT e QUALIDADE.
URL_FILTRO = f"{BASE_URL}/api/public/componente/indicador-quadrimestre/filtro"

DEFAULT_OUTPUT_BASE = "data/SIAPS"
DEFAULT_TIMEOUT = 60

RETRY_MAX_ATTEMPTS = 3
RETRY_BACKOFF_BASE = 5

# A API valida a origem via CORS — Origin/Referer do portal são obrigatórios.
DEFAULT_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
    "Origin": "https://siaps.saude.gov.br",
    "Referer": "https://siaps.saude.gov.br/",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/137.0.0.0 Safari/537.36"
    ),
}

# Prefixo IBGE (2 díg.) → sigla UF. Copiado de ProdSIA/config.py para manter o
# módulo autocontido (convenção do repo: cada downloader é independente).
UF_BY_IBGE_PREFIX = {
    "11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO",
    "21": "MA", "22": "PI", "23": "CE", "24": "RN", "25": "PB", "26": "PE", "27": "AL",
    "28": "SE", "29": "BA",
    "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
    "41": "PR", "42": "SC", "43": "RS",
    "50": "MS", "51": "MT", "52": "GO", "53": "DF",
}
