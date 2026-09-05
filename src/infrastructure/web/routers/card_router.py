from typing import Optional
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, Query, HTTPException, status, Response
from src.domain.repositories.card_repository import CardRepository
from src.domain.repositories.price_snapshot_repository import PriceSnapshotRepository
from src.infrastructure.cache.price_history_cache import PriceHistoryCacheService
from src.infrastructure.web.dependencies import (
    get_card_repository,
    get_price_snapshot_repository,
    get_price_history_cache_service
)
from src.infrastructure.web.dtos.card_dtos import CardResponseDTO, PaginatedCardsResponseDTO
from src.infrastructure.web.dtos.price_dtos import CardPriceHistoryResponseDTO, PricePointDTO
from src.infrastructure.web.middlewares.rate_limiter import RateLimiter

router = APIRouter(prefix="/cards", tags=["Cards"])
rate_limiter = RateLimiter(requests_per_minute=60)

@router.get(
    "",
    response_model=PaginatedCardsResponseDTO,
    summary="Listar cartas com filtros e paginação",
    dependencies=[Depends(rate_limiter)]
)
async def list_cards(
    set_id: Optional[UUID] = Query(None, description="Filtrar por ID interno do Set"),
    name: Optional[str] = Query(None, description="Filtrar por parte do nome da carta"),
    rarity: Optional[str] = Query(None, description="Filtrar por raridade (ex: Rare Holo)"),
    limit: int = Query(50, ge=1, le=250, description="Quantidade de registros por página"),
    offset: int = Query(0, ge=0, description="Deslocamento para paginação"),
    repo: CardRepository = Depends(get_card_repository)
) -> PaginatedCardsResponseDTO:
    domain_cards = await repo.list_cards(
        set_id=set_id,
        name=name,
        rarity=rarity,
        limit=limit,
        offset=offset
    )

    items = [
        CardResponseDTO(
            id=c.id,
            external_id=c.external_id,
            name=c.name,
            set_id=c.set_id,
            card_number=c.card_number,
            rarity=c.rarity,
            supertype=c.supertype.value,
            types=[t.value for t in c.types],
            hp=c.hp,
            national_dex_number=c.national_dex_number,
        )
        for c in domain_cards
    ]

    return PaginatedCardsResponseDTO(
        total=len(items),
        limit=limit,
        offset=offset,
        items=items
    )

@router.get(
    "/{card_id}/price-history",
    response_model=CardPriceHistoryResponseDTO,
    summary="Obter histórico de preços da carta (com Cache Redis)",
    dependencies=[Depends(rate_limiter)]
)
async def get_card_price_history(
    card_id: UUID,
    response: Response,
    start_date: Optional[datetime] = Query(None, description="Data inicial do filtro"),
    end_date: Optional[datetime] = Query(None, description="Data final do filtro"),
    card_repo: CardRepository = Depends(get_card_repository),
    price_repo: PriceSnapshotRepository = Depends(get_price_snapshot_repository),
    cache_service: PriceHistoryCacheService = Depends(get_price_history_cache_service)
) -> CardPriceHistoryResponseDTO:
    # 1. Eu consulto o cache do Redis primeiro (Cache-Aside)
    cached_dto = await cache_service.get(card_id, start_date, end_date)
    if cached_dto:
        response.headers["X-Cache"] = "HIT"
        return cached_dto

    # 2. Se for Cache MISS, eu valido a existência da carta no banco
    card = await card_repo.find_by_id(card_id)
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Carta com ID '{card_id}' não encontrada."
        )

    # 3. Eu busco a série temporal no PostgreSQL
    snapshots = await price_repo.list_by_card_id(
        card_id=card_id,
        start_date=start_date,
        end_date=end_date
    )

    history = [
        PricePointDTO(
            captured_at=s.captured_at,
            source=s.source,
            currency=s.market.currency,
            market=s.market.amount,
            low=s.low.amount if s.low else None,
            high=s.high.amount if s.high else None,
        )
        for s in snapshots
    ]

    result_dto = CardPriceHistoryResponseDTO(
        card_id=card_id,
        total_points=len(history),
        history=history
    )

    # 4. Eu populo o Redis com o resultado para as próximas requisições
    await cache_service.set(card_id, result_dto, start_date, end_date)
    response.headers["X-Cache"] = "MISS"

    return result_dto