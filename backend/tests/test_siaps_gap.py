"""Testes do calculador de lacuna financeira (gap) do SIAPS."""
import json
import pathlib

import pytest

from app.services.siaps_gap import (
    estrato_para,
    gap_por_registro,
    calcular_gaps,
)

FIXTURE = pathlib.Path(__file__).parent / "fixtures" / "siaps_260040_2025Q1.json"


@pytest.fixture
def envelope():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _registro(envelope, sg, tipo):
    return next(
        r for r in envelope["registros"]
        if r["sgEquipe"] == sg and r["tipoOrigem"] == tipo
    )


def test_estrato_para_le_campo_do_pagamento():
    assert estrato_para([{"dsFaixaIndiceEquidadeEsfEap": "ESTRATO 2"}]) == 2


def test_estrato_para_default_sem_pagamento():
    assert estrato_para([]) == 2


def test_gap_potencial_esf_cvat(envelope):
    # Água Preta 2025Q1 eSF CVAT: Reg7/Suf2/Bom2/Ót2 = 13 equipes; Ótimo=8000, Bom=6000.
    # Baseline = pago hoje (transição → todas como "Bom"); teto = todas Ótimo (valor pleno).
    # potencial = 13*8000 - 13*6000 = 104000 - 78000 = 26000.
    reg = _registro(envelope, "eSF", "CVAT")
    assert gap_por_registro(reg, estrato=2, variante="_", modo="potencial") == 26000.0


def test_gap_vigente_transicao_e_zero(envelope):
    # Em 2025Q1 (transição) o pagamento está travado em "Bom" → nada capturável agora.
    reg = _registro(envelope, "eSF", "CVAT")
    assert gap_por_registro(reg, estrato=2, variante="_", modo="vigente") == 0.0


def test_calcular_gaps_alinha_posicional_aos_resumos(envelope):
    dados = {
        "resumosPlanosOrcamentarios": [
            {"dsPlanoOrcamentario": "Equipes de Saúde da Família - eSF e eAP"},
            {"dsPlanoOrcamentario": "Atenção à Saúde Bucal"},
            {"dsPlanoOrcamentario": "Equipes Multiprofissionais"},
            {"dsPlanoOrcamentario": "Pagamento per capita"},
        ],
        "pagamentos": [{"dsFaixaIndiceEquidadeEsfEap": "ESTRATO 2"}],
    }
    resultado = calcular_gaps(envelope, dados)

    perdas = resultado["perda_por_recurso_potencial"]
    # Um valor por resumo, na mesma ordem.
    assert len(perdas) == 4
    # eSF (CVAT+Qualidade) cai no índice 0; eSB no 1; eMulti no 2; per capita 0.
    assert perdas[0] > 0
    assert perdas[1] > 0
    assert perdas[2] > 0
    assert perdas[3] == 0.0


def test_calcular_gaps_detalhe_por_equipe_componente(envelope):
    dados = {
        "resumosPlanosOrcamentarios": [
            {"dsPlanoOrcamentario": "Equipes de Saúde da Família - eSF e eAP"},
        ],
        "pagamentos": [{"dsFaixaIndiceEquidadeEsfEap": "ESTRATO 2"}],
    }
    resultado = calcular_gaps(envelope, dados)
    # 4 registros no fixture → 4 itens de detalhe.
    assert len(resultado["detalhe"]) == 4
    item = next(
        d for d in resultado["detalhe"]
        if d["sgEquipe"] == "eSF" and d["componente"] == "CVAT"
    )
    assert item["gap_potencial"] == 26000.0
    assert item["gap_vigente"] == 0.0
    assert item["quadrimestre"] == "2025Q1"
