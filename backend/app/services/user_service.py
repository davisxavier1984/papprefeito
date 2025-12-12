"""
Serviço para gerenciamento de usuários usando Appwrite
"""
from typing import Optional, List
from datetime import datetime
from fastapi import HTTPException, status
from appwrite.exception import AppwriteException
from appwrite.id import ID
from appwrite.query import Query

from app.core.appwrite_client import appwrite_client
from app.core.security import get_password_hash, verify_password
from app.core.config import settings
from app.models.schemas import User, UserCreate, UserUpdate
from app.utils.logger import logger


class UserService:
    """Serviço para operações de usuários"""

    def __init__(self):
        self.databases = appwrite_client.get_databases()
        self.database_id = settings.APPWRITE_DATABASE_ID
        # Vamos criar uma collection específica para usuários
        self.collection_id = "users"

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Busca usuário por ID

        Args:
            user_id: ID do usuário

        Returns:
            User ou None se não encontrado
        """
        try:
            doc = self.databases.get_document(
                database_id=self.database_id,
                collection_id=self.collection_id,
                document_id=user_id
            )
            return self._document_to_user(doc)
        except AppwriteException as e:
            if e.code == 404:
                return None
            logger.error(f"Erro ao buscar usuário por ID: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao buscar usuário"
            )

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Busca usuário por email

        Args:
            email: Email do usuário

        Returns:
            User ou None se não encontrado
        """
        try:
            result = self.databases.list_documents(
                database_id=self.database_id,
                collection_id=self.collection_id,
                queries=[
                    Query.equal("email", email.lower())
                ]
            )

            if result['total'] == 0:
                return None

            return self._document_to_user(result['documents'][0])
        except AppwriteException as e:
            logger.error(f"Erro ao buscar usuário por email: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao buscar usuário"
            )

    async def create_user(self, user_data: UserCreate) -> User:
        """
        Cria um novo usuário

        Args:
            user_data: Dados do usuário a ser criado

        Returns:
            Usuário criado

        Raises:
            HTTPException: Se já existir um usuário com o mesmo email
        """
        # Verifica se já existe usuário com o email
        existing_user = await self.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já cadastrado"
            )

        try:
            # Cria hash da senha
            hashed_password = get_password_hash(user_data.password)

            # Prepara dados para criar no Appwrite
            now = datetime.utcnow().isoformat()
            document_data = {
                "email": user_data.email.lower(),
                "nome": user_data.nome,
                "hashed_password": hashed_password,
                "is_active": True,
                "is_authorized": False,  # Novo usuário precisa de autorização
                "is_superuser": False,
                "created_at": now,
                "updated_at": now
            }

            # Cria documento no Appwrite
            doc = self.databases.create_document(
                database_id=self.database_id,
                collection_id=self.collection_id,
                document_id=ID.unique(),
                data=document_data
            )

            logger.info(f"Usuário criado com sucesso: {doc['$id']}")
            return self._document_to_user(doc)

        except AppwriteException as e:
            logger.error(f"Erro ao criar usuário: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao criar usuário"
            )

    async def update_user(self, user_id: str, user_data: UserUpdate) -> User:
        """
        Atualiza dados do usuário

        Args:
            user_id: ID do usuário
            user_data: Dados a serem atualizados

        Returns:
            Usuário atualizado
        """
        # Verifica se o usuário existe
        user = await self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )

        # Se está atualizando email, verifica se já existe outro usuário com o email
        if user_data.email and user_data.email != user.email:
            existing_user = await self.get_user_by_email(user_data.email)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email já cadastrado"
                )

        try:
            # Prepara dados para atualização (apenas campos não nulos)
            update_data = {}
            if user_data.nome is not None:
                update_data["nome"] = user_data.nome
            if user_data.email is not None:
                update_data["email"] = user_data.email.lower()
            if user_data.is_active is not None:
                update_data["is_active"] = user_data.is_active
            if user_data.is_authorized is not None:
                update_data["is_authorized"] = user_data.is_authorized
            if user_data.is_superuser is not None:
                update_data["is_superuser"] = user_data.is_superuser

            update_data["updated_at"] = datetime.utcnow().isoformat()

            # Atualiza documento no Appwrite
            doc = self.databases.update_document(
                database_id=self.database_id,
                collection_id=self.collection_id,
                document_id=user_id,
                data=update_data
            )

            logger.info(f"Usuário atualizado com sucesso: {user_id}")
            return self._document_to_user(doc)

        except AppwriteException as e:
            logger.error(f"Erro ao atualizar usuário: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao atualizar usuário"
            )

    async def update_password(
        self,
        user_id: str,
        current_password: str,
        new_password: str
    ) -> bool:
        """
        Atualiza a senha do usuário

        Args:
            user_id: ID do usuário
            current_password: Senha atual
            new_password: Nova senha

        Returns:
            True se a senha foi atualizada com sucesso

        Raises:
            HTTPException: Se a senha atual estiver incorreta
        """
        # Busca o usuário
        user_doc = await self._get_user_document(user_id)
        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )

        # Verifica a senha atual
        if not verify_password(current_password, user_doc.get("hashed_password", "")):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Senha atual incorreta"
            )

        try:
            # Cria hash da nova senha
            hashed_password = get_password_hash(new_password)

            # Atualiza senha no Appwrite
            self.databases.update_document(
                database_id=self.database_id,
                collection_id=self.collection_id,
                document_id=user_id,
                data={
                    "hashed_password": hashed_password,
                    "updated_at": datetime.utcnow().isoformat()
                }
            )

            logger.info(f"Senha atualizada com sucesso para usuário: {user_id}")
            return True

        except AppwriteException as e:
            logger.error(f"Erro ao atualizar senha: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao atualizar senha"
            )

    async def authenticate_user(
        self,
        email: str,
        password: str
    ) -> Optional[User]:
        """
        Autentica um usuário com email e senha

        Args:
            email: Email do usuário
            password: Senha do usuário

        Returns:
            User se autenticado com sucesso, None caso contrário

        Raises:
            HTTPException: Se o usuário não estiver autorizado
        """
        user_doc = await self._get_user_document_by_email(email)
        if not user_doc:
            return None

        # Verifica a senha
        if not verify_password(password, user_doc.get("hashed_password", "")):
            return None

        user = self._document_to_user(user_doc)

        # Verifica se o usuário está autorizado
        if not user.is_authorized:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuário aguardando autorização do administrador. Entre em contato com o suporte."
            )

        return user

    async def authorize_user(
        self,
        user_id: str,
        is_authorized: bool
    ) -> User:
        """
        Autoriza ou revoga autorização de um usuário

        Args:
            user_id: ID do usuário
            is_authorized: True para autorizar, False para revogar

        Returns:
            Usuário atualizado

        Raises:
            HTTPException: Se o usuário não for encontrado
        """
        # Verifica se o usuário existe
        user = await self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )

        try:
            # Atualiza autorização no Appwrite
            doc = self.databases.update_document(
                database_id=self.database_id,
                collection_id=self.collection_id,
                document_id=user_id,
                data={
                    "is_authorized": is_authorized,
                    "updated_at": datetime.utcnow().isoformat()
                }
            )

            action = "autorizado" if is_authorized else "revogado"
            logger.info(f"Usuário {action}: {user.email}")
            return self._document_to_user(doc)

        except AppwriteException as e:
            logger.error(f"Erro ao autorizar usuário: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao atualizar autorização do usuário"
            )

    async def set_superuser(
        self,
        user_id: str,
        is_superuser: bool
    ) -> User:
        """
        Define ou remove permissões de superusuário

        Args:
            user_id: ID do usuário
            is_superuser: True para tornar superuser, False para remover

        Returns:
            Usuário atualizado

        Raises:
            HTTPException: Se o usuário não for encontrado
        """
        # Verifica se o usuário existe
        user = await self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )

        try:
            # Atualiza permissão de superuser no Appwrite
            doc = self.databases.update_document(
                database_id=self.database_id,
                collection_id=self.collection_id,
                document_id=user_id,
                data={
                    "is_superuser": is_superuser,
                    "updated_at": datetime.utcnow().isoformat()
                }
            )

            action = "promovido a superusuário" if is_superuser else "removido de superusuário"
            logger.info(f"Usuário {action}: {user.email}")
            return self._document_to_user(doc)

        except AppwriteException as e:
            logger.error(f"Erro ao atualizar permissões de superusuário: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao atualizar permissões de superusuário"
            )

    async def list_pending_users(self) -> List[User]:
        """
        Lista usuários pendentes de autorização

        Returns:
            Lista de usuários não autorizados
        """
        try:
            result = self.databases.list_documents(
                database_id=self.database_id,
                collection_id=self.collection_id,
                queries=[
                    Query.equal("is_authorized", False),
                    Query.limit(100)
                ]
            )

            return [self._document_to_user(doc) for doc in result['documents']]

        except AppwriteException as e:
            logger.error(f"Erro ao listar usuários pendentes: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao listar usuários pendentes"
            )

    async def delete_user(self, user_id: str) -> bool:
        """
        Deleta um usuário (soft delete - marca como inativo)

        Args:
            user_id: ID do usuário

        Returns:
            True se deletado com sucesso
        """
        try:
            self.databases.update_document(
                database_id=self.database_id,
                collection_id=self.collection_id,
                document_id=user_id,
                data={
                    "is_active": False,
                    "updated_at": datetime.utcnow().isoformat()
                }
            )

            logger.info(f"Usuário desativado com sucesso: {user_id}")
            return True

        except AppwriteException as e:
            logger.error(f"Erro ao desativar usuário: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao desativar usuário"
            )

    async def list_users(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_superuser: Optional[bool] = None
    ) -> List[User]:
        """
        Lista usuários com paginação e filtros

        Args:
            skip: Número de registros a pular
            limit: Número máximo de registros
            search: Buscar por nome ou email
            is_active: Filtrar por status ativo
            is_superuser: Filtrar por superusuário

        Returns:
            Lista de usuários
        """
        try:
            queries = [
                Query.offset(skip),
                Query.limit(limit)
            ]

            # Adicionar filtros se especificados
            if is_active is not None:
                queries.append(Query.equal("is_active", is_active))

            if is_superuser is not None:
                queries.append(Query.equal("is_superuser", is_superuser))

            result = self.databases.list_documents(
                database_id=self.database_id,
                collection_id=self.collection_id,
                queries=queries
            )

            users = [self._document_to_user(doc) for doc in result['documents']]

            # Filtro de busca por nome ou email (feito em memória pois Appwrite não suporta busca full-text bem)
            if search:
                search_lower = search.lower()
                users = [
                    u for u in users
                    if search_lower in u.nome.lower() or search_lower in u.email.lower()
                ]

            return users

        except AppwriteException as e:
            logger.error(f"Erro ao listar usuários: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao listar usuários"
            )

    # Métodos auxiliares privados

    async def _get_user_document(self, user_id: str):
        """Busca documento do usuário por ID"""
        try:
            return self.databases.get_document(
                database_id=self.database_id,
                collection_id=self.collection_id,
                document_id=user_id
            )
        except AppwriteException as e:
            if e.code == 404:
                return None
            raise

    async def _get_user_document_by_email(self, email: str):
        """Busca documento do usuário por email"""
        try:
            result = self.databases.list_documents(
                database_id=self.database_id,
                collection_id=self.collection_id,
                queries=[Query.equal("email", email.lower())]
            )
            return result['documents'][0] if result['total'] > 0 else None
        except AppwriteException:
            return None

    def _document_to_user(self, doc: dict) -> User:
        """Converte documento do Appwrite para modelo User"""
        return User(
            id=doc['$id'],
            email=doc.get('email', ''),
            nome=doc.get('nome', ''),
            is_active=doc.get('is_active', True),
            is_authorized=doc.get('is_authorized', False),
            is_superuser=doc.get('is_superuser', False),
            created_at=datetime.fromisoformat(doc.get('created_at', datetime.utcnow().isoformat())),
            updated_at=datetime.fromisoformat(doc.get('updated_at')) if doc.get('updated_at') else None
        )
