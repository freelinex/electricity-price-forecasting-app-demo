import pickle
from abc import abstractmethod, ABC
from pathlib import Path
from typing import Any, List

import pandas as pd


class BaseModel(ABC):
    """
    Common base class for all forecasting models.
    Provides shared machine-learning functionality.
    """

    TARGET: str = ""
    FEATURES: List[str] = []

    def __init__(self, estimator: Any = None, **kwargs):
        """
        Initializes the base model.

        :param estimator: The underlying machine learning algorithm.
        :param kwargs: Model-specific configuration parameters.
        """
        self.estimator = estimator
        self.config = kwargs

    def fit(self, df: pd.DataFrame) -> None:
        """
        Trains the underlying estimator using the provided dataset.

        :param df: A pandas DataFrame containing historical training data.
        """
        if df.empty:
            raise ValueError("Training data is empty. Cannot fit the model.")

        missing_features = [feat for feat in self.FEATURES if feat not in df.columns]

        if missing_features:
            raise ValueError(
                f"Missing required features in training data: {missing_features}"
            )

        if self.TARGET not in df.columns:
            raise ValueError(
                f"Target column '{self.TARGET}' is missing from training data."
            )

        X = df[self.FEATURES]
        y = df[self.TARGET]

        if self.estimator is None:
            raise ValueError("Estimator is not initialized.")

        self.estimator.fit(X, y)

    def predict(self, df: pd.DataFrame) -> Any:
        """
        Generates predictions using the trained estimator.

        :param df: A pandas DataFrame containing the prepared features.
        :return: An array of predictions.
        """
        if self.estimator is None:
            raise ValueError("Estimator is not initialized.")

        missing_features = [feat for feat in self.FEATURES if feat not in df.columns]
        if missing_features:
            raise ValueError(
                f"Missing required features for prediction: {missing_features}"
            )

        X = df[self.FEATURES]

        return self.estimator.predict(X)

    def save(self, path: str | Path) -> None:
        """
        Saves the entire trained model instance to disk.
        Automatically creates parent directories if they do not exist.
        """
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        temp_path = output_path.with_suffix(".tmp.pkl")
        with open(temp_path, "wb") as file:
            pickle.dump(self, file)
        temp_path.replace(output_path)

    @classmethod
    def load(cls, path: str | Path) -> "BaseModel":
        """
        Loads a saved model instance from disk.
        """
        input_path = Path(path)
        if not input_path.exists():
            raise FileNotFoundError(f"Model artifact not found at {input_path}")
        with open(input_path, "rb") as file:
            return pickle.load(file)

    @abstractmethod
    def make_features(self, df: pd.DataFrame) -> pd.DataFrame:

        raise NotImplementedError("Subclasses must implement make_features()")

    @abstractmethod
    def predict_next(self, df: pd.DataFrame) -> float:
        raise NotImplementedError
