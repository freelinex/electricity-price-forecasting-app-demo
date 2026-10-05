"""Single-process refresh loop for the disk-backed deployment."""
import argparse
import logging
from threading import Event

from app.config.settings import settings
from app.services.forecast_pipeline import ForecastPipeline

logger = logging.getLogger(__name__)
# Extra days cover delayed actuals and DST; the API slices calendar-day windows.
FORECAST_PERIODS = 32 * 96


def refresh_loop(stop: Event) -> None:
    while not stop.is_set():
        try:
            logger.info("Forecast refresh started")
            ForecastPipeline().run(periods=FORECAST_PERIODS)
            logger.info("Forecast refresh completed; next attempt in %s seconds", settings.forecast_refresh_seconds)
        except Exception:
            logger.exception("Forecast refresh failed; retaining the previous forecast")
        stop.wait(settings.forecast_refresh_seconds)


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare or refresh data, models and forecasts")
    parser.add_argument("--retrain", action="store_true")
    args = parser.parse_args()
    ForecastPipeline().run(periods=FORECAST_PERIODS, retrain=args.retrain)


if __name__ == "__main__":
    main()
