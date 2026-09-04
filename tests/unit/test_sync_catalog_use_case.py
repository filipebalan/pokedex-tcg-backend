import pytest
from unittest.mock import AsyncMock
from uuid import uuid4
from src.application.use_cases.sync_catalog_use_case import SyncCatalogUseCase
from src.domain.entities.set import Set
from datetime import date

@pytest.mark.asyncio
async def test_sync_all_sets_deve_buscar_da_api_e_salvar_no_repositorio() -> None:
    # 1. Eu configuro o mock do cliente HTTP simulando a resposta da pokemontcg.io
    mock_client = AsyncMock()
    mock_client.get_sets.return_value = [
        {
            "id": "base1",
            "name": "Base",
            "series": "Base",
            "releaseDate": "1999/01/09",
            "total": 102
        }
    ]

    # 2. Eu configuro os repositórios mockados
    mock_set_repo = AsyncMock()
    mock_set_repo.find_by_external_id.return_value = None  # Não existe ainda no banco
    mock_card_repo = AsyncMock()

    # 3. Eu instancio o caso de uso e executo
    use_case = SyncCatalogUseCase(
        set_repo=mock_set_repo,
        card_repo=mock_card_repo,
        client=mock_client
    )

    sets_sincronizados = await use_case.sync_all_sets()

    # 4. Eu valido os comportamentos
    assert len(sets_sincronizados) == 1
    assert sets_sincronizados[0].name == "Base"
    assert sets_sincronizados[0].external_id == "base1"
    assert sets_sincronizados[0].total_cards == 102

    # Eu garanto que o método save() do repositório foi invocado com a entidade correta
    mock_set_repo.save.assert_awaited_once()