"""
Serviço para gerenciar edições de municípios usando SQLAlchemy async
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
import json
from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db_models import EdicaoDB


class EdicoesService:
    """Serviço para CRUD de edições de municípios"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_edicao(
        self,
        codigo_municipio: str,
        competencia: str
    ) -> Optional[Dict[str, Any]]:
        result = await self.session.execute(
            select(EdicaoDB).where(
                and_(
                    EdicaoDB.codigo_municipio == codigo_municipio,
                    EdicaoDB.competencia == competencia
                )
            )
        )
        row = result.scalar_one_or_none()
        if not row:
            return None
        return self._row_to_dict(row)

    async def salvar_edicao(
        self,
        codigo_municipio: str,
        competencia: str,
        perda_recurso_mensal: List[float],
        usuario_id: Optional[str] = None
    ) -> Dict[str, Any]:
        try:
            result = await self.session.execute(
                select(EdicaoDB).where(
                    and_(
                        EdicaoDB.codigo_municipio == codigo_municipio,
                        EdicaoDB.competencia == competencia
                    )
                )
            )
            row = result.scalar_one_or_none()
            now = datetime.utcnow()

            if row:
                row.perda_recurso_mensal = json.dumps(perda_recurso_mensal)
                row.updated_at = now
                if usuario_id:
                    row.usuario_id = usuario_id
            else:
                row = EdicaoDB(
                    codigo_municipio=codigo_municipio,
                    competencia=competencia,
                    perda_recurso_mensal=json.dumps(perda_recurso_mensal),
                    usuario_id=usuario_id,
                    created_at=now,
                    updated_at=now,
                )
                self.session.add(row)

            await self.session.commit()
            await self.session.refresh(row)

            return {
                'success': True,
                'document_id': str(row.id),
                'message': 'Edição salva com sucesso',
                'data': {
                    'codigo_municipio': row.codigo_municipio,
                    'competencia': row.competencia,
                    'perda_recurso_mensal': json.loads(row.perda_recurso_mensal),
                    'updated_at': row.updated_at.isoformat()
                }
            }
        except Exception as e:
            await self.session.rollback()
            return {
                'success': False,
                'error': str(e),
                'message': f'Erro ao salvar edição: {str(e)}'
            }

    async def listar_edicoes(
        self,
        codigo_municipio: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        try:
            stmt = select(EdicaoDB)
            if codigo_municipio:
                stmt = stmt.where(EdicaoDB.codigo_municipio == codigo_municipio)
            stmt = stmt.order_by(desc(EdicaoDB.updated_at)).offset(offset).limit(limit)

            result = await self.session.execute(stmt)
            rows = result.scalars().all()

            # Total count
            from sqlalchemy import func
            count_stmt = select(func.count(EdicaoDB.id))
            if codigo_municipio:
                count_stmt = count_stmt.where(EdicaoDB.codigo_municipio == codigo_municipio)
            total = (await self.session.execute(count_stmt)).scalar()

            return {
                'success': True,
                'total': total,
                'documents': [self._row_to_dict(r) for r in rows]
            }
        except Exception as e:
            print(f"Erro ao listar edições: {e}")
            return {
                'success': False,
                'error': str(e),
                'total': 0,
                'documents': []
            }

    async def deletar_edicao(
        self,
        codigo_municipio: str,
        competencia: str
    ) -> Dict[str, Any]:
        try:
            result = await self.session.execute(
                select(EdicaoDB).where(
                    and_(
                        EdicaoDB.codigo_municipio == codigo_municipio,
                        EdicaoDB.competencia == competencia
                    )
                )
            )
            row = result.scalar_one_or_none()

            if not row:
                return {
                    'success': False,
                    'message': 'Edição não encontrada'
                }

            await self.session.delete(row)
            await self.session.commit()

            return {
                'success': True,
                'message': 'Edição deletada com sucesso'
            }
        except Exception as e:
            await self.session.rollback()
            return {
                'success': False,
                'error': str(e),
                'message': f'Erro ao deletar edição: {str(e)}'
            }

    @staticmethod
    def _row_to_dict(row: EdicaoDB) -> Dict[str, Any]:
        return {
            'id': str(row.id),
            'codigo_municipio': row.codigo_municipio,
            'competencia': row.competencia,
            'perda_recurso_mensal': json.loads(row.perda_recurso_mensal),
            'usuario_id': row.usuario_id,
            'created_at': row.created_at.isoformat() if row.created_at else None,
            'updated_at': row.updated_at.isoformat() if row.updated_at else None,
        }
