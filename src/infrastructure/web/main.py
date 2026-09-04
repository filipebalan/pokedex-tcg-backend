from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from src.infrastructure.web.routers.card_router import router as card_router
from src.infrastructure.scheduler.catalog_scheduler import CatalogScheduler

# Eu gerencio o ciclo de vida (startup e shutdown) da aplicação FastAPI via lifespan
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Acontece na inicialização do servidor:
    scheduler = CatalogScheduler()
    scheduler.start()
    app.state.scheduler = scheduler
    
    yield  # A aplicação roda aqui enquanto estiver ativa

    # Acontece quando o servidor é finalizado:
    scheduler.shutdown()

app = FastAPI(
    title="Pokédex TCG API",
    description="Backend profissional de catálogo e série temporal de preços do Pokémon TCG físico.",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(card_router)

@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    return {"status": "healthy"}