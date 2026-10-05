import pandas as pd
from lightgbm import LGBMRegressor

from app.models.base_model import BaseModel
from app.models.features import MODEL_FEATURES
from app.utils.solar import sun_elevation
from app.utils.time_utils import next_timestamp


class SolarModel(BaseModel):

    TARGET = "solar"
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
                "sun_elevation": [sun_elevation(next_ts)],
                "solar_lag_96": [df["solar"].iloc[-96]],
                "solar_lag_672": [df["solar"].iloc[-672]],
            }
        )[self.FEATURES]

    def predict_next(self, df: pd.DataFrame) -> float:
        features_df = self.make_features(df)
        predictions = self.estimator.predict(features_df)
        return float(predictions[-1])
