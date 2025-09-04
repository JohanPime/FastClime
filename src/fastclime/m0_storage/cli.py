import typer
import shutil

from fastclime.config import settings
from fastclime.core.logging import get_logger
from .catalog import get_catalog

log = get_logger(__name__)
app = typer.Typer(help="Manage the FastClime data storage hub.")


@app.command()
def init():
    """Initializes the data storage directory and catalog."""
    log.info(f"Initializing data directory at: {settings.DATA_DIR}")

    # Create subdirectories
    dirs_to_create = [
        settings.DIR_RAW,
        settings.DIR_PROCESSED,
        settings.DIR_MODELS,
        settings.DIR_TMP,
    ]
    for d in dirs_to_create:
        d.mkdir(parents=True, exist_ok=True)
        log.info(f"Ensured directory exists: {d}")

    # Initialize catalog
    catalog = get_catalog()
    catalog.init_catalog()

    print(f"✅ FastClime data storage initialized at: {settings.DATA_DIR}")


@app.command()
def info():
    """Displays information about the data storage hub."""
    print("FastClime Data Storage Hub")
    print("==========================")
    print(f"Data Directory: {settings.DATA_DIR}")
    print(f"Catalog DB:     {settings.DATA_DIR / 'catalog.db'}")
    print("\nDirectory Structure:")

    for d in [
        settings.DIR_RAW,
        settings.DIR_PROCESSED,
        settings.DIR_MODELS,
        settings.DIR_TMP,
    ]:
        print(f"  - {d.relative_to(settings.DATA_DIR)}/")


@app.command()
def sync(
    remote: str = typer.Argument(
        ..., help="The remote URI to sync from (e.g., 's3://bucket/path')."
    ),
):
    """
    Syncs data from a remote source (placeholder).

    In a real implementation, this would use rclone, boto3, etc.
    """
    log.info(f"Starting sync from remote: {remote}")
    print(f"Syncing data from {remote}... (placeholder)")
    print("✅ Sync complete (placeholder).")


@app.command(name="clean-temp")
def clean_temp():
    """Removes all files and directories from the temporary data folder."""
    temp_dir = settings.DIR_TMP
    if not temp_dir.exists():
        log.warning(f"Temp directory not found at {temp_dir}, nothing to clean.")
        print("Temp directory does not exist. Nothing to clean.")
        return

    log.info(f"Cleaning temporary directory: {temp_dir}")
    for item in temp_dir.iterdir():
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()
    print(f"✅ Temporary directory cleaned: {temp_dir}")
