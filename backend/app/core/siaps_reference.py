"""Tabela de valores de referência do cofinanciamento da APS por classificação.

Núcleo financeiro da integração SIAPS: converte a classificação de desempenho de
cada equipe (Ótimo/Bom/Suficiente/Regular) nos componentes **CVAT** (Vínculo e
Acompanhamento Territorial) e **Qualidade** no valor mensal em reais.

Fontes confirmadas: **Portaria GM/MS 3.493/2024, Anexos XCIX-A (CVAT) e XCIX-B (Qualidade)**
da Portaria de Consolidação 6/2017; eSB conforme **Portaria 9.591/2025** (valores de desempenho
da Saúde Bucal, mais recentes). Atualizações de cronograma: 6.907/2025 e 10.994/2026.

**Achado importante:** CVAT e Qualidade têm **valores nacionais únicos — NÃO variam por estrato**
(o estrato/IED afeta apenas o Componente Fixo, que não é baseado em desempenho e não entra no
cálculo de lacuna). O padrão é Ótimo / Bom(0,75×) / Suficiente(0,5×) / Regular(0,25×).
A dimensão de estrato é mantida na estrutura (semeada igual) por extensibilidade.

Dimensões da tabela: ``componente → equipe → variante(CH/modalidade) → classificação → R$``.
O estrato vem do campo ``dsFaixaIndiceEquidadeEsfEap`` da API de financiamento.
"""
from __future__ import annotations

import re
from typing import Optional

from app.utils.logger import logger

# Ordem crescente de desempenho (chaves sem acento, alinhadas às chaves qtd* do SIAPS).
CLASSIFICACOES = ["Regular", "Suficiente", "Bom", "Otimo"]

# Valores confirmados contra os Anexos XCIX-A/B (3.493/2024) e Portaria 9.591/2025 (eSB).
# Caveat residual: a API SIAPS agrega por equipe sem CH/modalidade, então a *variante* usada
# (eAP 20h/30h, eSB tipo, eMulti modalidade) é inferida/aproximada — ver siaps_gap.variante_para.
SIAPS_VALORES_VALIDADOS = True

# Defasagem (meses) entre o quadrimestre avaliado e a competência em que é pago.
SIAPS_LAG_MESES = 4

# Estrato (IED) usado quando o campo do município é desconhecido/ausente.
ESTRATO_DEFAULT = 2

_ESTRATO_RE = re.compile(r"(\d+)")

# ---------------------------------------------------------------------------
# Tabela de valores. Os 4 estratos compartilham, por ora, os mesmos valores
# (manchetes da Portaria). Quando os anexos por estrato forem transcritos,
# basta diferenciar por chave de estrato. ``"_"`` = variante única.
# ---------------------------------------------------------------------------

# Anexo XCIX-A (CVAT). Valores nacionais únicos (não variam por estrato).
_CVAT = {
    "eSF": {"_": {"Regular": 2000.0, "Suficiente": 4000.0, "Bom": 6000.0, "Otimo": 8000.0}},
    "eAP": {
        "30h": {"Regular": 1000.0, "Suficiente": 2000.0, "Bom": 3000.0, "Otimo": 4000.0},
        "20h": {"Regular": 750.0, "Suficiente": 1500.0, "Bom": 2250.0, "Otimo": 3000.0},
    },
}

# Anexo XCIX-B (Qualidade). eSF/eAP/eMulti pelo Anexo; eSB pela Portaria 9.591/2025 (mais recente).
_QUALIDADE = {
    "eSF": {"_": {"Regular": 2000.0, "Suficiente": 4000.0, "Bom": 6000.0, "Otimo": 8000.0}},
    "eAP": {
        "30h": {"Regular": 1000.0, "Suficiente": 2000.0, "Bom": 3000.0, "Otimo": 4000.0},
        "20h": {"Regular": 750.0, "Suficiente": 1500.0, "Bom": 2250.0, "Otimo": 3000.0},
    },
    "eSB": {  # Portaria 9.591/2025 — substitui o Anexo XCIX-B para Saúde Bucal
        "20h": {"Regular": 500.0, "Suficiente": 750.0, "Bom": 1000.0, "Otimo": 1250.0},
        "30h": {"Regular": 750.0, "Suficiente": 1125.0, "Bom": 1500.0, "Otimo": 1875.0},
        "40h_I": {"Regular": 1000.0, "Suficiente": 1500.0, "Bom": 2000.0, "Otimo": 2500.0},
        "40h_II": {"Regular": 1200.0, "Suficiente": 1700.0, "Bom": 2500.0, "Otimo": 3300.0},
    },
    "eMulti": {  # Anexo XCIX-B
        "Ampliada": {"Regular": 2250.0, "Suficiente": 4500.0, "Bom": 6750.0, "Otimo": 9000.0},
        "Complementar": {"Regular": 1500.0, "Suficiente": 3000.0, "Bom": 4500.0, "Otimo": 6000.0},
        "Estrategica": {"Regular": 750.0, "Suficiente": 1500.0, "Bom": 2250.0, "Otimo": 3000.0},
    },
}

