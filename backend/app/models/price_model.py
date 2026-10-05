import pandas as pd
from lightgbm import LGBMRegressor

from app.models.base_model import BaseModel
from app.models.features import MODEL_FEATURES
from app.models.generation_model import GenerationModel
from app.utils.solar import sun_elevation
from app.utils.time_utils import is_nonworking_day, next_timestamp


class PriceModel(BaseModel):

    TARGET = "price"
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

    def make_features(
        self, df: pd.DataFrame, generation: GenerationModel
    ) -> pd.DataFrame:

        next_ts = next_timestamp(df)

        return pd.DataFrame(
            {
                "load": [generation.load],
                "wind": [generation.wind],
                "solar": [generation.solar],
                "hour": [next_ts.hour],
                "minute": [next_ts.minute],
                "dayofweek": [next_ts.dayofweek],
                "month": [next_ts.month],
                "is_nonworking_day": [is_nonworking_day(next_ts)],
                "sun_elevation": [sun_elevation(next_ts)],
                "price_lag_1": [df["price"].iloc[-1]],
                "price_lag_2": [df["price"].iloc[-2]],
                "price_lag_4": [df["price"].iloc[-4]],
                "price_lag_8": [df["price"].iloc[-8]],
                "price_lag_24": [df["price"].iloc[-24]],
                "price_lag_48": [df["price"].iloc[-48]],
                "price_lag_96": [df["price"].iloc[-96]],
                "price_lag_192": [df["price"].iloc[-192]],
                "price_lag_672": [df["price"].iloc[-672]],
            }
        )[self.FEATURES]

    def predict_next(self, df: pd.DataFrame, generation: GenerationModel) -> float:
        features_df = self.make_features(df, generation)
        predictions = self.estimator.predict(features_df)
        return float(predictions[-1])
