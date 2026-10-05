import os
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from main import app
from app.config.settings import Settings, settings
from app.services.dataset_builder import HistoricalDatasetBuilder
from app.services.forecast_store import forecast_window


@pytest.fixture
def isolated_data(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "forecast_file", tmp_path / "forecast.csv")
    monkeypatch.setattr(settings, "raw_file", tmp_path / "raw.csv")
    monkeypatch.setattr(settings, "forecast_refresh_enabled", False)
    return tmp_path


def publish(days=32):
    start = pd.Timestamp.now(tz=settings.timezone).normalize()
    frame = pd.DataFrame({
        "timestamp": pd.date_range(start, start + pd.DateOffset(days=days),
                                   freq="15min", inclusive="left"),
    })
    for name in ("price", "load", "wind", "solar"):
        frame[name] = 100.0
    frame.to_csv(settings.forecast_file, index=False)
    return frame


def test_data_dir_resolves_all_paths(tmp_path):
    configured = Settings(ENTSOE_API_KEY="test", DATA_DIR=tmp_path, _env_file=None)
    assert configured.raw_file == tmp_path / "raw/raw_dataset.csv"
    assert configured.processed_file == tmp_path / "processed/processed_dataset.csv"
    assert configured.cache_dir == tmp_path / "cache"
    assert configured.price_model_pkl == tmp_path / "model/price.pkl"
    assert configured.forecast_file == tmp_path / "forecast/forecast_dataset.csv"
    assert configured.forecast_refresh_enabled is True


def test_auto_refresh_can_be_explicitly_disabled(tmp_path):
    configured = Settings(ENTSOE_API_KEY="test", DATA_DIR=tmp_path,
                          FORECAST_REFRESH_ENABLED=False, _env_file=None)
    assert configured.forecast_refresh_enabled is False


def test_empty_deployment_serves_health_without_running_pipeline(isolated_data):
    with patch("app.services.forecast_pipeline.ForecastPipeline.run") as run:
        with TestClient(app) as client:
            assert client.get("/").status_code == 200
            assert client.get("/health").status_code == 200
            assert client.get("/ready").status_code == 503
            assert client.get("/forecast").status_code == 503
            assert client.get("/api/dashboard/highlights").status_code == 503
            assert client.get("/forecast?period=bad").status_code == 400
        run.assert_not_called()


def test_saved_forecast_and_dashboard_do_not_run_pipeline(isolated_data):
    publish()
    start = pd.Timestamp.now(tz=settings.timezone).normalize()
    raw = pd.DataFrame({"timestamp": pd.date_range(
        start - pd.DateOffset(days=1), start, freq="15min", inclusive="left"
    )})
    for name in ("price", "load", "wind", "solar"):
        raw[name] = 50.0
    raw.to_csv(settings.raw_file, index=False)
    with patch("app.services.forecast_pipeline.ForecastPipeline.run") as run:
        with TestClient(app) as client:
            assert client.get("/ready").status_code == 200
            response = client.get("/forecast?period=1m")
            assert response.status_code == 200
            assert response.json()["updated_at"]
            assert len(response.json()["forecast"]) == len(pd.date_range(
                start, start + pd.DateOffset(days=30), freq="15min", inclusive="left"
            ))
            assert client.get("/api/dashboard/highlights").status_code == 200
            assert client.get("/api/dashboard/drivers").status_code == 200
        run.assert_not_called()


def test_stale_or_incomplete_forecast_returns_503(isolated_data):
    publish(days=1)
    with TestClient(app) as client:
        assert client.get("/forecast?period=1w").status_code == 503
        frame = pd.read_csv(settings.forecast_file).iloc[1:]
        frame.to_csv(settings.forecast_file, index=False)
        assert client.get("/ready").status_code == 503
        publish()
        os.utime(settings.forecast_file, (1, 1))
        assert client.get("/forecast").status_code == 503


@pytest.mark.parametrize("date,points", [("2026-03-29", 92), ("2026-10-25", 100)])
def test_forecast_window_handles_dst(isolated_data, date, points):
    start = pd.Timestamp(date, tz=settings.timezone)
    frame = pd.DataFrame({"timestamp": pd.date_range(
        start, start + pd.DateOffset(days=1), freq="15min", inclusive="left"
    )})
    for name in ("price", "load", "wind", "solar"):
        frame[name] = 100.0
    frame.to_csv(settings.forecast_file, index=False)
    clock = SimpleNamespace(**vars(pd))
    clock.Timestamp = Mock(wraps=pd.Timestamp)
    clock.Timestamp.now.return_value = start
    with patch("app.services.forecast_store.pd", clock):
        result, _ = forecast_window(1)
    assert len(result) == points
    assert "timestamp" in result.columns


