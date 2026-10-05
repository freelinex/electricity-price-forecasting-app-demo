import logging
from zoneinfo import ZoneInfo

import pandas as pd
from fastapi import APIRouter, HTTPException

from app.services.forecast_store import forecast_window

router = APIRouter(tags=["Forecast"])
WARSAW_TZ = ZoneInfo("Europe/Warsaw")
logger = logging.getLogger(__name__)


@router.get("/forecast")
def get_forecast(period: str = "24h"):
    try:
        if period == "24h":
            days = 1
        elif period == "1w":
            days = 7
        elif period == "1m":
            days = 30
        else:
            raise HTTPException(
                status_code=400,
                detail="period must be 24h, 1w or 1m",
            )

        forecast_df, updated = forecast_window(days)

        if forecast_df.empty:
            raise HTTPException(
                status_code=404,
                detail="No forecast data generated",
            )

        if "price" not in forecast_df.columns:
            raise HTTPException(
                status_code=500,
                detail="Forecast data does not contain a 'price' column",
            )

        forecast_df["timestamp"] = pd.to_datetime(
            forecast_df["timestamp"],
            utc=True,
        )

        forecast_df["timestamp"] = forecast_df["timestamp"].dt.tz_convert(WARSAW_TZ)
        data = forecast_df

        return {
            "period": period,
            "timezone": "Europe/Warsaw",
            "updated_at": updated,
            "forecast": [
                {
                    "timestamp": row["timestamp"].isoformat(),
                    "price": round(float(row["price"]), 2),
                }
                for _, row in data.iterrows()
            ],
        }

    except HTTPException:
        raise

    except Exception:
        logger.exception("Forecast response failed")
        raise HTTPException(
            status_code=500,
            detail="Forecast is temporarily unavailable.",
        )
