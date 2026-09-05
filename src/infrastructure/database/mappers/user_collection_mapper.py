from uuid import uuid4
from src.domain.entities.user_collection import UserCollection, UserCollectionItem
from src.infrastructure.database.models.user_collection_model import UserCollectionModel, UserCollectionItemModel

class UserCollectionMapper:
    @staticmethod
    def to_domain(model: UserCollectionModel) -> UserCollection:
        domain_items = [
            UserCollectionItem(
                card_id=item.card_id,
                quantity=item.quantity,
                added_at=item.added_at,
            )
            for item in model.items
        ]

        return UserCollection(
            id=model.id,
            user_id=model.user_id,
            name=model.name,
            items=domain_items,
        )

    @staticmethod
    def to_model(entity: UserCollection) -> UserCollectionModel:
        collection_model = UserCollectionModel(
            id=entity.id,
            user_id=entity.user_id,
            name=entity.name,
        )

        collection_model.items = [
            UserCollectionItemModel(
                id=uuid4(),
                collection_id=entity.id,
                card_id=item.card_id,
                quantity=item.quantity,
                added_at=item.added_at,
            )
            for item in entity.items
        ]

        return collection_model