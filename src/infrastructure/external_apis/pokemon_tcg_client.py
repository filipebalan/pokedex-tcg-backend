import asyncio
from typing import Any, Optional
import httpx
from src.infrastructure.config.settings import settings

class PokemonTcgClient:
    BASE_URL = "https://api.pokemontcg.io/v2"

    def __init__(self, api_key: Optional[str] = None) -> None:
        # Eu priorizo a chave injetada ou utilizo a chave configurada no .env
        self._api_key = api_key or settings.POKEMON_TCG_API_KEY
        self._headers = {"User-Agent": "PokedexTCG/1.0"}
        if self._api_key:
            # Cabeçalho oficial exigido pela pokemontcg.io v2
            self._headers["X-Api-Key"] = self._api_key

    async def _get(self, endpoint: str, params: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        url = f"{self.BASE_URL}{endpoint}"
        max_retries = 3
        backoff_seconds = 2

        # Eu utilizo o cliente assíncrono httpx.AsyncClient com timeout defensivo
        async with httpx.AsyncClient(timeout=30.0, headers=self._headers) as client:
            for tentativa in range(max_retries):
                response = await client.get(url, params=params)

                # Se a API externa nos limitar (HTTP 429), eu aguardo com backoff exponencial
                if response.status_code == 429:
                    await asyncio.sleep(backoff_seconds * (tentativa + 1))
                    continue

                response.raise_for_status()
                return response.json()

            raise httpx.HTTPStatusError("Limite de requisições excedido após múltiplas tentativas.", request=response.request, response=response)

    async def get_sets(self) -> list[dict[str, Any]]:
        # Eu busco a listagem de todas as coleções oficiais
        payload = await self._get("/sets")
        return payload.get("data", [])

    async def get_cards_by_set(self, external_set_id: str, page: int = 1, page_size: int = 250) -> dict[str, Any]:
        # Eu busco cartas de uma coleção específica com paginação
        params = {
            "q": f"set.id:{external_set_id}",
            "page": page,
            "pageSize": page_size
        }
        return await self._get("/cards", params=params)