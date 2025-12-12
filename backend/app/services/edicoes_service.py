"""
Serviço para gerenciar edições de municípios no Appwrite
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
import json
from appwrite.query import Query
from appwrite.exception import AppwriteException
from appwrite.id import ID

from app.core.appwrite_client import appwrite_client
from app.core.config import settings


class EdicoesService:
    """Serviço para CRUD de edições de municípios"""

    def __init__(self):
        self.db = appwrite_client.get_databases()
        self.database_id = settings.APPWRITE_DATABASE_ID
        self.collection_id = settings.APPWRITE_COLLECTION_EDICOES_ID

    async def get_edicao(
        self,
        codigo_municipio: str,
        competencia: str
    ) -> Optional[Dict[str, Any]]:
        """
        Busca edição específica de município por código e competência

        Args:
            codigo_municipio: Código IBGE do município
            competencia: Competência no formato AAAAMM

        Returns:
            Dict com os dados da edição ou None se não encontrada
        """
        try:
            result = self.db.list_documents(
                database_id=self.database_id,
                collection_id=self.collection_id,
                queries=[
                    Query.equal('codigo_municipio', codigo_municipio),
                    Query.equal('competencia', competencia)
                ]
            )

            if result['total'] > 0:
                doc = result['documents'][0]
                return {
                    'id': doc['$id'],
                    'codigo_municipio': doc['codigo_municipio'],
                    'competencia': doc['competencia'],
                    'perda_recurso_mensal': json.loads(doc['perda_recurso_mensal']),
                    'usuario_id': doc.get('usuario_id'),
                    'created_at': doc['$createdAt'],
                    'updated_at': doc['$updatedAt']
                }
            return None

        except AppwriteException as e:
            print(f"Erro ao buscar edição: {e}")
            return None

    async def salvar_edicao(
        self,
        codigo_municipio: str,
        competencia: str,
        perda_recurso_mensal: List[float],
        usuario_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Salva ou atualiza edição de município

        Args:
            codigo_municipio: Código IBGE do município
            competencia: Competência no formato AAAAMM
            perda_recurso_mensal: Lista de valores de perda mensal por recurso
            usuario_id: ID do usuário que fez a edição (opcional)

        Returns:
            Dict com resultado da operação
        """
        try:
            # Verificar se já existe
            existing = await self.get_edicao(codigo_municipio, competencia)

            data = {
                'codigo_municipio': codigo_municipio,
                'competencia': competencia,
                'perda_recurso_mensal': json.dumps(perda_recurso_mensal),
                'updated_at': datetime.utcnow().isoformat()
            }

            if usuario_id:
                data['usuario_id'] = usuario_id

            if existing:
                # Atualizar documento existente
                result = self.db.update_document(
                    database_id=self.database_id,
                    collection_id=self.collection_id,
                    document_id=existing['id'],
                    data=data
                )
            else:
                # Criar novo documento
                data['created_at'] = datetime.utcnow().isoformat()
                document_id = f"{codigo_municipio}_{competencia}"

                result = self.db.create_document(
                    database_id=self.database_id,
                    collection_id=self.collection_id,
                    document_id=document_id,
                    data=data
                )

            return {
                'success': True,
                'document_id': result['$id'],
                'message': 'Edição salva com sucesso',
                'data': {
                    'codigo_municipio': result['codigo_municipio'],
                    'competencia': result['competencia'],
                    'perda_recurso_mensal': json.loads(result['perda_recurso_mensal']),
                    'updated_at': result['$updatedAt']
                }
            }

        except AppwriteException as e:
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
        """
        Lista todas as edições ou filtra por município

        Args:
            codigo_municipio: Código IBGE do município (opcional)
            limit: Número máximo de resultados
            offset: Offset para paginação

        Returns:
            Dict com lista de edições e total
        """
        try:
            queries = [
                Query.limit(limit),
                Query.offset(offset),
                Query.order_desc('$updatedAt')
            ]

            if codigo_municipio:
                queries.append(Query.equal('codigo_municipio', codigo_municipio))

            result = self.db.list_documents(
                database_id=self.database_id,
                collection_id=self.collection_id,
                queries=queries
            )

            documents = [
                {
                    'id': doc['$id'],
                    'codigo_municipio': doc['codigo_municipio'],
                    'competencia': doc['competencia'],
                    'perda_recurso_mensal': json.loads(doc['perda_recurso_mensal']),
                    'usuario_id': doc.get('usuario_id'),
                    'created_at': doc['$createdAt'],
                    'updated_at': doc['$updatedAt']
                }
                for doc in result['documents']
            ]

            return {
                'success': True,
                'total': result['total'],
                'documents': documents
            }

        except AppwriteException as e:
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
        """
        Deleta edição de município

        Args:
            codigo_municipio: Código IBGE do município
            competencia: Competência no formato AAAAMM

        Returns:
            Dict com resultado da operação
        """
        try:
            # Buscar documento primeiro para validar se existe
            existing = await self.get_edicao(codigo_municipio, competencia)

            if not existing:
                return {
                    'success': False,
                    'message': 'Edição não encontrada'
                }

            self.db.delete_document(
                database_id=self.database_id,
                collection_id=self.collection_id,
                document_id=existing['id']
            )

            return {
                'success': True,
                'message': 'Edição deletada com sucesso'
            }

        except AppwriteException as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Erro ao deletar edição: {str(e)}'
            }


# Instância global do serviço
edicoes_service = EdicoesService()
