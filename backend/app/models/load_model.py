import pandas as pd
from lightgbm import LGBMRegressor

from app.models.base_model import BaseModel
from app.models.features import MODEL_FEATURES
from app.utils.time_utils import is_nonworking_day, next_timestamp


class LoadModel(BaseModel):

    TARGET = "load"
    FEATURES = MODEL_FEATURES[TARGET]

    def __init__(self) -> None:
        super().__init__(
            LGBMRegressor(
                n_jobs=1,
                random_state=42,
                n_estimators=300,
                learning_rate=0.05,
                max_depth=-1,
            )
        )

    def make_features(self, df: pd.DataFrame) -> pd.DataFrame:
        if len(df) < 672:
            raise ValueError(f"Insufficient history. Required: 672, got: {len(df)}")

        next_ts = next_timestamp(df)

        return pd.DataFrame(
            {
                "hour": [next_ts.hour],
                "minute": [next_ts.minute],
                "dayofweek": [next_ts.dayofweek],
                "month": [next_ts.month],
                "is_nonworking_day": [is_nonworking_day(next_ts)],
                "load_lag_1": [df["load"].iloc[-1]],
                "load_lag_4": [df["load"].iloc[-4]],
                "load_lag_96": [df["load"].iloc[-96]],
                "load_lag_672": [df["load"].iloc[-672]],
            }
        )[self.FEATURES]

    def predict_next(self, df: pd.DataFrame) -> float:
        features_df = self.make_features(df)
        predictions = self.estimator.predict(features_df)
        return float(predictions[-1])
