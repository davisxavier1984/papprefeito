"""
Modelos SQLAlchemy para o banco de dados SQLite
"""
import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, Integer, Text, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class UserDB(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_authorized: Mapped[bool] = mapped_column(Boolean, default=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class EdicaoDB(Base):
    __tablename__ = "edicoes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codigo_municipio: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    competencia: Mapped[str] = mapped_column(String(6), nullable=False)
    perda_recurso_mensal: Mapped[str] = mapped_column(Text, nullable=False)  # JSON string
    usuario_id: Mapped[str] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("codigo_municipio", "competencia", name="uq_municipio_competencia"),
    )


class HistoricoPerdaDB(Base):
    """Histórico append-only de cada gravação de perdas (nunca é atualizado nem apagado)."""
    __tablename__ = "historico_perdas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codigo_ibge: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    competencia: Mapped[str] = mapped_column(String(6), nullable=False, index=True)
    usuario_id: Mapped[str] = mapped_column(String(36), nullable=True, index=True)
    operacao: Mapped[str] = mapped_column(String(10), nullable=False)  # create | update | upsert | delete
    perda_recurso_mensal: Mapped[str] = mapped_column(Text, nullable=False)  # JSON
    itens: Mapped[str] = mapped_column(Text, nullable=True)  # JSON
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)


class ValorReferenciaDB(Base):
    """Valor de referência do financiamento federal por vigência (story 3.3).

    Cada linha vale a partir de `vigente_desde` (AAAAMM) até a próxima vigência da mesma chave.
    """
    __tablename__ = "valores_referencia"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chave: Mapped[str] = mapped_column(String(60), nullable=False, index=True)
    vigente_desde: Mapped[str] = mapped_column(String(6), nullable=False)
    valor: Mapped[str] = mapped_column(String(30), nullable=False)  # decimal como texto
    fonte: Mapped[str] = mapped_column(String(255), nullable=True)
    usuario_id: Mapped[str] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("chave", "vigente_desde", name="uq_valor_referencia_vigencia"),
    )


class RespostaMinisterioDB(Base):
    """Última resposta da API de financiamento do Ministério por município e competência.

    Base do painel de acerto e dos municípios parecidos (aprendizado com o consultor).
    """
    __tablename__ = "respostas_ministerio"

    codigo_ibge: Mapped[str] = mapped_column(String(10), primary_key=True)
    competencia: Mapped[str] = mapped_column(String(6), primary_key=True)
    resposta: Mapped[str] = mapped_column(Text, nullable=False)  # JSON bruto
    atualizado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
