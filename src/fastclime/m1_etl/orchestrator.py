"""The main ETL orchestration logic."""

import shutil
import tempfile
import hashlib
from pathlib import Path

from fastclime.m1_etl.datasets import DATASETS
from . import constants
from ..m0_storage.catalog import get_catalog
from ..core.logging import get_logger

log = get_logger(__name__)


def ingest(
    dataset_name: str,
    year: int,
    bbox: list[float] | None = None,
    overwrite: bool = False,
    keep_temp: bool = False,
    **kwargs,
) -> dict:
    """
    Orchestrates the download, processing, and registration of a dataset.
    """
    if dataset_name not in DATASETS:
        log.error(f"Dataset '{dataset_name}' is not in the registry.")
        raise ValueError(
            f"Dataset '{dataset_name}' not recognized. "
            f"Available datasets: {list(DATASETS.keys())}"
        )

    spec = DATASETS[dataset_name]
    log.info(f"Starting ingestion for dataset '{dataset_name}' for year {year}...")

    temp_dir = Path(tempfile.mkdtemp(prefix=f"fastclime_{dataset_name}_"))
    log.info(f"Using temporary directory: {temp_dir}")

    try:
        processed_dir = constants.PROCESSED_DIR / dataset_name
        download_ctx = {"year": year, "bbox": bbox, "temp_dir": temp_dir, **kwargs}
        process_ctx = {
            "processed_dir": processed_dir,
            "year": year,
            "bbox": bbox,
            "temp_dir": temp_dir,
            **kwargs,
        }

        downloaded_files = spec["download"](**download_ctx)
        processed_file = spec["process"](raw_files=downloaded_files, **process_ctx)

    finally:
        if not keep_temp:
            shutil.rmtree(temp_dir, ignore_errors=True)

    catalog = get_catalog()
    catalog.register_dataset(
        name=dataset_name,
        source="http",  # Placeholder
        version=str(year),
        description=spec["desc"],
    )

    file_hash = hashlib.sha256(processed_file.read_bytes()).hexdigest()
    artifact_id = catalog.register_artifact(
        dataset_name=dataset_name,
        stage="processed",
        relative_path=str(processed_file.relative_to(constants.DATA_DIR)),
        file_hash=file_hash,
        file_size_bytes=processed_file.stat().st_size,
    )

    stats = {
        "dataset": dataset_name,
        "year": year,
        "processed_file_path": str(processed_file),
        "processed_file_size": processed_file.stat().st_size,
        "processed_file_sha256": file_hash,
        "artifact_uuid": str(artifact_id),
    }
    return stats