# componente -> equipe -> variante -> classificacao -> R$  (estrato aplicado no acesso)
VALORES_POR_COMPONENTE = {"CVAT": _CVAT, "QUALIDADE": _QUALIDADE}

# ---------------------------------------------------------------------------
# Cronograma de implantação (por componente). Fases:
#   transição (< parcial_desde): todos recebem como "Bom";
#   parcial   (parcial_desde..pleno_desde): "Ótimo" recebe Ótimo, demais recebem "Bom";
#   pleno     (>= pleno_desde): vale a classificação real.
# Quadrimestres em "AAAAQN" comparam-se lexicograficamente (N de 1 dígito).
# ---------------------------------------------------------------------------
SIAPS_TIMELINE = {
    "CVAT": {"parcial_desde": "2026Q3", "pleno_desde": "2027Q1"},
    "QUALIDADE": {"parcial_desde": "2026Q2", "pleno_desde": "2027Q1"},
}
CLASSIFICACAO_TRANSICAO = "Bom"


# --- Período: AAAAMM ↔ quadrimestre (duplicado do pacote SIAPS p/ robustez de deploy) ---

def comp_para_quadrimestre(comp: str) -> str:
    """AAAAMM → 'AAAAQN'. Meses 01–04→Q1, 05–08→Q2, 09–12→Q3."""
    ano = comp[:4]
    mes = int(comp[4:])
    return f"{ano}Q{(mes - 1) // 4 + 1}"


def _subtrai_meses(comp: str, n: int) -> str:
    ano, mes = int(comp[:4]), int(comp[4:])
    total = ano * 12 + (mes - 1) - n
    return f"{total // 12:04d}{total % 12 + 1:02d}"


def quadrimestre_aplicavel(competencia: str, lag_meses: int = SIAPS_LAG_MESES) -> str:
    """Quadrimestre cuja classificação determina o pagamento de uma competência.

    O resultado de um quadrimestre é pago nos meses seguintes (defasagem ``lag_meses``).
    """
    return comp_para_quadrimestre(_subtrai_meses(competencia, lag_meses))


# --- Acessores ----------------------------------------------------------------

def normalizar_estrato(ds_faixa: Optional[str]) -> int:
    """``"ESTRATO 2"`` → 2. Desconhecido/ausente → ``ESTRATO_DEFAULT``."""
    if ds_faixa:
        m = _ESTRATO_RE.search(ds_faixa)
        if m:
            n = int(m.group(1))
            if 1 <= n <= 4:
                return n
    return ESTRATO_DEFAULT


def valor_ref(
    componente: str,
    equipe: str,
    classificacao: str,
    estrato: int = ESTRATO_DEFAULT,
    variante: str = "_",
) -> float:
    """Valor mensal de referência (R$) para componente/equipe/classificação.

    Retorna ``0.0`` (com log) quando a combinação não está mapeada — assim o cálculo
    de gap degrada para "sem oportunidade" em vez de quebrar.
    """
    equipes = VALORES_POR_COMPONENTE.get(componente)
    if equipes is None:
        logger.warning("SIAPS valor_ref: componente desconhecido %r", componente)
        return 0.0
    variantes = equipes.get(equipe)
    if variantes is None:
        logger.warning("SIAPS valor_ref: equipe desconhecida %r/%r", componente, equipe)
        return 0.0
    tabela = variantes.get(variante) or variantes.get("_")
    if tabela is None:
        logger.warning(
            "SIAPS valor_ref: variante desconhecida %r/%r/%r", componente, equipe, variante
        )
        return 0.0
    return float(tabela.get(classificacao, 0.0))


def classificacao_vigente(componente: str, quadrimestre: str, classificacao_real: str) -> str:
    """Classificação que efetivamente determina o pagamento, dado o cronograma.

    transição → "Bom"; parcial → "Ótimo" se real for "Ótimo", senão "Bom"; pleno → real.
    """
    fases = SIAPS_TIMELINE.get(componente)
    if fases is None:
        return classificacao_real
    if quadrimestre >= fases["pleno_desde"]:
        return classificacao_real
    if quadrimestre >= fases["parcial_desde"]:
        return classificacao_real if classificacao_real == "Otimo" else CLASSIFICACAO_TRANSICAO
    return CLASSIFICACAO_TRANSICAO
