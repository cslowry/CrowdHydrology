"""
Storage Factory

Factory function to instantiate the appropriate CSV storage backend
based on application configuration.
"""

from django.conf import settings
from loguru import logger

from workers.storage.base import CSVStorageBackend
from workers.storage.local import LocalCSVStorage

# from workers.storage.r2 import R2CSVStorage


def get_csv_storage() -> CSVStorageBackend:
    """
    Factory function to get the configured CSV storage backend.

    Returns:
        CSVStorageBackend: An instance of the configured storage backend.

    Raises:
        ValueError: If the configured storage backend is not supported.
    """
    backend_type = settings.CSV_STORAGE_BACKEND.lower()

    if backend_type == "local":
        logger.info("Using local filesystem storage for CSVs")
        return LocalCSVStorage(base_path=settings.STATION_DATA_DIR)

    else:
        raise ValueError(
            f"Unsupported CSV storage backend: {backend_type}. "
            f"Supported backends: 'local', 'r2'"
        )
