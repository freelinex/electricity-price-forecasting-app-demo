from contextlib import asynccontextmanager
import logging
from threading import Event, Thread

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import forecasts, drivers
from app.config.settings import settings
from app.services.forecast_store import forecast_window
from app.utils.logger_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    stop = Event()
    if settings.forecast_refresh_enabled:
        from app.services.forecast_refresh import refresh_loop
        logger.info("Starting automatic forecast refresh; API serves saved forecasts while preparation runs.")
        Thread(target=refresh_loop, args=(stop,), daemon=True, name="forecast-refresh").start()
    else:
        logger.warning(
            "Automatic forecast refresh is disabled. Set FORECAST_REFRESH_ENABLED=true "
            "or run python -m app.services.forecast_refresh before using forecast endpoints."
        )
    try:
        yield
    finally:
        stop.set()

app = FastAPI(
    title="Voltio Energy Forecast API",
    description="API for energy data, dashboards, and forecasts",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins or [settings.frontend_url, "http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(forecasts.router)
app.include_router(drivers.router)


@app.get("/")
def home():
    return {"name": app.title, "version": app.version, "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ready")
def ready():
    _, updated = forecast_window(1)
    return {"status": "ready", "updated_at": updated}
