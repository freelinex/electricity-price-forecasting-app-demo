import pandas as pd
import logging

from app.config.settings import settings
from app.loader.entsoe_loader import EntsoeLoader
from app.utils.logger_config import setup_logging
from app.utils.time_utils import normalize_timezone, resample_to_15min
from app.utils.cache import get_cached_or_fetch

setup_logging()
logger = logging.getLogger(__name__)


class HistoricalDatasetBuilder:
    def __init__(self, loader=None):
        self.loader = loader or EntsoeLoader()

    @staticmethod
    def merge_energy_data(
        prices_df: pd.DataFrame, load_df: pd.DataFrame, renewable_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Merges prices, load, wind, and solar DataFrames into a single dataset.
        Uses an outer join to ensure no timestamps are lost even if data is missing.
        """
        if prices_df.empty and load_df.empty and renewable_df.empty:
            return pd.DataFrame()

        merged = pd.concat(
            [prices_df, load_df, renewable_df], axis=1, join="outer", sort=False
        )
        return merged.sort_index()

    def build_raw_data(
        self, start_date: str, end_date: str, refresh_cache: bool = False
    ) -> pd.DataFrame:
        """
        Generates the final historical dataset for the requested date range.
        Fetches data in monthly chunks to respect API rate limits and utilizes caching.
        """
        start_month = pd.Timestamp(start_date).replace(day=1)

        months = pd.date_range(start=start_month, end=end_date, freq="MS")

        all_months_data = []

        for dt in months:
            prices = get_cached_or_fetch(
                fetch_func=self.loader.get_prices,
                year=dt.year,
                month=dt.month,
                data_type="prices",
                refresh=refresh_cache,
            )

            load = get_cached_or_fetch(
                fetch_func=self.loader.get_load,
                year=dt.year,
                month=dt.month,
                data_type="load",
                refresh=refresh_cache,
            )

            renewable = get_cached_or_fetch(
                fetch_func=self.loader.get_wind_solar,
                year=dt.year,
                month=dt.month,
                data_type="renewable",
                refresh=refresh_cache,
            )

            prices = normalize_timezone(prices)
            load = normalize_timezone(load)
            renewable = normalize_timezone(renewable)

            prices = resample_to_15min(prices)
            load = resample_to_15min(load)
            renewable = resample_to_15min(renewable)

            monthly_merged = self.merge_energy_data(prices, load, renewable)

            if not monthly_merged.empty:
                all_months_data.append(monthly_merged)
                logger.info(
                    "Processed %s: %d rows",
                    dt.strftime("%Y-%m"),
                    len(monthly_merged),
                )

        if not all_months_data:
            return pd.DataFrame()

        final_dataset = pd.concat(all_months_data, axis=0, sort=False)

        start_ts = pd.to_datetime(start_date, utc=True)
        end_ts = pd.to_datetime(end_date, utc=True)
        final_dataset = final_dataset.loc[start_ts:end_ts]

        return final_dataset

    def update_raw_data(self) -> tuple[pd.DataFrame, pd.Timestamp]:
        raw_path = settings.raw_file

        if not raw_path.exists():
            raw = self.run()
            if raw.empty:
                raise ValueError("ENTSO-E returned no historical data.")
            raw = raw.rename_axis("timestamp").reset_index()
            return raw, raw["timestamp"].min()

        raw = pd.read_csv(raw_path)

        raw["timestamp"] = pd.to_datetime(
            raw["timestamp"],
            utc=True,
            errors="coerce",
        )

        raw = raw.dropna(subset=["timestamp"])
        raw = raw.sort_values("timestamp")

        if raw.empty:
            raise ValueError("Raw dataset contains no valid timestamps.")

        value_columns = ["load", "wind", "solar"]

        missing_mask = raw[value_columns].isna().any(axis=1)

        if missing_mask.any():
            update_start = raw.loc[missing_mask, "timestamp"].min()
        else:
            update_start = raw["timestamp"].max()

        now = pd.Timestamp.now(tz="UTC")

        new_data = self.build_raw_data(
            start_date=update_start.isoformat(),
            end_date=now.isoformat(),
            refresh_cache=True,
        )

        if not new_data.empty:
            new_data.index = pd.to_datetime(
                new_data.index,
                utc=True,
            )

            new_data = new_data.reset_index()
            new_data = new_data.rename(columns={"index": "timestamp"})

            raw = pd.concat(
                [raw, new_data],
                ignore_index=True,
            )

            raw = (
                raw.drop_duplicates(
                    subset="timestamp",
                    keep="last",
                )
                .sort_values("timestamp")
                .reset_index(drop=True)
            )

            temp_path = raw_path.with_suffix(".tmp.csv")

            raw.to_csv(
                temp_path,
                index=False,
            )

            temp_path.replace(raw_path)

        return raw, update_start

    def run(self):
        today = pd.Timestamp.now(tz="UTC")

        dataset = self.build_raw_data(
            start_date=str(today - pd.DateOffset(years=2)),
            end_date=str(today),
        )

        if dataset.empty:
            raise ValueError("ENTSO-E returned no historical data.")

        output = settings.raw_file
        output.parent.mkdir(parents=True, exist_ok=True)

        temp_output = output.with_suffix(".tmp.csv")
        dataset.to_csv(
            temp_output,
            index=True,
            index_label="timestamp",
        )
        temp_output.replace(output)
        return dataset


if __name__ == "__main__":
    HistoricalDatasetBuilder().update_raw_data()
