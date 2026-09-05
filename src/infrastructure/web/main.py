from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from src.infrastructure.web.routers.card_router import router as card_router
from src.infrastructure.web.routers.collection_router import router as collection_router
from src.infrastructure.scheduler.catalog_scheduler import CatalogScheduler

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    scheduler = CatalogScheduler()
    scheduler.start()
    app.state.scheduler = scheduler
    
    yield

    scheduler.shutdown()

app = FastAPI(
    title="Pokédex TCG API",
    description="Backend profissional de catálogo e série temporal de preços do Pokémon TCG físico.",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(card_router)
app.include_router(collection_router)  # Eu registro a rota de coleções

@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    return {"status": "healthy"}