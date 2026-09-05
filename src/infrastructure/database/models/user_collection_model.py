import uuid
from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.infrastructure.database.models.base import Base

class UserCollectionModel(Base):
    __tablename__ = "user_collections"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False, default="Minha Coleção")

    # Relacionamento 1:N com itens da coleção
    items: Mapped[list["UserCollectionItemModel"]] = relationship(
        back_populates="collection",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

class UserCollectionItemModel(Base):
    __tablename__ = "user_collection_items"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    collection_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user_collections.id", ondelete="CASCADE"), index=True, nullable=False)
    card_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("cards.id", ondelete="CASCADE"), index=True, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    collection: Mapped["UserCollectionModel"] = relationship(back_populates="items")