from src.domain.entities.card import Card
from src.domain.value_objects.card_types import CardSupertype, EnergyType
from src.infrastructure.database.models.card_model import CardModel

class CardMapper:
    @staticmethod
    def to_domain(model: CardModel) -> Card:
        # Eu reconstruo a lista de enums de tipo a partir das strings salvas no banco
        converted_types = [EnergyType(t) for t in model.types]

        return Card(
            id=model.id,
            external_id=model.external_id,
            name=model.name,
            set_id=model.set_id,
            card_number=model.card_number,
            rarity=model.rarity,
            supertype=CardSupertype(model.supertype),
            types=converted_types,
            hp=model.hp,
            national_dex_number=model.national_dex_number,
        )

    @staticmethod
    def to_model(entity: Card) -> CardModel:
        # Eu serializo os enums de EnergyType para lista de strings para o array do PostgreSQL
        raw_types = [t.value for t in entity.types]

        return CardModel(
            id=entity.id,
            external_id=entity.external_id,
            name=entity.name,
            set_id=entity.set_id,
            card_number=entity.card_number,
            rarity=entity.rarity,
            supertype=entity.supertype.value,
            types=raw_types,
            hp=entity.hp,
            national_dex_number=entity.national_dex_number,
        )