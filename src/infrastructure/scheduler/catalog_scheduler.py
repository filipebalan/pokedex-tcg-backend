import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.infrastructure.database.session import async_session_factory
from src.infrastructure.database.repositories.sqlalchemy_set_repository import SQLAlchemySetRepository
from src.infrastructure.database.repositories.sqlalchemy_card_repository import SQLAlchemyCardRepository
from src.infrastructure.external_apis.pokemon_tcg_client import PokemonTcgClient
from src.application.use_cases.sync_catalog_use_case import SyncCatalogUseCase

logger = logging.getLogger(__name__)

class CatalogScheduler:
    def __init__(self) -> None:
        # Eu utilizo o AsyncIOScheduler para rodar perfeitamente integrado ao event loop do FastAPI
        self._scheduler = AsyncIOScheduler()

    async def execute_catalog_sync(self) -> None:
        logger.info("Iniciando rotina agendada de sincronização de catálogo...")
        
        # Cada execução do job abre e fecha sua própria sessão isolada com o banco
        async with async_session_factory() as session:
            try:
                set_repo = SQLAlchemySetRepository(session)
                card_repo = SQLAlchemyCardRepository(session)
                client = PokemonTcgClient()

                use_case = SyncCatalogUseCase(
                    set_repo=set_repo,
                    card_repo=card_repo,
                    client=client
                )

                # Eu sincronizo todas as coleções cadastradas na pokemontcg.io
                synced_sets = await use_case.sync_all_sets()
                await session.commit()
                logger.info(f"Sincronização de coleções finalizada. Total: {len(synced_sets)} coleções atualizadas.")
            except Exception as exc:
                await session.rollback()
                logger.error(f"Erro durante a sincronização de catálogo: {exc}", exc_info=True)

    def start(self) -> None:
        # Como o catálogo muda pouquíssimas vezes por ano (decisão da nossa arquitetura),
        # eu configuro para rodar uma vez por semana aos domingos às 03:00 da manhã.
        self._scheduler.add_job(
            self.execute_catalog_sync,
            trigger="cron",
            day_of_week="sun",
            hour=3,
            minute=0,
            id="sync_catalog_job",
            replace_existing=True
        )
        self._scheduler.start()
        logger.info("APScheduler iniciado com o job de catálogo agendado.")

    def shutdown(self) -> None:
        # Eu desligo o agendador liberando as threads e recursos
        self._scheduler.shutdown(wait=False)
        logger.info("APScheduler desligado com sucesso.")