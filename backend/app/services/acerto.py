"""
Acerto do preenchimento automático em relação ao consultor.

Compara, plano a plano, o total que a regra sugere com o valor que o consultor informou
à mão. Só itens de origem "manual" entram: o que veio da própria regra não mede nada.
"""
import statistics
from typing import Any, Dict, Iterable, List, Tuple

from app.models.schemas import PlanoSugestao
from app.services.parecidos import PREFIXOS_PARECIDOS

PLANOS_ACERTO: Dict[str, Tuple[str, str]] = {
    'esf': ('eSF/eAP', 'Equipes de Saúde da Família'),
    'sb': ('Saúde Bucal', 'Atenção à Saúde Bucal'),
    'acs': ('ACS', 'Agentes Comunitários'),
}
FAIXA_SOMA = (0.8, 1.25)
ERRO_MAXIMO = 0.5


def metricas(pares: List[Tuple[float, float]]) -> Dict[str, Any]:
    """pares = (sugerido, informado)."""
    positivos = [(s, i) for s, i in pares if i > 0]
    erros = [abs(s - i) / i for s, i in positivos]
    soma_inf = sum(i for _, i in pares)
    erro_mediano = round(statistics.median(erros), 4) if erros else None
    razao = round(sum(s for s, _ in pares) / soma_inf, 4) if soma_inf else None
    alerta = bool((razao is not None and not FAIXA_SOMA[0] <= razao <= FAIXA_SOMA[1])
                  or (erro_mediano is not None and erro_mediano > ERRO_MAXIMO))
    return {
        'registros': len(pares),
        'exatos': sum(abs(s - i) < 1 for s, i in pares),
        'erro_mediano': erro_mediano,
        'com_valor': len(positivos),
        'dentro_25': sum(e <= 0.25 for e in erros),
        'zero_certo': sum((s > 0) == (i > 0) for s, i in pares),
        'razao_soma': razao,
        'alerta': alerta,
    }


def comparar(entradas: Iterable[Tuple[List[PlanoSugestao], List[Dict[str, Any]]]]) -> Dict[str, List[Tuple[float, float]]]:
    pares: Dict[str, List[Tuple[float, float]]] = {tipo: [] for tipo in PLANOS_ACERTO}
    for sugestoes, itens in entradas:
        total = {s.tipo: s.total_sugerido for s in sugestoes}
        for tipo, (_, prefixo) in PLANOS_ACERTO.items():
            item = next((i for i in itens if (i.get('plano') or '').startswith(prefixo)), None)
            if item and item.get('origem', 'manual') == 'manual' and tipo in total:
                pares[tipo].append((float(total[tipo]), float(item.get('valor') or 0)))
    return pares


def contar_preenchidos(itens_por_registro: Iterable[List[Dict[str, Any]]]) -> Dict[str, Dict[str, int]]:
    contagem = {p: {'registros': 0, 'preenchidos': 0} for p in PREFIXOS_PARECIDOS}
    for itens in itens_por_registro:
        for prefixo in PREFIXOS_PARECIDOS:
            item = next((i for i in itens if (i.get('plano') or '').startswith(prefixo)), None)
            if item and item.get('origem', 'manual') == 'manual':
                contagem[prefixo]['registros'] += 1
                contagem[prefixo]['preenchidos'] += bool(item.get('valor'))
    return contagem
