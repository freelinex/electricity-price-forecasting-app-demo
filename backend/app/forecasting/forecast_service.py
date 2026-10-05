from dataclasses import dataclass
import logging

from app.utils.logger_config import setup_logging

logger = logging.getLogger(__name__)

import pandas as pd

from app.config.settings import settings
from app.models.load_model import LoadModel
from app.models.wind_model import WindModel
from app.models.solar_model import SolarModel
from app.models.price_model import PriceModel
from app.utils.time_utils import next_timestamp

setup_logging()
logger = logging.getLogger(__name__)


@dataclass
class GenerationForecast:
    load: float
    wind: float
    solar: float


class ForecastService:
    def __init__(
        self,
        load_model: LoadModel,
        wind_model: WindModel,
        solar_model: SolarModel,
        price_model: PriceModel,
    ) -> None:
        self.load_model = load_model
        self.wind_model = wind_model
        self.solar_model = solar_model
        self.price_model = price_model

    def load_processed_data(self) -> pd.DataFrame:
        """Load processed data once and keep it in memory."""
        processed_path = settings.processed_file

        df = pd.read_csv(processed_path)

        df["timestamp"] = pd.to_datetime(
            df["timestamp"],
            utc=True,
        )

        return df

    def predict_generation(self, df: pd.DataFrame) -> GenerationForecast:
        return GenerationForecast(
            load=self.load_model.predict_next(df),
            wind=self.wind_model.predict_next(df),
            solar=self.solar_model.predict_next(df),
        )

    def predict_price(
        self,
        df: pd.DataFrame,
        generation: GenerationForecast,
    ) -> float:
        return self.price_model.predict_next(df, generation)

    def recursive_forecast(self, periods: int) -> pd.DataFrame:
        logger.info("Starting recursive forecast: periods=%s", periods)

        if periods <= 0:
            logger.error("Invalid forecast periods: %s", periods)
            raise ValueError("periods must be > 0")

        processed_df = self.load_processed_data().copy()

        logger.info(
            "Loaded processed data: rows=%s",
            len(processed_df),
        )

        processed_df["timestamp"] = pd.to_datetime(
            processed_df["timestamp"],
            utc=True,
        )

        processed_df = processed_df.sort_values("timestamp")

        latest_timestamp = processed_df["timestamp"].iloc[-1]
        polish_timestamp = latest_timestamp.tz_convert("Europe/Warsaw")

        logger.info(
            "Latest actual timestamp: %s",
            latest_timestamp,
        )
        start_of_day_polish = polish_timestamp.normalize()
        start_of_day_utc = start_of_day_polish.tz_convert("UTC")

        actual = processed_df[
            (processed_df["timestamp"] >= start_of_day_utc)
            & (processed_df["timestamp"] <= latest_timestamp)
        ].copy()

        logger.info(
            "Actual points for current day: %s",
            len(actual),
        )

        forecast_periods = periods - len(actual)

        logger.info(
            "Requested points=%s, actual points=%s, " "forecast points needed=%s",
            periods,
            len(actual),
            max(forecast_periods, 0),
        )

        if forecast_periods <= 0:
            logger.info(
                "Enough actual data available. " "Returning last %s actual points.",
                periods,
            )

            return actual.tail(periods).reset_index(drop=True)

        logger.info(
            "Starting recursive prediction for %s points",
            forecast_periods,
        )

        forecast = self.recursive_forecast_cached(forecast_periods).copy()

        logger.info(
            "Forecast completed: generated %s points",
            len(forecast),
        )

        result = pd.concat(
            [actual, forecast],
            ignore_index=True,
        )
        result["timestamp"] = pd.to_datetime(
            result["timestamp"], utc=True
        ).dt.tz_convert("Europe/Warsaw")
        result = result[["timestamp", "price", "load", "wind", "solar"]]

        logger.info(
            "Final forecast result: %s points",
            len(result),
        )

        return result

    def recursive_forecast_cached(
        self,
        periods: int,
    ) -> pd.DataFrame:

        # Models only need the largest lag (one week), not two years of history.
        history = self.load_processed_data().tail(672).reset_index(drop=True).copy()

        predictions = []

        for _ in range(periods):
            timestamp = next_timestamp(history)

            generation = self.predict_generation(history)

            price = self.predict_price(
                history,
                generation,
            )

            row = {
                "timestamp": timestamp,
                "load": generation.load,
                "wind": generation.wind,
                "solar": generation.solar,
                "price": price,
            }

            predictions.append(row)

            # Avoid creating a DataFrame + pd.concat()
            history.loc[len(history)] = row

        return pd.DataFrame(predictions)
