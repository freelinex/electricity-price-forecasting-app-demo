import logging
from pathlib import Path

import pandas as pd

from app.config.settings import settings
from app.training.registry import MODEL_REGISTRY
from app.models.features import MODEL_FEATURES
from app.utils.logger_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


class ModelTrainer:

    def load_processed_dataset(self, path: Path) -> pd.DataFrame:
        """Load the processed feature dataset."""
        return pd.read_csv(
            path,
            parse_dates=["timestamp"],
        )

    def train(self, name: str) -> None:
        processed_path = settings.processed_file
        processed_df = self.load_processed_dataset(processed_path)
        config = MODEL_REGISTRY[name]

        dataset = processed_df[[name] + MODEL_FEATURES[name]]

        split = int(len(dataset) * 0.8)
        train_data = dataset.iloc[:split]
        validation_data = dataset.iloc[split:]

        model = config.model_class()
        model.fit(train_data)

        model.save(config.model_path)


    @classmethod
    def train_all(cls) -> None:
        trainer = cls()
        for name in MODEL_REGISTRY:
            trainer.train(name)

        logger.info("All models trained.")


if __name__ == "__main__":
    ModelTrainer().train_all()
