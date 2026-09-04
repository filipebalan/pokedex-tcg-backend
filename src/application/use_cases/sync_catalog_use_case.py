from uuid import uuid4
from datetime import datetime
from typing import Any
from src.domain.entities.set import Set
from src.domain.entities.card import Card
from src.domain.value_objects.card_types import CardSupertype, EnergyType
from src.domain.repositories.set_repository import SetRepository
from src.domain.repositories.card_repository import CardRepository
from src.infrastructure.external_apis.pokemon_tcg_client import PokemonTcgClient

class SyncCatalogUseCase:
    def __init__(
        self,
        set_repo: SetRepository,
        card_repo: CardRepository,
        client: PokemonTcgClient
    ) -> None:
        # Eu recebo as dependências pelo construtor (Inversão de Dependência)
        self._set_repo = set_repo
        self._card_repo = card_repo
        self._client = client

    async def sync_all_sets(self) -> list[Set]:
        # Eu busco as coleções brutas da API externa
        raw_sets = await self._client.get_sets()
        synced_sets: list[Set] = []

        for data in raw_sets:
            external_id = data["id"]
            
            # Eu verifico se a coleção já existe no nosso banco para manter o ID interno estável
            existing = await self._set_repo.find_by_external_id(external_id)
            set_id = existing.id if existing else uuid4()

            # Eu converto a data que vem no formato 'YYYY/MM/DD'
            release_date = datetime.strptime(data["releaseDate"], "%Y/%m/%d").date()

            collection_set = Set(
                id=set_id,
                external_id=external_id,
                name=data["name"],
                series=data["series"],
                release_date=release_date,
                total_cards=data["total"],
            )

            # Eu salvo de forma idempotente
            await self._set_repo.save(collection_set)
            synced_sets.append(collection_set)

        return synced_sets

    async def sync_cards_for_set(self, external_set_id: str) -> list[Card]:
        # Eu garanto que o Set já exista no nosso banco local
        parent_set = await self._set_repo.find_by_external_id(external_set_id)
        if not parent_set:
            raise ValueError(f"Set com external_id '{external_set_id}' não encontrado no banco local.")

        page = 1
        synced_cards: list[Card] = []

        while True:
            response = await self._client.get_cards_by_set(external_set_id, page=page, page_size=250)
            raw_cards = response.get("data", [])
            if not raw_cards:
                break

            for data in raw_cards:
                card = self._parse_card(data, parent_set.id)
                await self._card_repo.save(card)
                synced_cards.append(card)

            # Eu verifico a paginação retornada pela pokemontcg.io v2
            total_count = response.get("totalCount", 0)
            page_size = response.get("pageSize", 250)
            if page * page_size >= total_count:
                break

            page += 1

        return synced_cards

    def _parse_card(self, data: dict[str, Any], internal_set_id: Any) -> Card:
        # Eu trato a conversão de HP que pode vir nulo ou como string (ex: '120')
        raw_hp = data.get("hp")
        hp: Optional[int] = None
        if raw_hp and raw_hp.isdigit():
            hp = int(raw_hp)

        # Eu mapeio os tipos elementais válidos ignorando strings corrompidas
        types: list[EnergyType] = []
        for t in data.get("types", []):
            try:
                types.append(EnergyType(t))
            except ValueError:
                pass

        # Eu mapeio o supertipo com fallback seguro
        raw_supertype = data.get("supertype", "Pokémon")
        try:
            supertype = CardSupertype(raw_supertype)
        except ValueError:
            supertype = CardSupertype.POKEMON

        # Eu obtenho o dex number se existir
        dex_numbers = data.get("nationalPokedexNumbers", [])
        national_dex = dex_numbers[0] if dex_numbers else None

        return Card(
            id=uuid4(),
            external_id=data["id"],
            name=data["name"],
            set_id=internal_set_id,
            card_number=str(data["number"]),
            rarity=data.get("rarity", "Common"),
            supertype=supertype,
            types=types,
            hp=hp,
            national_dex_number=national_dex,
        )