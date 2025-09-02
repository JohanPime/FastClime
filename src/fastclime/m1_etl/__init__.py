"""Public API for M1 – ETL-Ingest."""

from .datasets import DATASETS
from .orchestrator import ingest


def list_datasets() -> dict[str, str]:
    """Returns a dictionary of available dataset names and their descriptions."""
    return {name: spec["desc"] for name, spec in DATASETS.items()}


__all__ = [
    "DATASETS",
    "ingest",
    "list_datasets",
]
