from uuid import uuid4
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.database.session import get_db_session
from src.domain.entities.user import User
from src.domain.entities.user_collection import UserCollection
from src.domain.repositories.card_repository import CardRepository
from src.domain.repositories.price_snapshot_repository import PriceSnapshotRepository
from src.domain.repositories.user_collection_repository import UserCollectionRepository
from src.application.use_cases.calculate_collection_value_use_case import CalculateCollectionValueUseCase
from src.infrastructure.web.dependencies import (
    get_current_user,
    get_card_repository,
    get_price_snapshot_repository,
    get_user_collection_repository
)
from src.infrastructure.web.dtos.portfolio_dtos import AddCardToPortfolioRequestDTO
from src.infrastructure.web.dtos.collection_dtos import (
    CollectionValuationResponseDTO,
    CollectionItemValuationDTO
)

router = APIRouter(prefix="/portfolio", tags=["Portfolio"])

@router.get(
    "",
    response_model=CollectionValuationResponseDTO,
    summary="Consultar o portfólio salvo do usuário autenticado com valor atual de mercado"
)
async def get_my_portfolio(
    current_user: User = Depends(get_current_user),
    collection_repo: UserCollectionRepository = Depends(get_user_collection_repository),
    card_repo: CardRepository = Depends(get_card_repository),
    price_repo: PriceSnapshotRepository = Depends(get_price_snapshot_repository)
) -> CollectionValuationResponseDTO:
    # 1. Eu busco a coleção persistida deste usuário específico
    collection = await collection_repo.find_by_user_id(current_user.id)
    if not collection:
        collection = UserCollection(id=uuid4(), user_id=current_user.id)

    # 2. Eu reaproveito diretamente o motor de cálculo da Fase 4 (Open/Closed Principle)
    items_to_calc = [(item.card_id, item.quantity) for item in collection.items]
    use_case = CalculateCollectionValueUseCase(card_repo=card_repo, price_repo=price_repo)
    result = await use_case.calculate(items_to_calc)

    items_output = [
        CollectionItemValuationDTO(
            card_id=item.card_id,
            card_name=item.card_name,
            quantity=item.quantity,
            unit_price=item.unit_price.amount if item.unit_price else None,
            subtotal=item.subtotal.amount if item.subtotal else None,
            currency=item.unit_price.currency if item.unit_price else "USD",
            price_date=item.price_date
        )
        for item in result.items
    ]

    return CollectionValuationResponseDTO(
        total_value=result.total_value.amount,
        currency=result.total_value.currency,
        total_cards_count=result.total_cards_count,
        priced_items_count=result.priced_items_count,
        unpriced_items_count=result.unpriced_items_count,
        items=items_output
    )

@router.post(
    "/items",
    status_code=status.HTTP_201_CREATED,
    summary="Adicionar carta à coleção do usuário logado"
)
async def add_card_to_portfolio(
    payload: AddCardToPortfolioRequestDTO,
    current_user: User = Depends(get_current_user),
    collection_repo: UserCollectionRepository = Depends(get_user_collection_repository),
    session: AsyncSession = Depends(get_db_session)
) -> dict[str, str]:
    collection = await collection_repo.find_by_user_id(current_user.id)
    if not collection:
        collection = UserCollection(id=uuid4(), user_id=current_user.id)

    collection.add_or_update_card(payload.card_id, payload.quantity)
    await collection_repo.save(collection)
    await session.commit()

    return {"message": "Carta adicionada ao portfólio com sucesso."}