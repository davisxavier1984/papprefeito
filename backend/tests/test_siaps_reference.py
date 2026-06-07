"""Testes da tabela de valores de referência do SIAPS (núcleo financeiro)."""
import pytest

from app.core.siaps_reference import (
    normalizar_estrato,
    valor_ref,
    quadrimestre_aplicavel,
    classificacao_vigente,
)


def test_normalizar_estrato_extrai_numero():
    assert normalizar_estrato("ESTRATO 2") == 2
    assert normalizar_estrato("Estrato 4") == 4


def test_normalizar_estrato_default_quando_desconhecido():
    assert normalizar_estrato(None) == 2
    assert normalizar_estrato("não informado") == 2


def test_valor_ref_cvat_esf():
    # Anexo XCIX-A: padrão Ótimo / 0,75x / 0,5x / 0,25x
    assert valor_ref("CVAT", "eSF", "Otimo") == 8000.0
    assert valor_ref("CVAT", "eSF", "Bom") == 6000.0
    assert valor_ref("CVAT", "eSF", "Suficiente") == 4000.0
    assert valor_ref("CVAT", "eSF", "Regular") == 2000.0


def test_valor_ref_qualidade_eap_por_variante():
    # Qualidade eAP também varia por carga horária (Anexo XCIX-B).
    assert valor_ref("QUALIDADE", "eAP", "Otimo", variante="30h") == 4000.0
    assert valor_ref("QUALIDADE", "eAP", "Otimo", variante="20h") == 3000.0


def test_valor_ref_qualidade_esb_por_variante():
    assert valor_ref("QUALIDADE", "eSB", "Otimo", variante="40h_I") == 2500.0
    assert valor_ref("QUALIDADE", "eSB", "Regular", variante="20h") == 500.0


def test_valor_ref_qualidade_emulti_por_variante():
    assert valor_ref("QUALIDADE", "eMulti", "Bom", variante="Ampliada") == 6750.0


def test_valor_ref_desconhecido_retorna_zero():
    assert valor_ref("CVAT", "inexistente", "Bom") == 0.0


def test_quadrimestre_aplicavel_aplica_lag():
    # Competência 202509 (set) menos 4 meses -> 202505 (mai) -> 2025Q2
    assert quadrimestre_aplicavel("202509") == "2025Q2"
    # 202501 (jan) menos 4 meses -> 202409 (set/2024) -> 2024Q3
    assert quadrimestre_aplicavel("202501") == "2024Q3"


def test_classificacao_vigente_transicao_forca_bom():
    # Antes da implantação parcial, todos recebem como "Bom" (regra de transição).
    assert classificacao_vigente("CVAT", "2025Q1", "Otimo") == "Bom"
    assert classificacao_vigente("CVAT", "2025Q1", "Regular") == "Bom"


def test_classificacao_vigente_parcial_otimo_ou_bom():
    # CVAT parcial a partir de 2026Q3: Ótimo recebe Ótimo, os demais recebem Bom.
    assert classificacao_vigente("CVAT", "2026Q3", "Otimo") == "Otimo"
    assert classificacao_vigente("CVAT", "2026Q3", "Regular") == "Bom"
    assert classificacao_vigente("CVAT", "2026Q3", "Suficiente") == "Bom"


def test_classificacao_vigente_pleno_usa_real():
    # A partir de 2027Q1 vale a classificação real em todos os níveis.
    assert classificacao_vigente("CVAT", "2027Q1", "Regular") == "Regular"
    assert classificacao_vigente("CVAT", "2027Q1", "Suficiente") == "Suficiente"
