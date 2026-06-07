"""SIAPS — cliente CLI da API pública apisiaps.saude.gov.br.

Baixa a classificação final das equipes da APS no Cofinanciamento — componentes
CVAT (Vínculo e Acompanhamento Territorial) e QUALIDADE — por município e
quadrimestre, e persiste como JSON em data/SIAPS/<ibge6>/<periodo>.json.

Fluxo (REST, sem JSF):
  1. GET  /api/public/filtros/competencias  → valida o(s) quadrimestre(s) pedido(s).
  2. GET  /uf/<UF>/municipios               → resolve o nome do município (best-effort).
  3. POST /api/public/componente/indicador-quadrimestre/filtro
     body {"uf":[UF], "nuQuadrimestre":[...], "coMunicipioIbge":[ibge6]}
     → {"classificacaoFinalComponente": [ ...registros... ]}
"""

from __future__ import annotations

import argparse
import datetime
import json
import logging
import pathlib
import re
import sys
import time
from typing import List, Optional

import requests

try:
    from .config import (
        DEFAULT_HEADERS,
        DEFAULT_OUTPUT_BASE,
        DEFAULT_TIMEOUT,
        RETRY_BACKOFF_BASE,
        RETRY_MAX_ATTEMPTS,
        UF_BY_IBGE_PREFIX,
        URL_COMPETENCIAS,
        URL_FILTRO,
        URL_MUNICIPIOS,
    )
except ImportError:
    from config import (  # type: ignore[no-redef]
        DEFAULT_HEADERS,
        DEFAULT_OUTPUT_BASE,
        DEFAULT_TIMEOUT,
        RETRY_BACKOFF_BASE,
        RETRY_MAX_ATTEMPTS,
        UF_BY_IBGE_PREFIX,
        URL_COMPETENCIAS,
        URL_FILTRO,
        URL_MUNICIPIOS,
    )


logger = logging.getLogger("SIAPS")

_QUAD_RE = re.compile(r"^(\d{4})Q([1-3])$")


# --- Validadores ---------------------------------------------------------------

def _validar_ibge(valor: str) -> None:
    if not (valor.isdigit() and len(valor) in (6, 7)):
        raise ValueError(
            f"--ibge deve ter 6 ou 7 dígitos numéricos (ex.: 260040 = Água Preta/PE). "
            f"Recebido: {valor!r}"
        )


def _validar_quadrimestre(valor: str) -> None:
    if not _QUAD_RE.match(valor):
        raise ValueError(
            f"quadrimestre deve estar no formato AAAAQN (N=1..3, ex.: 2025Q1). "
            f"Recebido: {valor!r}"
        )


def _validar_competencia(valor: str, nome: str) -> None:
    if not (valor.isdigit() and len(valor) == 6):
        raise ValueError(
            f"{nome} deve estar no formato AAAAMM (6 dígitos). Recebido: {valor!r}"
        )
    mes = int(valor[4:])
    if not 1 <= mes <= 12:
        raise ValueError(f"{nome}: mês inválido em {valor!r}")


# --- Período: AAAAMM ↔ quadrimestre --------------------------------------------

def _comp_para_quadrimestre(comp: str) -> str:
    """AAAAMM → 'AAAAQN'. Meses 01–04→Q1, 05–08→Q2, 09–12→Q3."""
    ano = comp[:4]
    mes = int(comp[4:])
    q = (mes - 1) // 4 + 1
    return f"{ano}Q{q}"


def _mapear_competencias(comp_inicial: str, comp_final: str) -> List[str]:
    """Lista única e ordenada de quadrimestres que intersectam [comp_inicial, comp_final]."""
    _validar_competencia(comp_inicial, "--comp-inicial")
    _validar_competencia(comp_final, "--comp-final")
    if comp_inicial > comp_final:
        raise ValueError("--comp-inicial não pode ser posterior a --comp-final")

    def _ordinal(quad: str) -> int:
        ano, q = int(quad[:4]), int(quad[5:])
        return ano * 3 + (q - 1)

    ini = _comp_para_quadrimestre(comp_inicial)
    fim = _comp_para_quadrimestre(comp_final)
    quadrimestres = []
    for o in range(_ordinal(ini), _ordinal(fim) + 1):
        ano, q = divmod(o, 3)
        quadrimestres.append(f"{ano}Q{q + 1}")
    return quadrimestres


