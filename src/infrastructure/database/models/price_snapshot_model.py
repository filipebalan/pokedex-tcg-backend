import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import String, ForeignKey, DateTime, Numeric, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.infrastructure.database.models.base import Base

class PriceSnapshotModel(Base):
    __tablename__ = "price_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    card_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("cards.id", ondelete="CASCADE"), nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(50), nullable=False)
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    
    # Eu utilizo Numeric(10, 2) para garantir precisão exata de moeda no banco de dados (evitando float)
    price_market: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    price_low: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    price_high: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)

    # Relacionamento
    card: Mapped["CardModel"] = relationship(back_populates="price_snapshots")

    # Eu crio um índice composto para que buscas de séries temporais de uma carta sejam ultra-rápidas
    __table_args__ = (
        Index("idx_price_snapshot_card_date", "card_id", "captured_at"),
    )