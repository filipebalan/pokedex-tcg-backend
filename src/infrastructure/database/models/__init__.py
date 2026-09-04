# Eu garanto que todos os modelos relacionais sejam carregados no registro do SQLAlchemy
from src.infrastructure.database.models.base import Base
from src.infrastructure.database.models.set_model import SetModel
from src.infrastructure.database.models.card_model import CardModel
from src.infrastructure.database.models.price_snapshot_model import PriceSnapshotModel

__all__ = ["Base", "SetModel", "CardModel", "PriceSnapshotModel"]