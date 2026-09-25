"""
Municípios parecidos (Demais programas e Promoção à saúde).

O consultor preenche esses planos por julgamento: não há regra nos dados do Ministério.
Aqui procuramos, no histórico, os municípios mais parecidos em que ele preencheu à mão,
com a mesma medida validada na simulação de 24/09/2026.
"""
import math
import statistics
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Tuple

from app.services.regras_perda import filtrar_resumos_municipais

PREFIXOS_PARECIDOS: Tuple[str, str] = ('Demais programas', 'Incentivo financeiro da APS - Promoção')


@dataclass
class Perfil:
    uf: str
    municipio: str
    populacao: float
    equipes: float
    recebe: Dict[str, float]


@dataclass
class Exemplo:
    codigo_ibge: str
    competencia: str
    municipio: str
    uf: str
    valor: float
    distancia: float


def perfil(resposta: Dict[str, Any]) -> Optional[Perfil]:
    """Perfil do município na resposta do Ministério; None se faltar pagamento ou população."""
    pagamentos = resposta.get('pagamentos') or []
    p = pagamentos[0] if pagamentos else {}
    populacao = float(p.get('qtPopulacao') or 0)
    if populacao <= 0:
        return None
    recebe: Dict[str, float] = {}
    for r in filtrar_resumos_municipais(resposta.get('resumosPlanosOrcamentarios') or []):
        nome = r.get('dsPlanoOrcamentario') or ''
        recebe[nome] = recebe.get(nome, 0.0) + float(r.get('vlIntegral') or 0)
    return Perfil(
        uf=p.get('sgUf') or '', municipio=p.get('noMunicipio') or '',
        populacao=populacao,
        equipes=float(p.get('qtEsfTotalPgto') or 0) + float(p.get('qtEapTotalPgto') or 0),
        recebe=recebe,
    )


def _recebe(p: Perfil, prefixo: str) -> float:
    return sum(v for nome, v in p.recebe.items() if nome.startswith(prefixo))


def _vetor(p: Perfil, prefixo: str) -> List[float]:
    return [
        math.log10(p.populacao),
        math.log1p(p.equipes),
        math.log1p(_recebe(p, PREFIXOS_PARECIDOS[0])) / 3,
        math.log1p(_recebe(p, PREFIXOS_PARECIDOS[1])) / 3,
        math.log1p(_recebe(p, prefixo)) / 3,
    ]


def distancia(a: Perfil, b: Perfil, prefixo: str) -> float:
    base = math.sqrt(sum((x - y) ** 2 for x, y in zip(_vetor(a, prefixo), _vetor(b, prefixo))))
    return base + (0.5 if a.uf != b.uf else 0.0)


def parecidos(alvo_ibge: str, alvo: Perfil, historico: Iterable[Tuple[str, str, Perfil, List[Dict[str, Any]]]],
              prefixo: str, k: int = 3) -> List[Exemplo]:
    """Os k municípios mais parecidos em que o consultor preencheu o plano à mão com valor > 0."""
    candidatos = []
    for ibge, comp, perf, itens in historico:
        if ibge == alvo_ibge:
            continue
        item = next((i for i in itens if (i.get('plano') or '').startswith(prefixo)), None)
        if not item or item.get('origem', 'manual') != 'manual' or not item.get('valor'):
            continue
        candidatos.append(Exemplo(codigo_ibge=ibge, competencia=comp, municipio=perf.municipio, uf=perf.uf,
                                  valor=float(item['valor']), distancia=round(distancia(alvo, perf, prefixo), 3)))
    return sorted(candidatos, key=lambda e: e.distancia)[:k]


def mediana(exemplos: List[Exemplo]) -> Optional[float]:
    return round(statistics.median(e.valor for e in exemplos), 2) if exemplos else None
