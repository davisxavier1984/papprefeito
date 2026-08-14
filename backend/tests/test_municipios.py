"""Testes para o serviço de consulta de municípios."""
from pyUFbr.baseuf import ufbr

from app.services.municipios import municipio_service


def test_municipios_homonimos_resolvem_codigo_da_uf_correta():
    """SAPUCAIA existe em PA e RJ; cada uma deve receber o código da sua UF."""
    assert municipio_service.get_codigo_ibge("SAPUCAIA", "PA") == "150775"
    assert municipio_service.get_codigo_ibge("SAPUCAIA", "RJ") == "330540"


def test_municipio_homonimo_aparece_na_lista_da_uf():
    municipios_pa = municipio_service.get_municipios_por_uf("PA")

    sapucaia = next((m for m in municipios_pa if m.nome == "SAPUCAIA"), None)

    assert sapucaia is not None
    assert sapucaia.codigo_ibge == "150775"
    assert sapucaia.uf == "PA"


def test_nenhuma_uf_perde_municipios():
    """A lista retornada deve conter todos os municípios da UF, sem descartes."""
    for uf in ufbr.list_uf:
        esperados = set(ufbr.list_cidades(uf))
        retornados = {m.nome for m in municipio_service.get_municipios_por_uf(uf)}

        assert retornados == esperados, f"{uf} perdeu {sorted(esperados - retornados)}"


def test_uf_inexistente_retorna_lista_vazia():
    assert municipio_service.get_municipios_por_uf("XX") == []
