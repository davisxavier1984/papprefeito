#!/usr/bin/env python3
"""
Carga inicial de respostas_ministerio para as perdas já salvas.

Uso (no servidor, uma vez): cd backend && .venv/bin/python scripts/carregar_respostas_ministerio.py [desde=202512]
Consulta o Ministério (só leitura) para cada município/competência salvo a partir de `desde`
que ainda não tenha resposta guardada. A gravação acontece dentro da própria consulta.
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import async_session, init_db  # noqa: E402
from app.services.api_client import saude_api_client  # noqa: E402
from app.services.municipios_editados import municipio_editado_service  # noqa: E402
from app.services.respostas_ministerio import RespostasMinisterioService  # noqa: E402


async def main(desde: str) -> None:
    await init_db()
    async with async_session() as session:
        existentes = set(await RespostasMinisterioService(session).todas())
    pendentes = sorted({(e.codigo_ibge[:6], e.competencia) for e in municipio_editado_service.get_all_editados()
                        if e.competencia >= desde} - existentes)
    print(f"{len(pendentes)} consultas pendentes")
    falhas = 0
    for ibge, comp in pendentes:
        dados = await saude_api_client.consultar_financiamento(ibge, comp)
        falhas += dados is None
        print(f"{ibge}/{comp}: {'ok' if dados else 'sem dados'}")
        await asyncio.sleep(0.4)
    print(f"Concluído. Sem dados: {falhas}")


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else "202512"))
