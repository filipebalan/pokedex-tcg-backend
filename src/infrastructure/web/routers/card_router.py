from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from src.domain.repositories.card_repository import CardRepository
from src.infrastructure.web.dependencies import get_card_repository
from src.infrastructure.web.dtos.card_dtos import CardResponseDTO, PaginatedCardsResponseDTO
from src.infrastructure.web.middlewares.rate_limiter import RateLimiter

router = APIRouter(prefix="/cards", tags=["Cards"])

# Instância da proteção de rate limit injetável (60 requisições por minuto)
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
    # Eu busco as cartas aplicando os filtros através do repositório
    domain_cards = await repo.list_cards(
        set_id=set_id,
        name=name,
        rarity=rarity,
        limit=limit,
        offset=offset
    )

    # Eu converto as Entidades de Domínio para DTOs de resposta da API
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