# --- HTTP ----------------------------------------------------------------------

def _ibge_para_uf(ibge: str) -> str:
    prefix = ibge[:2]
    uf = UF_BY_IBGE_PREFIX.get(prefix)
    if uf is None:
        raise ValueError(f"prefixo IBGE {prefix!r} não mapeia para uma UF conhecida")
    return uf


def _session() -> requests.Session:
    s = requests.Session()
    s.headers.update(DEFAULT_HEADERS)
    return s


def _get_quadrimestres_validos(session: requests.Session, timeout: int) -> set[str]:
    """Conjunto de nuCompetencia que são quadrimestres (quadrimestre=true)."""
    r = session.get(URL_COMPETENCIAS, timeout=timeout)
    r.raise_for_status()
    dados = r.json()
    return {
        item["nuCompetencia"]
        for item in dados
        if isinstance(item, dict) and item.get("quadrimestre")
    }


def _resolver_municipio(
    session: requests.Session, uf: str, ibge6: str, timeout: int
) -> Optional[str]:
    """Nome do município a partir do IBGE (best-effort — None se indisponível)."""
    try:
        r = session.get(URL_MUNICIPIOS.format(uf=uf), timeout=timeout)
        r.raise_for_status()
        for m in r.json():
            if isinstance(m, dict) and m.get("coMunicipioIbge") == ibge6:
                return m.get("noMunicipio")
    except (requests.RequestException, ValueError) as exc:
        logger.warning("não foi possível resolver o nome do município: %s", exc)
    return None


def _post_filtro_com_retry(
    session: requests.Session, body: dict, timeout: int
) -> List[dict]:
    last_exc: Optional[Exception] = None
    for tentativa in range(1, RETRY_MAX_ATTEMPTS + 1):
        try:
            logger.info("POST %s (tentativa %d/%d)", URL_FILTRO, tentativa, RETRY_MAX_ATTEMPTS)
            logger.debug("body=%s", body)
            r = session.post(URL_FILTRO, json=body, timeout=timeout)
            logger.info("HTTP %s", r.status_code)
            if r.status_code == 429:
                espera = int(r.headers.get("Retry-After", RETRY_BACKOFF_BASE * tentativa))
                logger.warning("rate limit; aguardando %ds antes de re-tentar", espera)
                time.sleep(espera)
                continue
            if 500 <= r.status_code < 600 and tentativa < RETRY_MAX_ATTEMPTS:
                espera = RETRY_BACKOFF_BASE * tentativa
                logger.warning("erro %s no servidor; backoff %ds", r.status_code, espera)
                time.sleep(espera)
                continue
            r.raise_for_status()
            payload = r.json()
            if not isinstance(payload, dict):
                raise RuntimeError(
                    f"resposta da API não é um objeto JSON: {type(payload).__name__}"
                )
            return payload.get("classificacaoFinalComponente") or []
        except (requests.ConnectionError, requests.Timeout) as exc:
            last_exc = exc
            if tentativa < RETRY_MAX_ATTEMPTS:
                espera = RETRY_BACKOFF_BASE * tentativa
                logger.warning("falha de rede (%s); backoff %ds", exc, espera)
                time.sleep(espera)
                continue
            raise
    raise RuntimeError(f"esgotadas {RETRY_MAX_ATTEMPTS} tentativas") from last_exc


# --- Orquestração --------------------------------------------------------------

