import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.infrastructure.database.session import async_session_factory
from src.infrastructure.database.repositories.sqlalchemy_set_repository import SQLAlchemySetRepository
from src.infrastructure.database.repositories.sqlalchemy_card_repository import SQLAlchemyCardRepository
from src.infrastructure.database.repositories.sqlalchemy_price_snapshot_repository import SQLAlchemyPriceSnapshotRepository
from src.infrastructure.external_apis.pokemon_tcg_client import PokemonTcgClient
from src.application.use_cases.sync_catalog_use_case import SyncCatalogUseCase
from src.application.use_cases.capture_price_snapshots_use_case import CapturePriceSnapshotsUseCase

logger = logging.getLogger(__name__)

class CatalogScheduler:
    def __init__(self) -> None:
        # Eu utilizo o AsyncIOScheduler para operar de forma não bloqueante com o FastAPI
        self._scheduler = AsyncIOScheduler()

    async def execute_catalog_sync(self) -> None:
        logger.info("Iniciando rotina agendada de sincronização de catálogo...")
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

                synced_sets = await use_case.sync_all_sets()
                await session.commit()
                logger.info(f"Sincronização de catálogo finalizada. Total: {len(synced_sets)} coleções.")
            except Exception as exc:
                await session.rollback()
                logger.error(f"Erro na sincronização de catálogo: {exc}", exc_info=True)

    async def execute_price_sync(self) -> None:
        logger.info("Iniciando rotina diária de captura de snapshots de preços...")
        async with async_session_factory() as session:
            try:
                card_repo = SQLAlchemyCardRepository(session)
                price_repo = SQLAlchemyPriceSnapshotRepository(session)
                client = PokemonTcgClient()

                use_case = CapturePriceSnapshotsUseCase(
                    price_repo=price_repo,
                    client=client
                )

                # Eu listo as cartas cadastradas no banco local para atualizar suas cotações
                cards = await card_repo.list_cards(limit=100)
                captured_count = 0

                for card in cards:
                    snapshot = await use_case.capture_for_card(card)
                    if snapshot:
                        captured_count += 1

                await session.commit()
                logger.info(f"Captura diária de preços concluída. Total de snapshots gravados: {captured_count}.")
            except Exception as exc:
                await session.rollback()
                logger.error(f"Erro na captura diária de preços: {exc}", exc_info=True)

    def start(self) -> None:
        # 1. Job de Catálogo: Semanal (aos domingos às 03:00)
        self._scheduler.add_job(
            self.execute_catalog_sync,
            trigger="cron",
            day_of_week="sun",
            hour=3,
            minute=0,
            id="sync_catalog_job",
            replace_existing=True
        )

        # 2. Job de Preços: Diário (todos os dias às 04:00 da manhã)
        self._scheduler.add_job(
            self.execute_price_sync,
            trigger="cron",
            hour=4,
            minute=0,
            id="sync_daily_prices_job",
            replace_existing=True
        )

        self._scheduler.start()
        logger.info("APScheduler iniciado com os jobs de catálogo e preços ativos.")

    def shutdown(self) -> None:
        self._scheduler.shutdown(wait=False)
        logger.info("APScheduler desligado com sucesso.")