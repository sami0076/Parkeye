"""FastAPI app - init, router registration, CORS."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base
from app.routers import lots, predictions, recommendations, events, feedback, admin, websocket


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create tables on startup."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="Parkeye API",
    description="Parking availability API for GMU",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS.split(",") if settings.ALLOWED_ORIGINS else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(lots.router)
app.include_router(predictions.router)
app.include_router(recommendations.router)
app.include_router(events.router)
app.include_router(feedback.router)
app.include_router(admin.router)
app.include_router(websocket.router)


@app.get("/health")
async def health():
    """Health check for deployment."""
    return {"status": "ok"}
