import unittest
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd

from app.services.dataset_builder import HistoricalDatasetBuilder
from app.config.settings import settings


class TestHistoricalDatasetBuilder(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.temp_path = Path(self.temp_dir.name)

    def test_merge_energy_data(self):
        index = pd.to_datetime(
            [
                "2026-08-20 12:00",
                "2026-08-20 12:15",
            ],
            utc=True,
        )

        prices = pd.DataFrame(
            {"price": [80, 90]},
            index=index,
        )

        load = pd.DataFrame(
            {"load": [100, 110]},
            index=index,
        )

        renewable = pd.DataFrame(
            {
                "wind": [20, 25],
                "solar": [50, 60],
            },
            index=index,
        )

        result = HistoricalDatasetBuilder.merge_energy_data(
            prices,
            load,
            renewable,
        )

        expected = pd.DataFrame(
            {
                "price": [80, 90],
                "load": [100, 110],
                "wind": [20, 25],
                "solar": [50, 60],
            },
            index=index,
        )

        pd.testing.assert_frame_equal(result, expected)

    def test_merge_energy_data_keeps_missing_timestamps(self):
        index_prices = pd.to_datetime(
            ["2026-08-20 12:00"],
            utc=True,
        )

        index_load = pd.to_datetime(
            ["2026-08-20 12:15"],
            utc=True,
        )

        prices = pd.DataFrame(
            {"price": [80]},
            index=index_prices,
        )

        load = pd.DataFrame(
            {"load": [100]},
            index=index_load,
        )

        renewable = pd.DataFrame(
            columns=["wind", "solar"],
            index=pd.DatetimeIndex([], tz="UTC"),
        )

        result = HistoricalDatasetBuilder.merge_energy_data(
            prices,
            load,
            renewable,
        )

        self.assertEqual(len(result), 2)
        self.assertIn(index_prices[0], result.index)
        self.assertIn(index_load[0], result.index)

    def test_merge_energy_data_returns_empty_when_all_empty(self):
        result = HistoricalDatasetBuilder.merge_energy_data(
            pd.DataFrame(),
            pd.DataFrame(),
            pd.DataFrame(),
        )

        self.assertTrue(result.empty)

    @patch("app.services.dataset_builder.resample_to_15min")
    @patch("app.services.dataset_builder.normalize_timezone")
    @patch("app.services.dataset_builder.get_cached_or_fetch")
    def test_build_raw_data(
        self,
        mock_get_cached,
        mock_normalize,
        mock_resample,
    ):
        index = pd.to_datetime(
            [
                "2026-08-20 12:00",
                "2026-08-20 12:15",
            ],
            utc=True,
        )

        prices = pd.DataFrame(
            {"price": [80, 90]},
            index=index,
        )

        load = pd.DataFrame(
            {"load": [100, 110]},
            index=index,
        )

        renewable = pd.DataFrame(
            {
                "wind": [20, 25],
                "solar": [50, 60],
            },
            index=index,
        )

        mock_get_cached.side_effect = [
            prices,
            load,
            renewable,
        ]

        mock_normalize.side_effect = lambda df: df
        mock_resample.side_effect = lambda df: df

        builder = HistoricalDatasetBuilder()

        result = builder.build_raw_data(
            start_date="2026-08-20T12:00:00+00:00",
            end_date="2026-08-20T12:15:00+00:00",
        )

        self.assertFalse(result.empty)

        self.assertIn("price", result.columns)
        self.assertIn("load", result.columns)
        self.assertIn("wind", result.columns)
        self.assertIn("solar", result.columns)

        self.assertEqual(len(result), 2)

        self.assertEqual(
            mock_get_cached.call_count,
            3,
        )

    @patch("app.services.dataset_builder.HistoricalDatasetBuilder.run")
    def test_update_raw_data_when_file_does_not_exist(
        self,
        mock_run,
    ):
        index = pd.to_datetime(
            [
                "2026-08-20 12:00",
                "2026-08-20 12:15",
            ],
            utc=True,
        )

        raw = pd.DataFrame(
            {
                "timestamp": index,
                "load": [100, 110],
                "wind": [20, 25],
                "solar": [50, 60],
                "price": [80, 90],
            }
        )

        mock_run.return_value = raw.set_index("timestamp")

        missing_path = self.temp_path / "non_existing_raw.csv"

        with patch.object(
            settings,
            "raw_file",
            missing_path,
        ):
            result, update_start = HistoricalDatasetBuilder().update_raw_data()

        mock_run.assert_called_once()

        pd.testing.assert_frame_equal(
            result,
            raw,
        )

        self.assertEqual(
            update_start,
            raw["timestamp"].min(),
        )

    @patch("app.services.dataset_builder.HistoricalDatasetBuilder.build_raw_data")
    def test_update_raw_data_replaces_missing_values(
        self,
        mock_build_raw_data,
    ):
        with self.subTest("temporary missing value is replaced"):
            raw_path = self.temp_path / "test_raw_data.csv"

            raw = pd.DataFrame(
                {
                    "timestamp": pd.to_datetime(
                        [
                            "2026-08-20 12:00",
                            "2026-08-20 12:15",
                            "2026-08-20 12:30",
                        ],
                        utc=True,
                    ),
                    "load": [100, None, 120],
                    "wind": [20, 25, None],
                    "solar": [50, 60, 70],
                    "price": [80, 90, 100],
                }
            )

            raw.to_csv(
                raw_path,
                index=False,
            )

            new_data_index = pd.to_datetime(
                [
                    "2026-08-20 12:15",
                    "2026-08-20 12:30",
                ],
                utc=True,
            )

            new_data = pd.DataFrame(
                {
                    "load": [110, 120],
                    "wind": [25, 30],
                    "solar": [60, 70],
                    "price": [90, 100],
                },
                index=new_data_index,
            )

            mock_build_raw_data.return_value = new_data

            with patch.object(
                settings,
                "raw_file",
                raw_path,
            ):
                result, update_start = HistoricalDatasetBuilder().update_raw_data()

            self.assertEqual(
                update_start,
                pd.Timestamp(
                    "2026-08-20 12:15",
                    tz="UTC",
                ),
            )

            row = result[
                result["timestamp"]
                == pd.Timestamp(
                    "2026-08-20 12:15",
                    tz="UTC",
                )
            ].iloc[0]

            self.assertEqual(row["load"], 110)
            self.assertEqual(row["wind"], 25)
            self.assertEqual(row["solar"], 60)

            mock_build_raw_data.assert_called_once()

            self.assertTrue(raw_path.exists())

    @patch("app.services.dataset_builder.HistoricalDatasetBuilder.build_raw_data")
    def test_update_raw_data_keeps_existing_values(
        self,
        mock_build_raw_data,
    ):
        raw_path = self.temp_path / "test_raw_data_complete.csv"

        raw = pd.DataFrame(
            {
                "timestamp": pd.to_datetime(
                    [
                        "2026-08-20 12:00",
                        "2026-08-20 12:15",
                    ],
                    utc=True,
                ),
                "load": [100, 110],
                "wind": [20, 25],
                "solar": [50, 60],
                "price": [80, 90],
            }
        )

        raw.to_csv(
            raw_path,
            index=False,
        )

        mock_build_raw_data.return_value = pd.DataFrame()

        with patch.object(
            settings,
            "raw_file",
            raw_path,
        ):
            result, update_start = HistoricalDatasetBuilder().update_raw_data()

        self.assertFalse(result.empty)
        self.assertEqual(len(result), 2)

        self.assertEqual(
            update_start,
            pd.Timestamp(
                "2026-08-20 12:15",
                tz="UTC",
            ),
        )

    @patch("app.services.dataset_builder.HistoricalDatasetBuilder.build_raw_data")
    def test_run_saves_raw_data(
        self,
        mock_build_raw_data,
    ):
        index = pd.date_range(
            "2026-08-20 12:00",
            periods=2,
            freq="15min",
            tz="UTC",
        )

        dataset = pd.DataFrame(
            {
                "price": [80, 90],
                "load": [100, 110],
                "wind": [20, 25],
                "solar": [50, 60],
            },
            index=index,
        )

        mock_build_raw_data.return_value = dataset

        raw_path = self.temp_path / "test_run_raw.csv"

        with patch.object(
            settings,
            "raw_file",
            raw_path,
        ):
            result = HistoricalDatasetBuilder().run()

        mock_build_raw_data.assert_called_once()

        pd.testing.assert_frame_equal(
            result,
            dataset,
        )

        self.assertTrue(raw_path.exists())

        saved = pd.read_csv(
            raw_path,
            parse_dates=["timestamp"],
        )

        self.assertEqual(
            len(saved),
            2,
        )

        self.assertIn(
            "timestamp",
            saved.columns,
        )

        raw_path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
