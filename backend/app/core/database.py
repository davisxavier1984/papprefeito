"""
Configuração do banco de dados SQLite com SQLAlchemy async
"""
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings


engine = create_async_engine(settings.SQLITE_URL, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_session() -> AsyncSession:
    """Dependency para injetar sessão do banco."""
    async with async_session() as session:
        yield session


async def init_db():
    """Cria todas as tabelas no startup."""
    from app.models.db_models import UserDB, EdicaoDB  # noqa: F401
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
