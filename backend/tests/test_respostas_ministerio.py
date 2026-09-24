"""Respostas do Ministério guardadas no SQLite (banco temporário, nunca o de produção)."""
import asyncio

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.database import Base
from app.services.respostas_ministerio import RespostasMinisterioService, gravar_resposta


def _fabrica(tmp_path):
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'teste.db'}")

    async def criar():
        from app.models.db_models import RespostaMinisterioDB  # noqa: F401
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    asyncio.run(criar())
    return async_sessionmaker(engine, expire_on_commit=False)


def test_salvar_obter_e_substituir(tmp_path):
    fabrica = _fabrica(tmp_path)

    async def fluxo():
        async with fabrica() as s:
            svc = RespostasMinisterioService(s)
            await svc.salvar('290240', '202512', {'pagamentos': [{'qtPopulacao': 1}]})
            await svc.salvar('290240', '202512', {'pagamentos': [{'qtPopulacao': 2}]})
            await svc.salvar('292940', '202606', {'pagamentos': []})
            assert (await svc.obter('290240', '202512'))['pagamentos'][0]['qtPopulacao'] == 2
            assert await svc.obter('999999', '202512') is None
            assert set(await svc.todas()) == {('290240', '202512'), ('292940', '202606')}
    asyncio.run(fluxo())


def test_gravar_resposta_usa_a_fabrica(tmp_path):
    fabrica = _fabrica(tmp_path)
    asyncio.run(gravar_resposta('290240', '202512', {'x': 1}, session_factory=fabrica))

    async def ler():
        async with fabrica() as s:
            return await RespostasMinisterioService(s).obter('290240', '202512')
    assert asyncio.run(ler()) == {'x': 1}


def test_gravar_resposta_nao_propaga_erro(tmp_path):
    # Banco sem a tabela: a gravação falha, mas a consulta não pode quebrar
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'vazio.db'}")
    fabrica = async_sessionmaker(engine, expire_on_commit=False)
    asyncio.run(gravar_resposta('290240', '202512', {'x': 1}, session_factory=fabrica))


def test_listar_so_traz_as_chaves_pedidas(tmp_path):
    fabrica = _fabrica(tmp_path)

    async def fluxo():
        async with fabrica() as s:
            svc = RespostasMinisterioService(s)
            await svc.salvar('290240', '202512', {'pagamentos': [{'qtPopulacao': 1}]})
            await svc.salvar('290240', '202606', {'pagamentos': [{'qtPopulacao': 2}]})
            await svc.salvar('292940', '202512', {'pagamentos': [{'qtPopulacao': 3}]})
            resultado = await svc.listar([('290240', '202512'), ('292940', '999999')])
            # a chave pedida com competência que não existe não aparece
            assert set(resultado) == {('290240', '202512')}
            assert resultado[('290240', '202512')]['pagamentos'][0]['qtPopulacao'] == 1
    asyncio.run(fluxo())


def test_listar_sem_chaves_nao_consulta_e_devolve_vazio(tmp_path):
    fabrica = _fabrica(tmp_path)

    async def fluxo():
        async with fabrica() as s:
            assert await RespostasMinisterioService(s).listar([]) == {}
    asyncio.run(fluxo())


def test_salvar_concorrente_da_mesma_chave_nao_quebra(tmp_path):
    # Duas sessões tentando gravar a MESMA chave nova ao mesmo tempo não podem
    # derrubar uma delas com erro de chave duplicada: precisa ser um upsert atômico.
    fabrica = _fabrica(tmp_path)

    async def fluxo():
        async with fabrica() as s1, fabrica() as s2:
            await asyncio.gather(
                RespostasMinisterioService(s1).salvar('290240', '202512', {'pagamentos': [{'qtPopulacao': 1}]}),
                RespostasMinisterioService(s2).salvar('290240', '202512', {'pagamentos': [{'qtPopulacao': 2}]}),
            )
        async with fabrica() as s:
            resultado = await RespostasMinisterioService(s).obter('290240', '202512')
            assert resultado['pagamentos'][0]['qtPopulacao'] in (1, 2)
    asyncio.run(fluxo())


def test_listar_em_lotes_de_ate_500_codigos(tmp_path):
    fabrica = _fabrica(tmp_path)

    async def fluxo():
        async with fabrica() as s:
            svc = RespostasMinisterioService(s)
            for i in range(520):
                await svc.salvar(f"{i:06d}", '202512', {'pagamentos': [{'qtPopulacao': i}]})
            chaves = [(f"{i:06d}", '202512') for i in range(520)]
            resultado = await svc.listar(chaves)
            assert len(resultado) == 520
            assert resultado[('000519', '202512')]['pagamentos'][0]['qtPopulacao'] == 519
    asyncio.run(fluxo())