def test_cors_allows_configured_origin_only(isolated_data, monkeypatch):
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    configured = FastAPI()
    middleware = next(entry for entry in app.user_middleware if entry.cls is CORSMiddleware)
    configured.add_middleware(middleware.cls, **{
        **middleware.kwargs, "allow_origins": ["https://frontend.example"],
    })
    with TestClient(configured) as client:
        headers = {"Origin": "https://frontend.example", "Access-Control-Request-Method": "GET"}
        allowed = client.options("/forecast", headers=headers)
        assert allowed.status_code == 200
        assert allowed.headers["access-control-allow-origin"] == headers["Origin"]
        headers["Origin"] = "https://other.example"
        assert client.options("/forecast", headers=headers).status_code == 400


def test_bootstrap_uses_real_indexed_builder_output(isolated_data):
    raw = pd.DataFrame({
        "price": [10, 11], "load": [100, 110], "wind": [20, 21], "solar": [30, 31],
    }, index=pd.date_range("2026-10-01", periods=2, freq="15min", tz="UTC"))
    with patch.object(HistoricalDatasetBuilder, "build_raw_data", return_value=raw):
        frame, update_start = HistoricalDatasetBuilder().update_raw_data()
    assert "timestamp" in frame.columns
    assert update_start == raw.index.min()
    assert settings.raw_file.exists()


def test_empty_entsoe_does_not_publish_empty_raw_file(isolated_data):
    with patch.object(HistoricalDatasetBuilder, "build_raw_data", return_value=pd.DataFrame()):
        with pytest.raises(ValueError, match="no historical data"):
            HistoricalDatasetBuilder().update_raw_data()
    assert not settings.raw_file.exists()


def test_background_refresh_starts_and_stops(isolated_data, monkeypatch):
    from threading import Event
    started, stopped = Event(), Event()

    def loop(stop):
        started.set()
        stop.wait(3)
        if stop.is_set():
            stopped.set()

    monkeypatch.setattr(settings, "forecast_refresh_enabled", True)
    with patch("app.services.forecast_refresh.refresh_loop", side_effect=loop):
        with TestClient(app) as client:
            assert started.wait(2)
            assert client.get("/health").status_code == 200
        assert stopped.wait(2)


def test_bootstrap_trains_models_and_publishes_usable_forecast(isolated_data, monkeypatch):
    from dataclasses import replace
    import numpy as np
    from app.services.forecast_pipeline import ForecastPipeline
    from app.training.registry import MODEL_REGISTRY

    monkeypatch.setattr(settings, "processed_file", isolated_data / "processed.csv")
    model_paths = {}
    for name, config in MODEL_REGISTRY.items():
        path = isolated_data / f"{name}.pkl"
        monkeypatch.setattr(settings, f"{name}_model_pkl", path)

        def small_model(model_class=config.model_class):
            model = model_class()
            model.estimator.set_params(n_estimators=5, n_jobs=1, verbosity=-1)
            return model

        model_paths[name] = replace(config, model_path=path, model_class=small_model)

    monkeypatch.setattr("app.services.trainer_pipeline.MODEL_REGISTRY", model_paths)
    index = pd.date_range(end=pd.Timestamp.now(tz="UTC").floor("15min"),
                          periods=1500, freq="15min")
    wave = np.sin(np.arange(len(index)) / 96 * 2 * np.pi)
    raw = pd.DataFrame({"price": 100 + 10 * wave, "load": 1000 + 100 * wave,
                        "wind": 200 + 30 * wave, "solar": 100 + 50 * wave}, index=index)
    with patch.object(HistoricalDatasetBuilder, "build_raw_data", return_value=raw):
        ForecastPipeline().run(periods=192)
    assert ForecastPipeline.models_exist()
    with TestClient(app) as client:
        assert client.get("/ready").status_code == 200
        assert client.get("/forecast").status_code == 200


def test_dashboard_current_price_during_repeated_dst_hour(isolated_data):
    now = pd.Timestamp("2026-10-25T01:30:00Z").tz_convert(settings.timezone)
    index = pd.date_range("2026-10-25T00:00:00Z", periods=12, freq="15min").tz_convert(settings.timezone)
    today = pd.DataFrame({"price": range(12), "wind": 10., "solar": 20., "load": 100.}, index=index)
    yesterday = today.copy()
    with patch("app.api.routers.drivers.fetch_dashboard_data", return_value=(yesterday, today, now)):
        with TestClient(app) as client:
            result = client.get("/api/dashboard/highlights")
    assert result.status_code == 200
    assert result.json()["current_price"] == 4
