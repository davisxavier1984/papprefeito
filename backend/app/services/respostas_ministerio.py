"""
Respostas da API de financiamento do Ministério guardadas no SQLite.

Gravadas a cada consulta (SaudeAPIClient.consultar_financiamento). Servem para o sistema
se comparar com o que o consultor informou, sem consultar o Ministério de novo.
"""
import json
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session
from app.models.db_models import RespostaMinisterioDB
from app.utils.logger import logger


class RespostasMinisterioService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def salvar(self, codigo_ibge: str, competencia: str, dados: Dict[str, Any]) -> None:
        row = await self.session.get(RespostaMinisterioDB, (codigo_ibge, competencia))
        texto = json.dumps(dados, ensure_ascii=False)
        if row:
            row.resposta = texto
            row.atualizado_em = datetime.utcnow()
        else:
            self.session.add(RespostaMinisterioDB(codigo_ibge=codigo_ibge, competencia=competencia, resposta=texto))
        await self.session.commit()

    async def obter(self, codigo_ibge: str, competencia: str) -> Optional[Dict[str, Any]]:
        row = await self.session.get(RespostaMinisterioDB, (codigo_ibge, competencia))
        return json.loads(row.resposta) if row else None

    async def todas(self) -> Dict[Tuple[str, str], Dict[str, Any]]:
        rows = (await self.session.execute(select(RespostaMinisterioDB))).scalars().all()
        return {(r.codigo_ibge, r.competencia): json.loads(r.resposta) for r in rows}


async def gravar_resposta(codigo_ibge: str, competencia: str, dados: Dict[str, Any],
                          session_factory=async_session) -> None:
    """Grava sem nunca quebrar a consulta: uma falha aqui só gera aviso no log."""
    try:
        async with session_factory() as session:
            await RespostasMinisterioService(session).salvar(codigo_ibge, competencia, dados)
    except Exception as exc:
        logger.warning(f"Não foi possível guardar a resposta do Ministério de {codigo_ibge}/{competencia}: {exc}")
