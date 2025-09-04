"""
Public API for the M0 Storage-Hub module.

This module provides a centralized way to manage data directories,
file paths, and metadata for the FastClime project.
"""

from fastclime.config import settings
from .io import data_path, calculate_sha256, Stage
from .catalog import DataCatalog, get_catalog as get_catalog_singleton
from ..core.logging import get_logger

log = get_logger(__name__)

# --- Public API for the Storage Hub ---


def get_catalog() -> DataCatalog:
    """Returns a fresh instance of the DataCatalog."""
    return get_catalog_singleton()


# Expose the DATA_DIR directly from settings for convenience
DATA_DIR = settings.DATA_DIR


# Expose key functions from submodules
def register_dataset(*args, **kwargs):
    get_catalog().register_dataset(*args, **kwargs)


def register_artifact(*args, **kwargs):
    return get_catalog().register_artifact(*args, **kwargs)


def sync(remote_source: str):
    """
    Placeholder for the data synchronization logic.
    In a real implementation, this would trigger a robust sync process.
    """
    log.info(f"Syncing from remote source: {remote_source}...")
    print(f"Syncing from {remote_source}... (placeholder)")


__all__ = [
    # Constants
    "DATA_DIR",
    # Types
    "Stage",
    # Functions
    "get_catalog",
    "data_path",
    "calculate_sha256",
    "register_dataset",
    "register_artifact",
    "sync",
]
