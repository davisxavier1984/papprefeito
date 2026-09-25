"""Cliente da API pública do SIAPS (classificação das equipes da APS).

Espelha o padrão de ``SaudeAPIClient`` (httpx async + cache em JSON). Baixa a
classificação final das equipes nos componentes CVAT e Qualidade, por município e
quadrimestre, e persiste em ``data/SIAPS/<ibge6>/<periodo>.json`` (mesmo esquema do
CLI ``SIAPS/``, de modo que backend e CLI compartilham o cache).

A lógica HTTP (validação de quadrimestre, resolução de nome, POST com retry/429) é
portada do CLI ``SIAPS/baixa_siaps.py`` para httpx assíncrono. Os helpers puros de
período vêm de ``app.core.siaps_reference`` (duplicados do pacote SIAPS por robustez
de deploy — ver teste anti-drift).
"""
from __future__ import annotations

import asyncio
import datetime
import json
import os
import pathlib
from typing import Any, Dict, List, Optional

import httpx

from app.core.config import settings
from app.core.siaps_reference import quadrimestre_aplicavel
from app.utils.logger import logger

# A API valida a origem via CORS — Origin/Referer do portal são obrigatórios.
_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
    "Origin": "https://siaps.saude.gov.br",
    "Referer": "https://siaps.saude.gov.br/",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
    ),
}

# Prefixo IBGE (2 díg.) → UF (duplicado do pacote SIAPS p/ robustez de deploy).
_UF_BY_IBGE_PREFIX = {
    "11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO",
    "21": "MA", "22": "PI", "23": "CE", "24": "RN", "25": "PB", "26": "PE", "27": "AL",
    "28": "SE", "29": "BA",
    "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
    "41": "PR", "42": "SC", "43": "RS",
    "50": "MS", "51": "MT", "52": "GO", "53": "DF",
}

_RETRY_MAX_ATTEMPTS = 3
_RETRY_BACKOFF_BASE = 5


