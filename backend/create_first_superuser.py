#!/usr/bin/env python3
"""
Script para criar o primeiro superusuário autorizado (SQLite)
"""
import sys
import os
from datetime import datetime
from getpass import getpass
from pathlib import Path

# Adiciona o diretório ao path para importar módulos do app
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import get_password_hash
from app.models.db_models import UserDB
from app.core.database import Base


def validate_email(email: str) -> bool:
    return '@' in email and '.' in email


def validate_password(password: str) -> bool:
    if len(password) < 8:
        print("Senha deve ter no minimo 8 caracteres")
        return False
    if not any(c.isupper() for c in password):
        print("Senha deve conter ao menos uma letra maiuscula")
        return False
    if not any(c.islower() for c in password):
        print("Senha deve conter ao menos uma letra minuscula")
        return False
    if not any(c.isdigit() for c in password):
        print("Senha deve conter ao menos um numero")
        return False
    return True


def main():
    # Usa engine sincrono (sqlite:/// sem aiosqlite)
    sync_url = settings.SQLITE_URL.replace("sqlite+aiosqlite", "sqlite")
    engine = create_engine(sync_url, echo=False)

    # Cria tabelas se nao existirem
    Base.metadata.create_all(engine)

    print("=" * 60)
    print("CRIAR PRIMEIRO SUPERUSUARIO")
    print("=" * 60)
    print()

    with Session(engine) as session:
        # Verifica se ja existem superusuarios
        existing_super = session.execute(
            select(UserDB).where(UserDB.is_superuser == True)  # noqa: E712
        ).scalar_one_or_none()

        if existing_super:
            print(f"Ja existe pelo menos um superusuario no sistema:")
            print(f"   Email: {existing_super.email}")
            print(f"   Nome: {existing_super.nome}")
            print()
            response = input("Deseja criar outro superusuario? (s/n): ")
            if response.lower() != 's':
                print("Operacao cancelada.")
                return

        # Coleta informacoes do superusuario
        print("Digite os dados do superusuario:")
        print()

        while True:
            email = input("Email: ").strip()
            if validate_email(email):
                break
            print("Email invalido. Tente novamente.")

        nome = input("Nome completo: ").strip()
        if not nome:
            nome = "Administrador"

        while True:
            password = getpass("Senha (minimo 8 caracteres, com maiuscula, minuscula e numero): ")
            if validate_password(password):
                password_confirm = getpass("Confirme a senha: ")
                if password == password_confirm:
                    break
                print("As senhas nao conferem. Tente novamente.")
            else:
                print("Tente novamente.")

        print()
        print("Resumo:")
        print(f"   Email: {email}")
        print(f"   Nome: {nome}")
        print(f"   Superusuario: Sim")
        print(f"   Autorizado: Sim")
        print()

        response = input("Confirma a criacao? (s/n): ")
        if response.lower() != 's':
            print("Operacao cancelada.")
            return

        # Verifica se ja existe usuario com este email
        existing = session.execute(
            select(UserDB).where(UserDB.email == email.lower())
        ).scalar_one_or_none()

        if existing:
            print(f"Ja existe um usuario com o email {email}")
            sys.exit(1)

        now = datetime.utcnow()
        user = UserDB(
            email=email.lower(),
            nome=nome,
            hashed_password=get_password_hash(password),
            is_active=True,
            is_authorized=True,
            is_superuser=True,
            created_at=now,
            updated_at=now,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        print()
        print("Superusuario criado com sucesso!")
        print()
        print("Detalhes:")
        print(f"   ID: {user.id}")
        print(f"   Email: {user.email}")
        print(f"   Nome: {user.nome}")
        print()
        print("Voce ja pode fazer login com este usuario!")


if __name__ == "__main__":
    main()