def baixar_siaps(
    ibge: str,
    quadrimestres: Optional[List[str]] = None,
    comp_inicial: Optional[str] = None,
    comp_final: Optional[str] = None,
    uf: Optional[str] = None,
    output_dir: Optional[str] = None,
    timeout: int = DEFAULT_TIMEOUT,
) -> pathlib.Path:
    """Baixa a classificação final (CVAT + Qualidade) de um município por quadrimestre."""
    _validar_ibge(ibge)
    ibge6 = ibge[:6]

    # Resolve o período: quadrimestres explícitos, ou mapeados de comp-inicial/final.
    if quadrimestres:
        quads = list(quadrimestres)
    elif comp_inicial and comp_final:
        quads = _mapear_competencias(comp_inicial, comp_final)
    else:
        raise ValueError(
            "informe --quadrimestre (ex.: 2025Q1,2025Q2) ou o par --comp-inicial/--comp-final"
        )
    for q in quads:
        _validar_quadrimestre(q)

    if uf is None:
        uf = _ibge_para_uf(ibge6)
    uf = uf.upper()

    if output_dir is None:
        output_dir = f"{DEFAULT_OUTPUT_BASE}/{ibge6}"
    destino_dir = pathlib.Path(output_dir)
    destino_dir.mkdir(parents=True, exist_ok=True)
    arquivo_final = destino_dir / f"{'_'.join(quads)}.json"

    session = _session()

    # Valida os quadrimestres pedidos contra os disponíveis na API.
    disponiveis = _get_quadrimestres_validos(session, timeout=timeout)
    ausentes = [q for q in quads if q not in disponiveis]
    if ausentes:
        raise RuntimeError(
            f"quadrimestre(s) indisponível(is) no SIAPS: {', '.join(ausentes)}. "
            f"Disponíveis: {', '.join(sorted(disponiveis))}"
        )

    municipio = _resolver_municipio(session, uf, ibge6, timeout=timeout)

    body = {"uf": [uf], "nuQuadrimestre": quads, "coMunicipioIbge": [ibge6]}
    registros = _post_filtro_com_retry(session, body, timeout=timeout)
    if not registros:
        raise RuntimeError(
            f"resposta sem dados para ibge={ibge6} uf={uf} quadrimestres={quads}"
        )

    payload = {
        "ibge": ibge6,
        "uf": uf,
        "municipio": municipio,
        "quadrimestres": quads,
        "fonte": URL_FILTRO,
        "extraido_em": datetime.date.today().isoformat(),
        "total_registros": len(registros),
        "registros": registros,
    }
    arquivo_final.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    logger.info(
        "Arquivo salvo: %s (%d bytes, %d registros em %d quadrimestre(s))",
        arquivo_final,
        arquivo_final.stat().st_size,
        len(registros),
        len(quads),
    )
    return arquivo_final


# --- CLI -----------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="SIAPS",
        description=(
            "Baixa a classificação final das equipes da APS no Cofinanciamento "
            "(CVAT + Qualidade) por município e quadrimestre, do portal SIAPS."
        ),
    )
    parser.add_argument(
        "--ibge",
        required=True,
        help="Código IBGE de 6 ou 7 dígitos do município (ex.: 260040 = Água Preta/PE).",
    )
    parser.add_argument(
        "--quadrimestre",
        default=None,
        help="Quadrimestre(s) AAAAQN separados por vírgula (ex.: 2025Q1,2025Q2,2025Q3).",
    )
    parser.add_argument(
        "--comp-inicial",
        default=None,
        help="Competência inicial AAAAMM (alternativa a --quadrimestre; é mapeada para quadrimestres).",
    )
    parser.add_argument(
        "--comp-final",
        default=None,
        help="Competência final AAAAMM (use junto com --comp-inicial).",
    )
    parser.add_argument(
        "--uf",
        default=None,
        help="Sigla UF (2 letras). Se omitido, deriva do prefixo IBGE.",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help=f"Diretório de saída (padrão: {DEFAULT_OUTPUT_BASE}/<ibge6>/).",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT,
        help=f"Timeout HTTP em segundos (padrão: {DEFAULT_TIMEOUT}).",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Log em DEBUG.")
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        stream=sys.stderr,
    )

    quadrimestres = None
    if args.quadrimestre:
        quadrimestres = [q.strip() for q in args.quadrimestre.split(",") if q.strip()]

    try:
        caminho = baixar_siaps(
            ibge=args.ibge,
            quadrimestres=quadrimestres,
            comp_inicial=args.comp_inicial,
            comp_final=args.comp_final,
            uf=args.uf,
            output_dir=args.output_dir,
            timeout=args.timeout,
        )
    except ValueError as exc:
        logger.error("Argumento inválido: %s", exc)
        return 2
    except requests.HTTPError as exc:
        sc = exc.response.status_code if exc.response is not None else "?"
        logger.error("Falha HTTP %s: %s", sc, exc)
        return 3
    except RuntimeError as exc:
        logger.error("Falha de negócio: %s", exc)
        return 3
    except requests.RequestException as exc:
        logger.error("Falha de rede: %s", exc)
        return 4
    except Exception as exc:  # noqa: BLE001
        logger.exception("Erro inesperado: %s", exc)
        return 1

    print(caminho)
    return 0


if __name__ == "__main__":
    sys.exit(main())
