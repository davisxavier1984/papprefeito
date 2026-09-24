"""
Respostas da API de financiamento do Ministério guardadas no SQLite.

Gravadas a cada consulta (SaudeAPIClient.consultar_financiamento). Servem para o sistema
se comparar com o que o consultor informou, sem consultar o Ministério de novo.
"""
import json
from datetime import datetime
from typing import Any, Dict, Iterable, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session
from app.models.db_models import RespostaMinisterioDB
from app.utils.logger import logger


class RespostasMinisterioService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def salvar(self, codigo_ibge: str, competencia: str, dados: Dict[str, Any]) -> None:
        """Upsert atômico: duas gravações concorrentes da mesma chave não derrubam uma delas."""
        texto = json.dumps(dados, ensure_ascii=False)
        agora = datetime.utcnow()
        stmt = insert(RespostaMinisterioDB).values(
            codigo_ibge=codigo_ibge, competencia=competencia, resposta=texto, atualizado_em=agora,
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=['codigo_ibge', 'competencia'],
            set_={'resposta': stmt.excluded.resposta, 'atualizado_em': stmt.excluded.atualizado_em},
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def obter(self, codigo_ibge: str, competencia: str) -> Optional[Dict[str, Any]]:
        row = await self.session.get(RespostaMinisterioDB, (codigo_ibge, competencia))
        return json.loads(row.resposta) if row else None

    async def todas(self) -> Dict[Tuple[str, str], Dict[str, Any]]:
        rows = (await self.session.execute(select(RespostaMinisterioDB))).scalars().all()
        return {(r.codigo_ibge, r.competencia): json.loads(r.resposta) for r in rows}

    async def listar(self, chaves: Iterable[Tuple[str, str]]) -> Dict[Tuple[str, str], Dict[str, Any]]:
        """Busca só as chaves pedidas, sem ler a tabela inteira.

        Filtra por `codigo_ibge IN (...)` (em lotes de até 500 códigos, se a lista for
        grande) e depois filtra a competência em Python, já que a tabela cresce com toda
        consulta ao Ministério.
        """
        pedidas = set(chaves)
        if not pedidas:
            return {}
        codigos = sorted({codigo for codigo, _ in pedidas})
        resultado: Dict[Tuple[str, str], Dict[str, Any]] = {}
        for inicio in range(0, len(codigos), 500):
            bloco = codigos[inicio:inicio + 500]
            rows = (await self.session.execute(
                select(RespostaMinisterioDB).where(RespostaMinisterioDB.codigo_ibge.in_(bloco))
            )).scalars().all()
            for r in rows:
                chave = (r.codigo_ibge, r.competencia)
                if chave in pedidas:
                    resultado[chave] = json.loads(r.resposta)
        return resultado


async def gravar_resposta(codigo_ibge: str, competencia: str, dados: Dict[str, Any],
                          session_factory=async_session) -> None:
    """Grava sem nunca quebrar a consulta: uma falha aqui só gera aviso no log."""
    try:
        async with session_factory() as session:
            await RespostasMinisterioService(session).salvar(codigo_ibge, competencia, dados)
    except Exception as exc:
        logger.warning(f"Não foi possível guardar a resposta do Ministério de {codigo_ibge}/{competencia}: {exc}")
