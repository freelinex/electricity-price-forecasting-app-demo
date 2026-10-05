"""Read published forecasts without fetching data or training models."""
import logging
import os
import time

import numpy as np
import pandas as pd
from fastapi import HTTPException

from app.config.settings import settings

logger = logging.getLogger(__name__)


def read_forecast() -> tuple[pd.DataFrame, str]:
    try:
        with settings.forecast_file.open("rb") as source:
            updated = os.fstat(source.fileno()).st_mtime
            if time.time() - updated > settings.forecast_max_age_seconds:
                raise HTTPException(503, "Forecast is stale; refresh is pending.")
            frame = pd.read_csv(source)
        if frame.empty or not {"timestamp", "price", "load", "wind", "solar"}.issubset(frame.columns):
            raise ValueError("Incomplete forecast file")
        frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True)
        values = frame[["price", "load", "wind", "solar"]].apply(pd.to_numeric, errors="coerce")
        if frame["timestamp"].isna().any() or not np.isfinite(values.to_numpy()).all():
            raise ValueError("Invalid forecast values")
        return frame, pd.Timestamp(updated, unit="s", tz="UTC").isoformat()
    except HTTPException:
        raise
    except FileNotFoundError:
        raise HTTPException(503, "Forecast is being prepared. Please try again later.") from None
    except Exception:
        logger.exception("Cannot read published forecast")
        raise HTTPException(503, "Forecast is temporarily unavailable.") from None


def forecast_window(days: int) -> tuple[pd.DataFrame, str]:
    frame, updated = read_forecast()
    start = pd.Timestamp.now(tz=settings.timezone).normalize()
    end = start + pd.DateOffset(days=days)
    # Require full coverage, including days with a daylight-saving transition.
    expected = pd.date_range(start, end, freq="15min", inclusive="left").tz_convert("UTC")
    frame = frame.drop_duplicates("timestamp", keep="last").set_index("timestamp").sort_index()
    if not expected.isin(frame.index).all():
        raise HTTPException(503, "Forecast does not yet cover the requested period.")
    return frame.loc[expected].rename_axis("timestamp").reset_index(), updated
