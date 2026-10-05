import pandas as pd
from lightgbm import LGBMRegressor

from app.models.base_model import BaseModel
from app.models.features import MODEL_FEATURES
from app.utils.time_utils import next_timestamp


class WindModel(BaseModel):

    TARGET = "wind"
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

        next_ts = next_timestamp(df)

        return pd.DataFrame(
            {
                "hour": [next_ts.hour],
                "minute": [next_ts.minute],
                "dayofweek": [next_ts.dayofweek],
                "month": [next_ts.month],
                "wind_lag_96": [df["wind"].iloc[-96]],
                "wind_lag_672": [df["wind"].iloc[-672]],
            }
        )[self.FEATURES]

    def predict_next(self, df: pd.DataFrame) -> float:
        features_df = self.make_features(df)
        predictions = self.estimator.predict(features_df)
        return float(predictions[-1])
