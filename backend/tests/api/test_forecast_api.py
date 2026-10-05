import pytest
import pandas as pd
from fastapi.testclient import TestClient
from unittest.mock import patch

from main import app

client = TestClient(app)


@pytest.fixture
def mock_forecast_df():
    """Returns a simple mock DataFrame for the /forecast endpoint."""

    now = pd.Timestamp.now(tz="UTC").floor("h") + pd.Timedelta(hours=1)

    return pd.DataFrame(
        {
            "timestamp": [
                now,
                now + pd.Timedelta(hours=1),
            ],
            "price": [100.0, 110.0],
            "wind": [50.0, 60.0],
            "solar": [10.0, 0.0],
            "load": [1000.0, 1100.0],
        }
    )


@patch("app.api.routers.forecasts.forecast_window")
def test_run_forecast_success(mock_run, mock_forecast_df):
    """Test successful forecast generation."""

    mock_run.return_value = (mock_forecast_df, "2026-10-05T00:00:00+00:00")

    response = client.get("/forecast?period=24h")

    assert response.status_code == 200

    data = response.json()

    assert data["period"] == "24h"
    assert data["timezone"] == "Europe/Warsaw"

    assert len(data["forecast"]) == 2

    assert data["forecast"][0]["price"] == 100.0
    assert data["forecast"][1]["price"] == 110.0


@patch("app.api.routers.forecasts.forecast_window")
def test_run_forecast_empty_data(mock_run):
    """Test behavior when forecast pipeline returns empty data."""

    mock_run.return_value = (pd.DataFrame(), "2026-10-05T00:00:00+00:00")

    response = client.get("/forecast")

    assert response.status_code == 404
    assert response.json()["detail"] == "No forecast data generated"


@patch("app.api.routers.forecasts.forecast_window")
def test_run_forecast_internal_error(mock_run):
    """Test behavior when forecast pipeline raises an exception."""

    mock_run.side_effect = Exception("Database connection failed")

    response = client.get("/forecast")

    assert response.status_code == 500

    assert response.json()["detail"] == "Forecast is temporarily unavailable."
