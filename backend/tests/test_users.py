"""Gestão de usuários: só o admin cria, sem fluxo de aprovação."""
import asyncio

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.database import Base
from app.models.db_models import UserDB
from app.models.schemas import UserCreate, UserUpdate
from app.services.user_service import UserService

SENHA = 'Senha123'


def _rodar(corrotina_fn):
    """Executa corrotina_fn(service, session) num SQLite em memória."""
    async def _main():
        engine = create_async_engine('sqlite+aiosqlite:///:memory:')
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        sessao = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        async with sessao() as session:
            resultado = await corrotina_fn(UserService(session), session)
        await engine.dispose()
        return resultado
    return asyncio.run(_main())


def test_usuario_criado_pelo_admin_ja_pode_entrar():
    async def fluxo(service, _):
        await service.create_user(UserCreate(email='ana@x.com', nome='Ana', password=SENHA))
        return await service.authenticate_user('ana@x.com', SENHA)

    user = _rodar(fluxo)
    assert user.is_authorized and user.is_active and not user.is_superuser


def test_criacao_respeita_perfil_administrador():
    async def fluxo(service, _):
        return await service.create_user(
            UserCreate(email='adm@x.com', nome='Adm', password=SENHA, is_superuser=True)
        )

    assert _rodar(fluxo).is_superuser


def test_ativar_libera_usuario_antigo_pendente():
    async def fluxo(service, session):
        row = UserDB(email='velho@x.com', nome='Velho', hashed_password='x',
                     is_active=True, is_authorized=False)
        session.add(row)
        await session.commit()
        return await service.update_user(row.id, UserUpdate(is_active=True))

    assert _rodar(fluxo).is_authorized


def test_cadastro_publico_removido():
    from main import app
    caminhos = {getattr(r, 'path', '') for r in app.routes}
    assert '/api/auth/register' not in caminhos
    # Desativar conta é só pelo admin
    assert not any(getattr(r, 'path', '') == '/api/auth/me' and 'DELETE' in getattr(r, 'methods', set())
                   for r in app.routes)
    assert '/api/auth/login' in caminhos


@pytest.mark.parametrize('campos', [
    {'is_superuser': False},
    {'is_active': False},
    {'is_authorized': False},
])
def test_admin_nao_remove_o_proprio_acesso(campos):
    from app.api.endpoints.users import update_user

    async def fluxo(service, _):
        admin = await service.create_user(
            UserCreate(email='adm@x.com', nome='Adm', password=SENHA, is_superuser=True)
        )
        with pytest.raises(HTTPException) as exc:
            await update_user(admin.id, UserUpdate(**campos), current_user=admin, user_service=service)
        return exc.value.status_code

    assert _rodar(fluxo) == 400
