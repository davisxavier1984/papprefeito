"""
Estimativa de eMulti a partir dos profissionais elegíveis do CNES (story 3.6).

Faz parte do preenchimento automático (story 3.3) e do cálculo dos relatórios em lote:
calcula quantas eMulti o município poderia ter; o usuário revisa junto com os outros planos.

Regra calibrada nos 85 municípios do histórico (docs/analises/regras-perda-ministerio.md):
    equipes = mín(eSF + eAP, profissionais elegíveis ÷ 6, nutricionistas + psicólogos)
    perda   = equipes × custeio da Estratégica − custeio atual
Sem carga horária, por decisão do usuário. O divisor fica nos valores de referência.
"""
import asyncio
import time
from typing import Any, Dict, List, Optional, Tuple

from app.models.schemas import EstimativaEmulti, ProfissionalElegivel
from app.services.api_client import saude_api_client
from app.services.cnes import cnes_client, emulti_regras
from app.services.regras_perda import Valores, filtrar_resumos_municipais, tipo_do_plano
from app.services.relatorios_service import DadosNaoEncontrados
from app.utils.logger import logger

MODALIDADES = ('estrategica', 'complementar', 'ampliada')
CNES_TTL_SEGUNDOS = 12 * 3600
NUTRI_PSI = ('2237-10', '2515-10')

_cache_cnes: Dict[str, Tuple[float, Dict[str, Any]]] = {}


async def coletar_cnes(codigo_ibge: str) -> Dict[str, Any]:
    """Coleta do CNES com cache em memória (a coleta de um município grande leva dezenas de segundos)."""
    ibge6 = cnes_client.ibge6(codigo_ibge)
    em_cache = _cache_cnes.get(ibge6)
    if em_cache and time.time() - em_cache[0] < CNES_TTL_SEGUNDOS:
        return em_cache[1]
    dados = await asyncio.to_thread(cnes_client.coletar_municipio, ibge6)
    _cache_cnes[ibge6] = (time.time(), dados)
    return dados


def _categorias() -> Dict[str, Tuple[str, bool]]:
    """cbo -> (categoria, está em alguma composição fixa), sem repetir categorias."""
    fixos = {cbo for m in emulti_regras.MODALIDADES.values() for g in m['fixas'] for _, cbo in g['opcoes']}
    cats: Dict[str, Tuple[str, bool]] = {}
    for m in emulti_regras.MODALIDADES.values():
        for g in m['fixas']:
            for nome, cbo in g['opcoes']:
                cats.setdefault(cbo, (nome, True))
    for nome, cbo in emulti_regras.VARIAVEIS:
        cats.setdefault(cbo, (nome, cbo in fixos))
    return cats


def _plano_emulti(dados: Dict[str, Any]) -> Tuple[Optional[int], Optional[str], List[str]]:
    nomes = [r.get('dsPlanoOrcamentario', '') for r in filtrar_resumos_municipais(dados.get('resumosPlanosOrcamentarios') or [])]
    for i, nome in enumerate(nomes):
        if tipo_do_plano(nome) == 'emulti':
            return i, nome, nomes
    return None, None, nomes


async def estimar(codigo_ibge: str, competencia: str, valores: Valores,
                  divisor: Optional[int] = None, dados: Optional[Dict[str, Any]] = None) -> EstimativaEmulti:
    """`dados` permite reaproveitar a resposta do Ministério já consultada."""
    if dados is None:
        dados = await saude_api_client.consultar_financiamento(codigo_ibge, competencia)
    if not dados or not dados.get('resumosPlanosOrcamentarios'):
        raise DadosNaoEncontrados("Sem dados de financiamento do Ministério para este município")
    p = (dados.get('pagamentos') or [{}])[0]
    n = lambda k: int(p.get(k) or 0)  # noqa: E731

    cnes = await coletar_cnes(codigo_ibge)
    indice = emulti_regras.construir_indice_cbo(emulti_regras.agregar_por_cbo(cnes.get('profissionais', [])))
    pessoas = {cbo: (len(item['cns']) or item['qtd']) for cbo, item in indice.items()}

    profissionais = [
        ProfissionalElegivel(categoria=nome, cbo=cbo, pessoas=pessoas[cbo], composicao_fixa=fixa)
        for cbo, (nome, fixa) in _categorias().items() if pessoas.get(cbo)
    ]
    profissionais.sort(key=lambda x: (-x.pessoas, x.categoria))
    total_elegiveis = sum(x.pessoas for x in profissionais)
    nutri_psi = sum(pessoas.get(c, 0) for c in NUTRI_PSI)

    equipes_aps = n('qtEsfCredenciado') + n('qtEapCredenciadas')
    div = divisor or int(valores['emulti_profissionais_por_equipe'][0])
    estimadas = max(min(equipes_aps, total_elegiveis // div, nutri_psi), 0)

    custeio = {m: float(valores[f'emulti_custeio_{m}'][0]) for m in MODALIDADES}
    combinacao = {'estrategica': estimadas, 'complementar': 0, 'ampliada': 0}
    custeio_atual = float(p.get('vlPagamentoEmultiCusteio') or 0)
    perda = max(sum(combinacao[m] * custeio[m] for m in MODALIDADES) - custeio_atual, 0.0)

    equipes_aps_cnes = cnes_client.contar_equipes_aps(cnes.get('equipes', []))
    avisos = []
    if not cnes.get('profissionais'):
        avisos.append("O CNES não retornou profissionais para este município")
    if abs(equipes_aps_cnes - equipes_aps) > 2:
        avisos.append(f"eSF/eAP no CNES ({equipes_aps_cnes}) diferem das credenciadas no Ministério ({equipes_aps})")
    indice_plano, plano, _ = _plano_emulti(dados)

    return EstimativaEmulti(
        codigo_ibge=codigo_ibge, competencia=competencia,
        equipes_aps=equipes_aps, equipes_aps_cnes=equipes_aps_cnes,
        atuais={'estrategica': n('qtEmultiPagamentoEstrategica'), 'complementar': n('qtEmultiPagamentoComplementar'),
                'ampliada': n('qtEmultiPagamentoAmpliada')},
        teto={'estrategica': n('qtTetoEmultiEstrategica'), 'complementar': n('qtTetoEmultiComplementar'),
              'ampliada': n('qtTetoEmultiAmpliada')},
        custeio_atual=custeio_atual,
        profissionais_elegiveis=total_elegiveis, nutricionistas_psicologos=nutri_psi,
        profissionais=profissionais, divisor=div, equipes_estimadas=estimadas,
        combinacao=combinacao, custeio_modalidade=custeio,
        qualidade_pct=float(valores['emulti_qualidade_bom_pct'][0]),
        perda_estimada=round(perda, 2), indice_plano=indice_plano, plano=plano,
        aviso="; ".join(avisos) or None,
    )


async def estimar_ou_none(codigo_ibge: str, competencia: str, valores: Valores,
                          dados: Dict[str, Any]) -> Optional[EstimativaEmulti]:
    """Para o preenchimento automático: se o CNES falhar, só a eMulti fica sem cálculo."""
    try:
        return await estimar(codigo_ibge, competencia, valores, dados=dados)
    except Exception as exc:
        logger.warning(f"Estimativa eMulti indisponível para {codigo_ibge}/{competencia}: {exc}")
        return None
