"""
CSV Storage Backend Abstraction

This module provides an abstract base class for CSV storage backends,
following the Strategy Pattern to allow flexible switching between
different storage solutions (local filesystem, cloud storage, etc.).
"""

from abc import ABC, abstractmethod

import pandas as pd


class CSVStorageBackend(ABC):
    """Abstract base class for CSV storage backends."""

    @abstractmethod
    def save_csv(self, station_id: str, dataframe: pd.DataFrame) -> str:
        """
        Save a DataFrame as a CSV file for the given station.

        Args:
            station_id: The station identifier (used in filename).
            dataframe: The pandas DataFrame to save.

        Returns:
            str: The path/URL where the CSV was saved.
        """
        pass
