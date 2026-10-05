import logging

import pandas as pd
from fastapi import APIRouter, HTTPException
from app.config.settings import settings
from app.services.forecast_store import forecast_window
from app.api.schemas.dashboard import (
    TodayHighlightsResponse,
    HighlightMetric,
    PriceDriversResponse,
    PriceDriver,
)

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])
logger = logging.getLogger(__name__)


def calculate_trend(
    current: float, previous: float, inverse: bool = False
) -> tuple[str, str]:
    """Calculates percentage change and returns the trend direction and formatted string."""
    if previous == 0 or pd.isna(previous):
        return "neutral", "0%"

    change = ((current - previous) / previous) * 100

    if change > 0:
        trend = "down" if inverse else "up"
        return trend, f"+{change:.1f}%"
    elif change < 0:
        trend = "up" if inverse else "down"
        return trend, f"{change:.1f}%"
    else:
        return "neutral", "Rate"


def fetch_dashboard_data():
    """Retrieves and aligns real historical actuals with today's forecast."""
    try:
        forecast_df, _ = forecast_window(1)

        if "timestamp" in forecast_df.columns:
            forecast_df["timestamp"] = pd.to_datetime(
                forecast_df["timestamp"], utc=True
            )
            forecast_df.set_index("timestamp", inplace=True)
        else:
            forecast_df.index = pd.to_datetime(forecast_df.index, utc=True)

        raw_df = pd.read_csv(settings.raw_file)
        raw_df["timestamp"] = pd.to_datetime(raw_df["timestamp"], utc=True)
        raw_df = raw_df.dropna(subset=["timestamp", "price", "load", "wind", "solar"])
        raw_df.set_index("timestamp", inplace=True)

        raw_df = raw_df.tz_convert(settings.timezone)
        forecast_df = forecast_df.tz_convert(settings.timezone)
        now = pd.Timestamp.now(tz=settings.timezone)

        yesterday_start = now.normalize() - pd.DateOffset(days=1)
        yesterday_end = now.normalize() - pd.Timedelta(seconds=1)
        today_start = now.normalize()
        today_end = now.normalize() + pd.DateOffset(days=1) - pd.Timedelta(seconds=1)

        yesterday_data = raw_df.loc[yesterday_start:yesterday_end]
        today_data = forecast_df.loc[today_start:today_end]

        if yesterday_data.empty or today_data.empty:
            raise ValueError("Insufficient data to calculate daily comparisons.")

        return yesterday_data, today_data, now

    except HTTPException:
        raise
    except Exception:
        logger.exception("Dashboard data unavailable")
        raise HTTPException(
            status_code=503, detail="Dashboard data is temporarily unavailable."
        )


@router.get("/highlights", response_model=TodayHighlightsResponse)
def get_today_highlights():
    yesterday_data, today_data, now = fetch_dashboard_data()

    yesterday_prices = yesterday_data["price"]
    today_prices = today_data["price"]

    yesterday_avg = yesterday_prices.mean()
    today_avg = today_prices.mean()
    yesterday_peak = yesterday_prices.max()
    today_peak = today_prices.max()
    yesterday_low = yesterday_prices.min()
    today_low = today_prices.min()

    # Floor in UTC to distinguish the repeated hour when DST ends.
    current_hour = now.tz_convert("UTC").floor("h").tz_convert(settings.timezone)
    try:
        current_price = float(today_prices.loc[current_hour])
    except KeyError:
        current_price = float(today_prices.iloc[0])

    avg_trend, avg_text = calculate_trend(today_avg, yesterday_avg)
    peak_trend, peak_text = calculate_trend(today_peak, yesterday_peak)
    low_trend, low_text = calculate_trend(today_low, yesterday_low)

    return TodayHighlightsResponse(
        current_price=round(current_price, 2),
        today_average=HighlightMetric(
            value=round(today_avg, 2), trend=avg_trend, change_text=avg_text
        ),
        today_peak=HighlightMetric(
            value=round(today_peak, 2), trend=peak_trend, change_text=peak_text
        ),
        today_low=HighlightMetric(
            value=round(today_low, 2), trend=low_trend, change_text=low_text
        ),
    )


@router.get("/drivers", response_model=PriceDriversResponse)
def get_price_drivers():
    yesterday_data, today_data, _ = fetch_dashboard_data()

    y_wind = yesterday_data["wind"].mean()
    t_wind = today_data["wind"].mean()
    y_solar = yesterday_data["solar"].mean()
    t_solar = today_data["solar"].mean()
    y_load = yesterday_data["load"].mean()
    t_load = today_data["load"].mean()

    wind_trend, wind_text = calculate_trend(t_wind, y_wind, inverse=True)
    solar_trend, solar_text = calculate_trend(t_solar, y_solar, inverse=True)
    load_trend, load_text = calculate_trend(t_load, y_load, inverse=False)

    return PriceDriversResponse(
        summary="Price drivers calculated based on daily averages",
        drivers=[
            PriceDriver(
                name="Wind Generation",
                description="Wind output impact",
                previous_value=round(y_wind, 1),
                current_value=round(t_wind, 1),
                unit="MW",
                change_text=wind_text,
                trend=wind_trend,
            ),
            PriceDriver(
                name="Solar Generation",
                description="Solar output impact",
                previous_value=round(y_solar, 1),
                current_value=round(t_solar, 1),
                unit="MW",
                change_text=solar_text,
                trend=solar_trend,
            ),
            PriceDriver(
                name="Electricity Demand",
                description="Grid load impact",
                previous_value=round(y_load, 1),
                current_value=round(t_load, 1),
                unit="MW",
                change_text=load_text,
                trend=load_trend,
            ),
        ],
    )