class SiapsAPIClient:
    """Cliente para a API pública apisiaps.saude.gov.br."""

    def __init__(self):
        self.base_url = settings.SIAPS_BASE_URL
        self.timeout = settings.SIAPS_TIMEOUT
        self.cache_dir = settings.SIAPS_CACHE_DIR
        self.cache_ttl_days = settings.SIAPS_CACHE_TTL_DAYS

    # --- helpers ----------------------------------------------------------

    def _uf_de_ibge(self, ibge6: str) -> Optional[str]:
        return _UF_BY_IBGE_PREFIX.get(ibge6[:2])

    def _cache_path(self, ibge6: str, quadrimestres: List[str]) -> pathlib.Path:
        nome = "_".join(quadrimestres)
        return pathlib.Path(self.cache_dir) / ibge6 / f"{nome}.json"

    def _ler_cache(self, path: pathlib.Path) -> Optional[Dict[str, Any]]:
        if not path.exists():
            return None
        try:
            idade = datetime.date.today() - datetime.date.fromtimestamp(path.stat().st_mtime)
            if idade.days > self.cache_ttl_days:
                logger.info("SIAPS cache expirado (%d dias): %s", idade.days, path)
                return None
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            logger.warning("SIAPS: falha ao ler cache %s: %s", path, exc)
            return None

    # --- HTTP -------------------------------------------------------------

    async def _quadrimestres_validos(self, client: httpx.AsyncClient) -> set[str]:
        r = await client.get(f"{self.base_url}/api/public/filtros/competencias")
        r.raise_for_status()
        return {
            item["nuCompetencia"]
            for item in r.json()
            if isinstance(item, dict) and item.get("quadrimestre")
        }

    async def _resolver_municipio(
        self, client: httpx.AsyncClient, uf: str, ibge6: str
    ) -> Optional[str]:
        try:
            r = await client.get(f"{self.base_url}/uf/{uf}/municipios")
            r.raise_for_status()
            for m in r.json():
                if isinstance(m, dict) and m.get("coMunicipioIbge") == ibge6:
                    return m.get("noMunicipio")
        except (httpx.HTTPError, ValueError) as exc:
            logger.warning("SIAPS: não foi possível resolver o município: %s", exc)
        return None

    async def _post_filtro(
        self, client: httpx.AsyncClient, body: dict
    ) -> List[dict]:
        url = f"{self.base_url}/api/public/componente/indicador-quadrimestre/filtro"
        last_exc: Optional[Exception] = None
        for tentativa in range(1, _RETRY_MAX_ATTEMPTS + 1):
            try:
                r = await client.post(url, json=body)
                if r.status_code == 429:
                    espera = int(r.headers.get("Retry-After", _RETRY_BACKOFF_BASE * tentativa))
                    logger.warning("SIAPS rate limit; aguardando %ds", espera)
                    await asyncio.sleep(espera)
                    continue
                if 500 <= r.status_code < 600 and tentativa < _RETRY_MAX_ATTEMPTS:
                    await asyncio.sleep(_RETRY_BACKOFF_BASE * tentativa)
                    continue
                r.raise_for_status()
                payload = r.json()
                if not isinstance(payload, dict):
                    raise ValueError("resposta da API SIAPS não é objeto JSON")
                return payload.get("classificacaoFinalComponente") or []
            except (httpx.ConnectError, httpx.TimeoutException) as exc:
                last_exc = exc
                if tentativa < _RETRY_MAX_ATTEMPTS:
                    await asyncio.sleep(_RETRY_BACKOFF_BASE * tentativa)
                    continue
                raise
        raise RuntimeError(f"SIAPS: esgotadas {_RETRY_MAX_ATTEMPTS} tentativas") from last_exc

    # --- orquestração -----------------------------------------------------

    async def consultar_classificacao(
        self,
        codigo_ibge: str,
        quadrimestres: List[str],
        force_refresh: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """Classificação (CVAT + Qualidade) por município e quadrimestre(s).

        Retorna o envelope ``{ibge,uf,municipio,quadrimestres,registros[],...}`` ou
        ``None`` em caso de erro/sem dados.
        """
        if not codigo_ibge or len(codigo_ibge) < 6:
            logger.error("SIAPS: código IBGE inválido: %r", codigo_ibge)
            return None
        ibge6 = codigo_ibge[:6]
        uf = self._uf_de_ibge(ibge6)
        if uf is None:
            logger.error("SIAPS: prefixo IBGE %r não mapeia UF", ibge6[:2])
            return None

        quads = sorted(set(quadrimestres))
        cache_path = self._cache_path(ibge6, quads)
        if not force_refresh:
            cached = self._ler_cache(cache_path)
            if cached is not None:
                logger.info("SIAPS cache hit: %s", cache_path)
                return cached

        try:
            async with httpx.AsyncClient(timeout=self.timeout, headers=_HEADERS) as client:
                disponiveis = await self._quadrimestres_validos(client)
                ausentes = [q for q in quads if q not in disponiveis]
                if ausentes:
                    logger.warning(
                        "SIAPS: quadrimestre(s) indisponível(is): %s (disp.: %s)",
                        ", ".join(ausentes), ", ".join(sorted(disponiveis)),
                    )
                    return None

                municipio = await self._resolver_municipio(client, uf, ibge6)
                body = {"uf": [uf], "nuQuadrimestre": quads, "coMunicipioIbge": [ibge6]}
                registros = await self._post_filtro(client, body)
                if not registros:
                    logger.warning("SIAPS: sem registros para %s/%s", ibge6, quads)
                    return None

                envelope = {
                    "ibge": ibge6,
                    "uf": uf,
                    "municipio": municipio,
                    "quadrimestres": quads,
                    "fonte": f"{self.base_url}/api/public/componente/indicador-quadrimestre/filtro",
                    "extraido_em": datetime.date.today().isoformat(),
                    "total_registros": len(registros),
                    "registros": registros,
                }
                self._salvar_cache(cache_path, envelope)
                return envelope

        except httpx.HTTPStatusError as exc:
            logger.error("SIAPS: erro HTTP %s", exc.response.status_code)
            return None
        except (httpx.HTTPError, ValueError, RuntimeError) as exc:
            logger.error("SIAPS: falha na consulta: %s", exc)
            return None

    async def consultar_para_competencia(
        self,
        codigo_ibge: str,
        competencia: str,
        quadrimestre: Optional[str] = None,
        force_refresh: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """Como ``consultar_classificacao``, mas resolve o quadrimestre a partir da
        competência mensal (defasagem do pagamento), salvo override explícito."""
        quad = quadrimestre or quadrimestre_aplicavel(competencia)
        return await self.consultar_classificacao(codigo_ibge, [quad], force_refresh)

    def _salvar_cache(self, path: pathlib.Path, envelope: dict) -> None:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                json.dumps(envelope, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            logger.info("SIAPS cache salvo: %s", os.path.abspath(path))
        except OSError as exc:
            logger.warning("SIAPS: falha ao salvar cache %s: %s", path, exc)


# Instância global do cliente
siaps_api_client = SiapsAPIClient()
