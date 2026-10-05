import logging
from threading import Lock
from pathlib import Path

import pandas as pd

from app.config.settings import settings
from app.forecasting.forecast_service import ForecastService
from app.models.load_model import LoadModel
from app.models.wind_model import WindModel
from app.models.solar_model import SolarModel
from app.models.price_model import PriceModel
from app.services.dataset_builder import HistoricalDatasetBuilder
from app.services.features_builder import FeatureBuilder
from app.services.trainer_pipeline import ModelTrainer
from app.utils.logger_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


class ForecastPipeline:
    _lock = Lock()

    def run(
            self, periods: int = settings.periods, retrain: bool = False
    ) -> pd.DataFrame:
        with self._lock:
            return self._run(periods, retrain)

    def _run(
        self, periods: int = settings.periods, retrain: bool = False
    ) -> pd.DataFrame:
        builder = HistoricalDatasetBuilder()
        raw_df, update_start = builder.update_raw_data()

        if raw_df.empty:
            raise ValueError("Raw dataset is empty.")

        processed = FeatureBuilder().build_processed_data(update_start)

        if processed.empty:
            raise ValueError("Processed dataset is empty.")

        if retrain or not self.models_exist():
            logger.info("Training models...")
            ModelTrainer.train_all()
        else:
            logger.info("Using existing trained models.")

        forecast_service = ForecastService(
            load_model=LoadModel.load(settings.load_model_pkl),
            wind_model=WindModel.load(settings.wind_model_pkl),
            solar_model=SolarModel.load(settings.solar_model_pkl),
            price_model=PriceModel.load(settings.price_model_pkl),
        )

        # Forecast
        logger.info(
            "Forecast started: periods=%d",
            periods,
        )
        result = forecast_service.recursive_forecast(
            periods=periods,
        )

        logger.info(
            "Forecast ended: %d rows generated",
            len(result),
        )

        # Save forecast
        output_path = settings.forecast_file
        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        # Write the new forecast to a temporary file first
        temp_output_path = output_path.with_suffix(".tmp.csv")

        result.to_csv(
            temp_output_path,
            index=False,
        )

        # Replace the old forecast with the new one
        temp_output_path.replace(output_path)
        logger.info(
            "Forecast saved: %s (%d rows)",
            output_path,
            len(result),
        )

        return result

    @staticmethod
    def models_exist() -> bool:
        return all(
            Path(path).exists()
            for path in (
                settings.load_model_pkl,
                settings.wind_model_pkl,
                settings.solar_model_pkl,
                settings.price_model_pkl,
            )
        )


if __name__ == "__main__":
    ForecastPipeline().run()
