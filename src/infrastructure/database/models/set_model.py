import uuid
from datetime import date
from sqlalchemy import String, Integer, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.infrastructure.database.models.base import Base

class SetModel(Base):
    __tablename__ = "sets"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    external_id: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    series: Mapped[str] = mapped_column(String(100), nullable=False)
    release_date: Mapped[date] = mapped_column(Date, nullable=False)
    total_cards: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relacionamento 1:N com as cartas
    cards: Mapped[list["CardModel"]] = relationship(back_populates="set", cascade="all, delete-orphan")