import typer
from fastclime.core.logging import get_logger

log = get_logger(__name__)
app = typer.Typer(help="ETL pipelines for ingesting and cleaning geospatial data.")


@app.command()
def run(
    dataset: str = typer.Argument(
        ..., help="Name of the dataset to ingest (e.g., 'smap', 'ndvi')."
    ),
):
    """Run an ETL pipeline for a specific dataset (placeholder)."""
    log.info(f"Running ETL for dataset: {dataset}...")
    print(f"Running ETL for dataset: {dataset}... (placeholder)")
