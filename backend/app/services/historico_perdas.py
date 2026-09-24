"""
Histórico append-only das perdas gravadas (story 3.2).

Cada gravação em municipios_editados.json gera um registro com o usuário, os valores e,
quando enviados, os itens por plano (origem e valor sugerido). É a base para aprender
com os aceites e as correções do usuário.
"""
import json
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db_models import HistoricoPerdaDB
from app.models.schemas import HistoricoPerda, ItemPerda
from app.utils.logger import logger


class HistoricoPerdasService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def registrar(
        self,
        codigo_ibge: str,
        competencia: str,
        operacao: str,
        perda_recurso_mensal: List[float],
        itens: Optional[List[ItemPerda]] = None,
        usuario_id: Optional[str] = None,
    ) -> None:
        """Acrescenta um registro. Falhas são logadas e não interrompem a gravação principal."""
        try:
            self.session.add(HistoricoPerdaDB(
                codigo_ibge=codigo_ibge,
                competencia=competencia,
                usuario_id=usuario_id,
                operacao=operacao,
                perda_recurso_mensal=json.dumps(perda_recurso_mensal),
                itens=json.dumps([i.model_dump() for i in itens]) if itens is not None else None,
            ))
            await self.session.commit()
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Erro ao registrar histórico de {codigo_ibge}_{competencia}: {e}")

    async def listar(self, codigo_ibge: str, competencia: str) -> List[HistoricoPerda]:
        result = await self.session.execute(
            select(HistoricoPerdaDB)
            .where(HistoricoPerdaDB.codigo_ibge == codigo_ibge, HistoricoPerdaDB.competencia == competencia)
            .order_by(HistoricoPerdaDB.id)
        )
        return [
            HistoricoPerda(
                id=row.id,
                codigo_ibge=row.codigo_ibge,
                competencia=row.competencia,
                usuario_id=row.usuario_id,
                operacao=row.operacao,
                perda_recurso_mensal=json.loads(row.perda_recurso_mensal),
                itens=json.loads(row.itens) if row.itens else None,
                created_at=row.created_at,
            )
            for row in result.scalars().all()
        ]
