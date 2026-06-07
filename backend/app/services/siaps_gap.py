"""Cálculo da lacuna financeira (gap) a partir da classificação SIAPS.

Funções puras (sem I/O) que cruzam a classificação de desempenho das equipes
(envelope SIAPS) com a tabela de valores de referência (``siaps_reference``) e os
dados de financiamento (estrato + pagamentos), produzindo:

- ``detalhe[]``: gap por equipe × componente × quadrimestre (alimenta o card de detalhe);
- ``perda_por_recurso_{vigente,potencial}[]``: arrays **posicionais** alinhados a
  ``resumosPlanosOrcamentarios`` (alimentam, posição a posição, ``perda_recurso_mensal``).

Dois modos — ambos medem o ganho contra o que o município **recebe hoje** (sob a fase do
cronograma; na transição todas as equipes são pagas como "Bom", não pela classificação crua):
- ``potencial``: ganho se todas as equipes chegarem a "Ótimo" no valor pleno (fim do cronograma);
- ``vigente``: ganho capturável agora, com o teto também limitado pela fase atual (0 na transição).
"""
from __future__ import annotations

from typing import Optional

from app.core.siaps_reference import (
    CLASSIFICACOES,
    classificacao_vigente,
    normalizar_estrato,
    valor_ref,
)

# sgEquipe (SIAPS) → substring do dsPlanoOrcamentario (espelha processarProgramas.ts).
EQUIPE_PARA_SUBSTRING = {
    "eSF": "Equipes de Saúde da Família",
    "eAP": "Equipes de Saúde da Família",
    "eSB": "Saúde Bucal",
    "eMulti": "Multiprofissionais",
}

# Variante (CH/modalidade) padrão por equipe quando não inferível dos pagamentos.
# TODO confirmar inferência fina a partir dos campos de pagamentos.
_VARIANTE_DEFAULT = {"eSF": "_", "eAP": "30h", "eSB": "40h_I", "eMulti": "Ampliada"}


def estrato_para(pagamentos: list) -> int:
    """Estrato (IED) do município a partir do primeiro pagamento."""
    ds = None
    if pagamentos:
        ds = (pagamentos[0] or {}).get("dsFaixaIndiceEquidadeEsfEap")
    return normalizar_estrato(ds)


def variante_para(registro: dict, pagamentos: list) -> str:
    """Variante (CH/modalidade) da equipe, derivada das modalidades que o município
    REALMENTE tem nos pagamentos — não de um palpite. Usa a modalidade predominante
    (maior nº de equipes pagas). Só cai no default quando o pagamento não informa
    nenhuma modalidade ("se não tem, não usa").
    """
    equipe = registro.get("sgEquipe", "")
    pag = pagamentos[0] if pagamentos else {}

    if equipe == "eAP":
        candidatos = {
            "30h": (pag.get("qtEap30hCompletas") or 0) + (pag.get("qtEap30hIncompletas") or 0),
            "20h": (pag.get("qtEap20hCompletas") or 0) + (pag.get("qtEap20hIncompletas") or 0),
        }
    elif equipe == "eSB":
        candidatos = {
            "40h_I": pag.get("qtSbPagamentoModalidadeI") or 0,
            "40h_II": pag.get("qtSbPagamentoModalidadeII") or 0,
            "30h": pag.get("qtSbPagamentoDifModalidade30Horas") or 0,
            "20h": pag.get("qtSbPagamentoDifModalidade20Horas") or 0,
        }
    elif equipe == "eMulti":
        candidatos = {
            "Ampliada": pag.get("qtEmultiPagamentoAmpliada") or 0,
            "Complementar": pag.get("qtEmultiPagamentoComplementar") or 0,
            "Estrategica": pag.get("qtEmultiPagamentoEstrategica") or 0,
        }
    else:
        return _VARIANTE_DEFAULT.get(equipe, "_")

    presentes = {k: v for k, v in candidatos.items() if v and v > 0}
    if presentes:
        return max(presentes, key=presentes.get)
    return _VARIANTE_DEFAULT.get(equipe, "_")


