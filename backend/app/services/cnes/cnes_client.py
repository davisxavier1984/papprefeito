"""
Cliente da API do CNES web (cnes.datasus.gov.br/services).

Fonte primária de dados de profissionais e equipes do município. Reflete o
estado corrente do SCNES — não há noção de competência.

Atenção: a API exige o header Referer da página de consulta; sem ele o servidor
responde "Your connection was refused".

Origem: maisprofissionais/cnes_utils.py (adaptado de requests para httpx).
"""

import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import httpx

logger = logging.getLogger(__name__)

BASE_URL = "https://cnes.datasus.gov.br/services"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://cnes.datasus.gov.br/pages/estabelecimentos/consulta.jsp",
    "Accept": "application/json",
}

# Concorrência moderada: são ~2 requisições por estabelecimento e não queremos
# ser bloqueados pelo servidor do DATASUS.
MAX_WORKERS = 8

# Retry para instabilidade do DATASUS (equivalente ao Retry do urllib3 no original)
TENTATIVAS = 3
BACKOFF = 2
STATUS_RETRY = {500, 502, 503, 504}


def _criar_session():
    """Cria cliente HTTP com os headers exigidos pelo CNES."""
    limits = httpx.Limits(max_connections=MAX_WORKERS * 2)
    return httpx.Client(headers=HEADERS, timeout=60, limits=limits,
                        transport=httpx.HTTPTransport(retries=TENTATIVAS, limits=limits))


def fmt_cbo(cbo: str) -> str:
    """Converte CBO da API ('251605') para o formato da Portaria ('2516-05')."""
    if not cbo:
        return ''
    cbo = str(cbo).strip()
    if '-' in cbo:
        return cbo
    if len(cbo) == 6 and cbo.isdigit():
        return f"{cbo[:4]}-{cbo[4:]}"
    return cbo


def ibge6(codigo_ibge: str) -> str:
    """Reduz o código IBGE de 7 dígitos para os 6 usados pelo CNES."""
    return str(codigo_ibge).strip()[:6]


def _get_json(session, path):
    for tentativa in range(TENTATIVAS + 1):
        r = session.get(f"{BASE_URL}/{path}")
        if r.status_code in STATUS_RETRY and tentativa < TENTATIVAS:
            time.sleep(BACKOFF * (2 ** tentativa))
            continue
        r.raise_for_status()
        return r.json()


def listar_estabelecimentos(codigo_ibge: str, session=None):
    """Lista os estabelecimentos do município (código IBGE de 6 ou 7 dígitos)."""
    session = session or _criar_session()
    return _get_json(session, f"estabelecimentos?municipio={ibge6(codigo_ibge)}")


def listar_profissionais(estab_id: str, session=None):
    """Lista os profissionais de um estabelecimento (id = IBGE6 + CNES7)."""
    session = session or _criar_session()
    return _get_json(session, f"estabelecimentos-profissionais/{estab_id}")


def listar_equipes(estab_id: str, session=None):
    """Lista as equipes de um estabelecimento (id = IBGE6 + CNES7)."""
    session = session or _criar_session()
    return _get_json(session, f"estabelecimentos-equipes/{estab_id}")


def ch_total(prof: dict) -> int:
    """Carga horária semanal total do vínculo (ambulatorial + hospitalar + outros)."""
    return sum(int(prof.get(k) or 0) for k in ('chAmb', 'chHosp', 'chOutros'))


def coletar_municipio(codigo_ibge: str, apenas_sus=True, progresso=None) -> dict:
    """
    Coleta estabelecimentos, profissionais e equipes de um município.

    Args:
        codigo_ibge: código IBGE do município (6 ou 7 dígitos)
        apenas_sus: se True, consulta apenas unidades com atendeSus == 'S'
        progresso: callable(feitos, total) para feedback de UI

    Returns:
        dict com 'estabelecimentos', 'profissionais' e 'equipes'.
        Cada profissional/equipe carrega 'estab_id' e 'estab_nome'.
    """
    with _criar_session() as session:
        estabs = listar_estabelecimentos(codigo_ibge, session)

        alvos = [e for e in estabs if not apenas_sus or e.get('atendeSus') == 'S']
        logger.info("Município %s: %d estabelecimentos (%d consultados)",
                    codigo_ibge, len(estabs), len(alvos))

        profissionais, equipes = [], []
        total = len(alvos)
        feitos = 0

        def _coletar(estab):
            eid = estab['id']
            return estab, listar_profissionais(eid, session), listar_equipes(eid, session)

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
            futuros = [pool.submit(_coletar, e) for e in alvos]
            for fut in as_completed(futuros):
                feitos += 1
                if progresso:
                    progresso(feitos, total)
                try:
                    estab, profs, eqs = fut.result()
                except Exception as e:
                    logger.warning("Falha ao coletar estabelecimento: %s", e)
                    continue
                for p in profs:
                    p['estab_id'] = estab['id']
                    p['estab_nome'] = estab.get('noFantasia', '')
                    p['cbo_fmt'] = fmt_cbo(p.get('cbo'))
                    p['ch_total'] = ch_total(p)
                    profissionais.append(p)
                for q in eqs:
                    q['estab_id'] = estab['id']
                    q['estab_nome'] = estab.get('noFantasia', '')
                    equipes.append(q)

    return {
        'estabelecimentos': estabs,
        'profissionais': profissionais,
        'equipes': equipes,
    }


# Siglas de equipe que contam para a faixa de vinculação da eMulti.
# A comparação é por sigla, não por texto livre: "EAPP - EQUIPE DE ATENCAO
# PRIMARIA PRISIONAL" contém "ATENCAO PRIMARIA" mas não é eSF/eAP.
SIGLAS_APS = {'ESF', 'EAP'}
SIGLA_EMULTI = 'EMULTI'


def sigla_equipe(equipe: dict) -> str:
    """Extrai a sigla do início de dsEquipe ('ESF - EQUIPE DE...' -> 'ESF')."""
    ds = (equipe.get('dsEquipe') or '').strip()
    return ds.split('-')[0].strip().upper()


def _ativa(equipe: dict) -> bool:
    return not (equipe.get('dtDesativacao') or '').strip()


def contar_equipes_aps(equipes) -> int:
    """Conta equipes ativas de eSF/eAP — a faixa que define a modalidade eMulti."""
    return sum(1 for q in equipes if _ativa(q) and sigla_equipe(q) in SIGLAS_APS)


def listar_emulti(equipes):
    """Equipes eMulti ativas já cadastradas no município."""
    return [q for q in equipes if _ativa(q) and sigla_equipe(q) == SIGLA_EMULTI]
