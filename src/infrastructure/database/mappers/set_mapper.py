from src.domain.entities.set import Set
from src.infrastructure.database.models.set_model import SetModel

class SetMapper:
    @staticmethod
    def to_domain(model: SetModel) -> Set:
        # Eu converto o modelo relacional do SQLAlchemy para a Entidade rica do Domínio
        return Set(
            id=model.id,
            external_id=model.external_id,
            name=model.name,
            series=model.series,
            release_date=model.release_date,
            total_cards=model.total_cards,
        )

    @staticmethod
    def to_model(entity: Set) -> SetModel:
        # Eu converto a Entidade do Domínio para o modelo relacional pronto para persistência
        return SetModel(
            id=entity.id,
            external_id=entity.external_id,
            name=entity.name,
            series=entity.series,
            release_date=entity.release_date,
            total_cards=entity.total_cards,
        )