def _contagens(registro: dict) -> dict:
    """{classificacao: qtd} a partir das chaves qtdClassificacao* do registro."""
    return {
        c: int(registro.get(f"qtdClassificacao{c}", 0) or 0) for c in CLASSIFICACOES
    }


def gap_por_registro(registro: dict, estrato: int, variante: str, modo: str) -> float:
    """Lacuna financeira mensal (R$) de um registro (equipe × componente × quadrimestre)."""
    componente = registro.get("tipoOrigem", "")
    equipe = registro.get("sgEquipe", "")
    quadrimestre = registro.get("nuQuadrimestre", "")
    qtd = _contagens(registro)

    def v(classificacao: str) -> float:
        return valor_ref(componente, equipe, classificacao, estrato=estrato, variante=variante)

    # Baseline comum: o que o município RECEBE HOJE, sob a fase atual do cronograma.
    # Na transição todas as equipes são pagas como "Bom" (piso real) — não pela classificação
    # crua. Assim o ganho é medido contra o que de fato entra no caixa, não contra Regular/Suf.
    total = sum(qtd.values())
    pago_atual = sum(
        qtd[c] * v(classificacao_vigente(componente, quadrimestre, c))
        for c in CLASSIFICACOES
    )

    if modo == "potencial":
        # Teto = todas as equipes pagas como Ótimo no valor PLENO (fim do cronograma).
        return float(max(0.0, total * v("Otimo") - pago_atual))

    if modo == "vigente":
        # Teto = toda equipe "Ótima" SOB A FASE ATUAL (na transição ainda é "Bom" → 0 capturável).
        pago_se_otimo = v(classificacao_vigente(componente, quadrimestre, "Otimo"))
        return float(max(0.0, total * pago_se_otimo - pago_atual))

    raise ValueError(f"modo inválido: {modo!r} (use 'potencial' ou 'vigente')")


def _indice_resumo(sg_equipe: str, resumos: list) -> Optional[int]:
    """Índice do resumo cujo dsPlanoOrcamentario casa com a equipe (substring)."""
    substr = EQUIPE_PARA_SUBSTRING.get(sg_equipe)
    if not substr:
        return None
    for i, r in enumerate(resumos):
        if substr in (r.get("dsPlanoOrcamentario") or ""):
            return i
    return None


def calcular_gaps(envelope: dict, dados_financiamento: dict) -> dict:
    """Cruza o envelope SIAPS com o financiamento e devolve detalhe + arrays posicionais."""
    resumos = dados_financiamento.get("resumosPlanosOrcamentarios", []) or []
    pagamentos = dados_financiamento.get("pagamentos", []) or []
    estrato = estrato_para(pagamentos)

    perda_vigente = [0.0] * len(resumos)
    perda_potencial = [0.0] * len(resumos)
    detalhe = []

    for reg in envelope.get("registros", []) or []:
        variante = variante_para(reg, pagamentos)
        g_vig = gap_por_registro(reg, estrato, variante, "vigente")
        g_pot = gap_por_registro(reg, estrato, variante, "potencial")

        idx = _indice_resumo(reg.get("sgEquipe", ""), resumos)
        if idx is not None:
            perda_vigente[idx] += g_vig
            perda_potencial[idx] += g_pot

        detalhe.append({
            "sgEquipe": reg.get("sgEquipe"),
            "componente": reg.get("tipoOrigem"),
            "quadrimestre": reg.get("nuQuadrimestre"),
            "variante": variante,
            "contagens": _contagens(reg),
            "totalEquipes": int(reg.get("totalEquipesValidasParaComponente", 0) or 0),
            "gap_vigente": g_vig,
            "gap_potencial": g_pot,
        })

    return {
        "estrato": estrato,
        "perda_por_recurso_vigente": perda_vigente,
        "perda_por_recurso_potencial": perda_potencial,
        "total_vigente": float(sum(perda_vigente)),
        "total_potencial": float(sum(perda_potencial)),
        "detalhe": detalhe,
    }
