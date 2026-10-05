from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from app.services.forecast_pipeline import ForecastPipeline


class TestForecastPipeline:

    @patch("app.services.forecast_pipeline.ForecastService")
    @patch("app.services.forecast_pipeline.PriceModel")
    @patch("app.services.forecast_pipeline.SolarModel")
    @patch("app.services.forecast_pipeline.WindModel")
    @patch("app.services.forecast_pipeline.LoadModel")
    @patch("app.services.forecast_pipeline.ModelTrainer")
    @patch("app.services.forecast_pipeline.FeatureBuilder")
    @patch("app.services.forecast_pipeline.HistoricalDatasetBuilder")
    def test_run_without_retraining(
        self,
        mock_builder,
        mock_feature_builder,
        mock_trainer,
        mock_load_model,
        mock_wind_model,
        mock_solar_model,
        mock_price_model,
        mock_forecast_service,
        tmp_path,
    ):
        raw_df = pd.DataFrame(
            {
                "timestamp": pd.to_datetime(
                    ["2026-08-20 12:00"],
                    utc=True,
                ),
                "load": [100],
                "wind": [20],
                "solar": [50],
                "price": [80],
            }
        )

        processed_df = pd.DataFrame(
            {
                "load": [100],
                "wind": [20],
                "solar": [50],
                "price": [80],
            }
        )

        forecast_df = pd.DataFrame(
            {
                "timestamp": ["2026-08-21 12:00"],
                "price": [90],
            }
        )

        update_start = pd.Timestamp(
            "2026-08-20 12:00",
            tz="UTC",
        )

        mock_builder.return_value.update_raw_data.return_value = (
            raw_df,
            update_start,
        )

        mock_feature_builder.return_value.build_processed_data.return_value = (
            processed_df
        )

        mock_forecast_service.return_value.recursive_forecast.return_value = forecast_df

        output_path = tmp_path / "forecast" / "forecast.csv"

        with patch(
            "app.services.forecast_pipeline.settings.forecast_file",
            output_path,
        ), patch.object(
            ForecastPipeline,
            "models_exist",
            return_value=True,
        ):

            result = ForecastPipeline().run(periods=96)

        pd.testing.assert_frame_equal(
            result,
            forecast_df,
        )

        mock_builder.return_value.update_raw_data.assert_called_once()

        mock_feature_builder.return_value.build_processed_data.assert_called_once_with(
            update_start
        )

        mock_trainer.train_all.assert_not_called()

        mock_forecast_service.return_value.recursive_forecast.assert_called_once_with(
            periods=96
        )

        assert output_path.exists()

        saved = pd.read_csv(output_path)

        assert len(saved) == len(forecast_df)

    @patch("app.services.forecast_pipeline.ForecastService")
    @patch("app.services.forecast_pipeline.PriceModel")
    @patch("app.services.forecast_pipeline.SolarModel")
    @patch("app.services.forecast_pipeline.WindModel")
    @patch("app.services.forecast_pipeline.LoadModel")
    @patch("app.services.forecast_pipeline.ModelTrainer")
    @patch("app.services.forecast_pipeline.FeatureBuilder")
    @patch("app.services.forecast_pipeline.HistoricalDatasetBuilder")
    def test_run_with_retraining(
        self,
        mock_builder,
        mock_feature_builder,
        mock_trainer,
        mock_load_model,
        mock_wind_model,
        mock_solar_model,
        mock_price_model,
        mock_forecast_service,
        tmp_path,
    ):
        raw_df = pd.DataFrame({"load": [100]})
        processed_df = pd.DataFrame({"load": [100]})
        forecast_df = pd.DataFrame({"price": [90]})

        update_start = pd.Timestamp(
            "2026-08-20 12:00",
            tz="UTC",
        )

        mock_builder.return_value.update_raw_data.return_value = (
            raw_df,
            update_start,
        )

        mock_feature_builder.return_value.build_processed_data.return_value = (
            processed_df
        )

        mock_forecast_service.return_value.recursive_forecast.return_value = forecast_df

        output_path = tmp_path / "forecast" / "forecast.csv"

        with patch(
            "app.services.forecast_pipeline.settings.forecast_file",
            output_path,
        ):

            result = ForecastPipeline().run(
                periods=96,
                retrain=True,
            )

        mock_trainer.train_all.assert_called_once()

        mock_forecast_service.return_value.recursive_forecast.assert_called_once_with(
            periods=96
        )

        assert output_path.exists()
        assert len(result) == 1

    @patch("app.services.forecast_pipeline.HistoricalDatasetBuilder")
    def test_run_raises_when_raw_is_empty(
        self,
        mock_builder,
    ):
        mock_builder.return_value.update_raw_data.return_value = (
            pd.DataFrame(),
            pd.Timestamp("2026-08-20", tz="UTC"),
        )

        with pytest.raises(
            ValueError,
            match="Raw dataset is empty",
        ):
            ForecastPipeline().run()

    @patch("app.services.forecast_pipeline.FeatureBuilder")
    @patch("app.services.forecast_pipeline.HistoricalDatasetBuilder")
    def test_run_raises_when_processed_is_empty(
        self,
        mock_builder,
        mock_feature_builder,
    ):
        raw_df = pd.DataFrame({"load": [100]})

        update_start = pd.Timestamp(
            "2026-08-20 12:00",
            tz="UTC",
        )

        mock_builder.return_value.update_raw_data.return_value = (
            raw_df,
            update_start,
        )

        mock_feature_builder.return_value.build_processed_data.return_value = (
            pd.DataFrame()
        )

        with pytest.raises(
            ValueError,
            match="Processed dataset is empty",
        ):
            ForecastPipeline().run()

    def test_models_exist_when_model_missing(self):
        with patch(
            "app.services.forecast_pipeline.settings.load_model_pkl",
            Path("/tmp/load.pkl"),
        ), patch(
            "app.services.forecast_pipeline.settings.wind_model_pkl",
            Path("/tmp/wind.pkl"),
        ), patch(
            "app.services.forecast_pipeline.settings.solar_model_pkl",
            Path("/tmp/solar.pkl"),
        ), patch(
            "app.services.forecast_pipeline.settings.price_model_pkl",
            Path("/tmp/price.pkl"),
        ):

            result = ForecastPipeline.models_exist()

        assert result is False

    def test_models_exist_when_models_are_recent(
        self,
        tmp_path,
    ):
        model_paths = [
            tmp_path / "load.pkl",
            tmp_path / "wind.pkl",
            tmp_path / "solar.pkl",
            tmp_path / "price.pkl",
        ]

        for path in model_paths:
            path.touch()

        with patch(
            "app.services.forecast_pipeline.settings.load_model_pkl",
            model_paths[0],
        ), patch(
            "app.services.forecast_pipeline.settings.wind_model_pkl",
            model_paths[1],
        ), patch(
            "app.services.forecast_pipeline.settings.solar_model_pkl",
            model_paths[2],
        ), patch(
            "app.services.forecast_pipeline.settings.price_model_pkl",
            model_paths[3],
        ):

            result = ForecastPipeline.models_exist()

        assert result is True

