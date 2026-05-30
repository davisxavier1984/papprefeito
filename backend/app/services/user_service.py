"""
Serviço para gerenciamento de usuários usando SQLAlchemy async
"""
from typing import Optional, List
from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash, verify_password
from app.models.schemas import User, UserCreate, UserUpdate
from app.models.db_models import UserDB
from app.utils.logger import logger

# Hash bcrypt fixo para comparação em tempo ~constante quando o e-mail não existe
# (mitiga enumeração de usuários por timing no login)
_DUMMY_PASSWORD_HASH = get_password_hash("invalid-timing-equalizer")


class UserService:
    """Serviço para operações de usuários"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        result = await self.session.execute(
            select(UserDB).where(UserDB.id == user_id)
        )
        row = result.scalar_one_or_none()
        if not row:
            return None
        return self._row_to_user(row)

    async def get_user_by_email(self, email: str) -> Optional[User]:
        result = await self.session.execute(
            select(UserDB).where(UserDB.email == email.lower())
        )
        row = result.scalar_one_or_none()
        if not row:
            return None
        return self._row_to_user(row)

    async def create_user(self, user_data: UserCreate) -> User:
        existing_user = await self.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já cadastrado"
            )

        hashed_password = get_password_hash(user_data.password)
        now = datetime.utcnow()

        row = UserDB(
            email=user_data.email.lower(),
            nome=user_data.nome,
            hashed_password=hashed_password,
            is_active=True,
            is_authorized=False,
            is_superuser=False,
            created_at=now,
            updated_at=now,
        )
        self.session.add(row)
        await self.session.commit()
        await self.session.refresh(row)

        logger.info(f"Usuário criado com sucesso: {row.id}")
        return self._row_to_user(row)

    async def update_user(self, user_id: str, user_data: UserUpdate) -> User:
        result = await self.session.execute(
            select(UserDB).where(UserDB.id == user_id)
        )
        row = result.scalar_one_or_none()
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )

        if user_data.email and user_data.email.lower() != row.email:
            existing = await self.get_user_by_email(user_data.email)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email já cadastrado"
                )

        if user_data.nome is not None:
            row.nome = user_data.nome
        if user_data.email is not None:
            row.email = user_data.email.lower()
        if user_data.is_active is not None:
            row.is_active = user_data.is_active
        if user_data.is_authorized is not None:
            row.is_authorized = user_data.is_authorized
        if user_data.is_superuser is not None:
            row.is_superuser = user_data.is_superuser
        row.updated_at = datetime.utcnow()

        await self.session.commit()
        await self.session.refresh(row)

        logger.info(f"Usuário atualizado com sucesso: {user_id}")
        return self._row_to_user(row)

    async def update_password(
        self,
        user_id: str,
        current_password: str,
        new_password: str
    ) -> bool:
        result = await self.session.execute(
            select(UserDB).where(UserDB.id == user_id)
        )
        row = result.scalar_one_or_none()
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )

        if not verify_password(current_password, row.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Senha atual incorreta"
            )

        row.hashed_password = get_password_hash(new_password)
        row.updated_at = datetime.utcnow()
        await self.session.commit()

        logger.info(f"Senha atualizada com sucesso para usuário: {user_id}")
        return True

    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        result = await self.session.execute(
            select(UserDB).where(UserDB.email == email.lower())
        )
        row = result.scalar_one_or_none()
        if not row:
            # Verificação dummy em tempo ~constante (evita enumeração por timing)
            verify_password(password, _DUMMY_PASSWORD_HASH)
            return None

        if not verify_password(password, row.hashed_password):
            return None

        user = self._row_to_user(row)

        if not user.is_authorized:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuário aguardando autorização do administrador. Entre em contato com o suporte."
            )

        return user

    async def authorize_user(self, user_id: str, is_authorized: bool) -> User:
        result = await self.session.execute(
            select(UserDB).where(UserDB.id == user_id)
        )
        row = result.scalar_one_or_none()
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )

        row.is_authorized = is_authorized
        row.updated_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(row)

        action = "autorizado" if is_authorized else "revogado"
        logger.info(f"Usuário {action}: {row.email}")
        return self._row_to_user(row)

    async def set_superuser(self, user_id: str, is_superuser: bool) -> User:
        result = await self.session.execute(
            select(UserDB).where(UserDB.id == user_id)
        )
        row = result.scalar_one_or_none()
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )

        row.is_superuser = is_superuser
        row.updated_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(row)

        action = "promovido a superusuário" if is_superuser else "removido de superusuário"
        logger.info(f"Usuário {action}: {row.email}")
        return self._row_to_user(row)

    async def list_pending_users(self) -> List[User]:
        result = await self.session.execute(
            select(UserDB).where(UserDB.is_authorized == False)  # noqa: E712
        )
        rows = result.scalars().all()
        return [self._row_to_user(r) for r in rows]

    async def delete_user(self, user_id: str) -> bool:
        result = await self.session.execute(
            select(UserDB).where(UserDB.id == user_id)
        )
        row = result.scalar_one_or_none()
        if not row:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao desativar usuário"
            )

        row.is_active = False
        row.updated_at = datetime.utcnow()
        await self.session.commit()

        logger.info(f"Usuário desativado com sucesso: {user_id}")
        return True

    async def list_users(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_superuser: Optional[bool] = None
    ) -> List[User]:
        stmt = select(UserDB)

        if is_active is not None:
            stmt = stmt.where(UserDB.is_active == is_active)
        if is_superuser is not None:
            stmt = stmt.where(UserDB.is_superuser == is_superuser)
        if search:
            pattern = f"%{search}%"
            stmt = stmt.where(
                UserDB.nome.ilike(pattern) | UserDB.email.ilike(pattern)
            )

        stmt = stmt.offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        rows = result.scalars().all()
        return [self._row_to_user(r) for r in rows]

    @staticmethod
    def _row_to_user(row: UserDB) -> User:
        return User(
            id=row.id,
            email=row.email,
            nome=row.nome,
            is_active=row.is_active,
            is_authorized=row.is_authorized,
            is_superuser=row.is_superuser,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )
