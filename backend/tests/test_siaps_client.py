"""Testes do cliente SIAPS — foco no que é determinístico (sem rede)."""
import pathlib
import sys

# Permite importar o pacote SIAPS (raiz do repo) para o teste anti-drift.
# Append (não insert) para não sombrear o pacote ``app`` do backend com o app.py da raiz.
_ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.append(str(_ROOT))


def test_uf_por_ibge_nao_diverge_do_pacote_siaps():
    """O mapa UF duplicado no backend deve bater com o do pacote SIAPS."""
    from SIAPS.config import UF_BY_IBGE_PREFIX as siaps_uf
    from app.services.siaps_client import _UF_BY_IBGE_PREFIX as backend_uf

    assert backend_uf == siaps_uf


def test_consultar_para_competencia_resolve_quadrimestre(monkeypatch):
    """A competência mensal é mapeada para o quadrimestre defasado antes de consultar."""
    import asyncio

    from app.services import siaps_client

    capturado = {}

    async def fake_consultar(self, codigo_ibge, quadrimestres, force_refresh=False):
        capturado["quads"] = quadrimestres
        return {"registros": []}

    monkeypatch.setattr(
        siaps_client.SiapsAPIClient, "consultar_classificacao", fake_consultar
    )
    client = siaps_client.SiapsAPIClient()
    # 202509 - 4 meses = 202505 -> 2025Q2
    asyncio.run(client.consultar_para_competencia("260040", "202509"))
    assert capturado["quads"] == ["2025Q2"]
