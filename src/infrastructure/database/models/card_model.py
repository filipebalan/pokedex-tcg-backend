import uuid
from typing import Optional
from sqlalchemy import String, Integer, ForeignKey, Index
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.infrastructure.database.models.base import Base

class CardModel(Base):
    __tablename__ = "cards"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    external_id: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    set_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sets.id", ondelete="CASCADE"), nullable=False, index=True)
    card_number: Mapped[str] = mapped_column(String(20), nullable=False)
    rarity: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    supertype: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Eu utilizo o tipo nativo ARRAY de Strings do PostgreSQL para salvar múltiplos tipos elementais
    types: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False, default=list)
    hp: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    national_dex_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)

    # Relacionamentos
    set: Mapped["SetModel"] = relationship(back_populates="cards")
    price_snapshots: Mapped[list["PriceSnapshotModel"]] = relationship(back_populates="card", cascade="all, delete-orphan")