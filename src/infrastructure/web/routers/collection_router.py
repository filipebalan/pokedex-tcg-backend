from fastapi import APIRouter, Depends
from src.domain.repositories.card_repository import CardRepository
from src.domain.repositories.price_snapshot_repository import PriceSnapshotRepository
from src.application.use_cases.calculate_collection_value_use_case import CalculateCollectionValueUseCase
from src.infrastructure.web.dependencies import get_card_repository, get_price_snapshot_repository
from src.infrastructure.web.dtos.collection_dtos import (
    CalculateCollectionRequestDTO,
    CollectionValuationResponseDTO,
    CollectionItemValuationDTO
)
from src.infrastructure.web.middlewares.rate_limiter import RateLimiter

router = APIRouter(prefix="/collection", tags=["Collection"])
rate_limiter = RateLimiter(requests_per_minute=60)

@router.post(
    "/value",
    response_model=CollectionValuationResponseDTO,
    summary="Calcular valor total de mercado de uma coleção de cartas",
    dependencies=[Depends(rate_limiter)]
)
async def calculate_collection_value(
    payload: CalculateCollectionRequestDTO,
    card_repo: CardRepository = Depends(get_card_repository),
    price_repo: PriceSnapshotRepository = Depends(get_price_snapshot_repository)
) -> CollectionValuationResponseDTO:
    use_case = CalculateCollectionValueUseCase(
        card_repo=card_repo,
        price_repo=price_repo
    )

    # Eu converto os DTOs para tuplas (card_id, quantidade) esperadas pelo caso de uso
    items_input = [(item.card_id, item.quantity) for item in payload.items]
    result = await use_case.calculate(items_input)

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