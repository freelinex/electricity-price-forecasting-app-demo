from typing import ClassVar

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):

    entsoe_api_key: str = Field(min_length=1, validation_alias="ENTSOE_API_KEY")
    country: str = Field(default="PL", validation_alias="COUNTRY")

    PROJECT_NAME: str = "Electricity Price Forecasting"
    BASE_DIR: ClassVar[Path] = Path(__file__).resolve().parents[1]

    ENV_FILE: ClassVar[Path] = BASE_DIR / ".env"

    data_dir: Path = Field(default=BASE_DIR / "data", validation_alias="DATA_DIR")
    forecast_dir: Path
    raw_file: Path
    processed_file: Path
    cache_dir: Path
    model_dir: Path
    load_model_pkl: Path
    wind_model_pkl: Path
    solar_model_pkl: Path
    price_model_pkl: Path
    forecast_file: Path

    LATITUDE: float = Field(default=52.1, validation_alias="LATITUDE")
    LONGITUDE: float = Field(default=21.0, validation_alias="LONGITUDE")
    periods: ClassVar[int] = 96
    timezone: str = "Europe/Warsaw"
    cors_origins: list[str] = Field(default_factory=list, validation_alias="CORS_ORIGINS")
    forecast_refresh_enabled: bool = Field(default=True, validation_alias="FORECAST_REFRESH_ENABLED")
    forecast_refresh_seconds: int = Field(default=3600, ge=60, validation_alias="FORECAST_REFRESH_SECONDS")
    forecast_max_age_seconds: int = Field(default=86400, ge=60, validation_alias="FORECAST_MAX_AGE_SECONDS")
    entsoe_timeout: int = Field(default=30, ge=1, validation_alias="ENTSOE_TIMEOUT")

    @model_validator(mode="before")
    @classmethod
    def resolve_data_paths(cls, values):
        values = dict(values)
        root = Path(values.get("DATA_DIR", values.get("data_dir", cls.BASE_DIR / "data")))
        for name, relative in {
            "forecast_dir": "forecast", "raw_file": "raw/raw_dataset.csv",
            "processed_file": "processed/processed_dataset.csv", "cache_dir": "cache",
            "model_dir": "model", "load_model_pkl": "model/load.pkl",
            "wind_model_pkl": "model/wind.pkl", "solar_model_pkl": "model/solar.pkl",
            "price_model_pkl": "model/price.pkl", "forecast_file": "forecast/forecast_dataset.csv",
        }.items():
            values.setdefault(name, root / relative)
        return values

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
        populate_by_name=True,
    )


settings: Settings = Settings()  # type: ignore[call-arg]
