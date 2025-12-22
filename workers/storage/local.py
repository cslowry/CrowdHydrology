"""
Local Filesystem CSV Storage Backend

Stores CSV files on the local filesystem, maintaining the existing behavior
of the application.
"""

import os

import pandas as pd
from loguru import logger

from workers.storage.base import CSVStorageBackend


class LocalCSVStorage(CSVStorageBackend):
    """Storage backend that saves CSV files to the local filesystem."""

    def __init__(self, base_path: str):
        """
        Initialize the local storage backend.

        Args:
            base_path: Base directory where CSV files will be stored.
        """
        self.base_path = base_path

    def save_csv(self, station_id: str, dataframe: pd.DataFrame) -> str:
        """
        Save a DataFrame as a CSV file to the local filesystem.

        Args:
            station_id: The station identifier (used in filename).
            dataframe: The pandas DataFrame to save.

        Returns:
            str: The absolute path where the CSV was saved.
        """
        # Ensure the directory exists
        try:
            os.makedirs(self.base_path, exist_ok=True)
            logger.info(f"Output directory ensured at: {self.base_path}")
        except Exception as e:
            logger.error(f"Failed to create directory {self.base_path}: {e}")
            raise

        # Generate filename and save
        csv_path = os.path.join(self.base_path, f"{station_id}_data.csv")
        dataframe.to_csv(csv_path, index=False)
        logger.info(f"Station {station_id} CSV saved locally at {csv_path}")

        return csv_path
