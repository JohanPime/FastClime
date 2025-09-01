import hashlib
from pathlib import Path
from fastclime.config import settings
from typing import Literal

Stage = Literal["raw", "processed", "models", "tmp"]


def get_stage_dir(stage: Stage) -> Path:
    """Gets the base directory for a given stage."""
    stage_map = {
        "raw": settings.DIR_RAW,
        "processed": settings.DIR_PROCESSED,
        "models": settings.DIR_MODELS,
        "tmp": settings.DIR_TMP,
    }
    return stage_map[stage]


def data_path(dataset_name: str, stage: Stage, filename: str) -> Path:
    """
    Constructs a path to a data file within the managed directory structure.

    Args:
        dataset_name: The name of the dataset (e.g., 'smap').
        stage: The processing stage ('raw', 'processed', 'models', 'tmp').
        filename: The name of the file.

    Returns:
        A Path object to the data file.
    """
    base_dir = get_stage_dir(stage) / dataset_name
    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir / filename


def calculate_sha256(filepath: Path) -> str:
    """Calculates the SHA256 hash of a file."""
    if not filepath.is_file():
        raise FileNotFoundError(f"File not found at {filepath}")

    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        # Read and update hash in chunks of 4K
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()
