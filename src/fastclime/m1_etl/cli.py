import typer
from typing_extensions import Annotated
import json

from fastclime.core.logging import get_logger
from .orchestrator import ingest
from .datasets import DATASETS

log = get_logger(__name__)
app = typer.Typer(
    help="ETL pipelines for ingesting and cleaning geospatial data.",
    add_completion=False,
)


@app.command()
def list():
    """Lists all available datasets that can be ingested."""
    log.info("Listing available datasets...")
    if not DATASETS:
        print("No datasets are available.")
        return

    print("Available datasets:")
    for name, spec in DATASETS.items():
        print(f"  - {name}: {spec['desc']}")


@app.command()
def run(
    dataset: Annotated[
        str,
        typer.Argument(help="Alias of the dataset to ingest (e.g., 'dem', 'smap')."),
    ],
    year: Annotated[
        int,
        typer.Option(
            help="Year to ingest data for.",
        ),
    ],
    bbox: Annotated[
        str,
        typer.Option(
            "--bbox",
            help='Bounding box in "min_lon min_lat max_lon max_lat" format.',
            callback=lambda value: [float(v) for v in value.split()],
        ),
    ] = None,
    overwrite: Annotated[
        bool,
        typer.Option(
            "--overwrite",
            help="Re-ingest and overwrite existing data.",
        ),
    ] = False,
    day_of_year: Annotated[int, typer.Option(help="Day of year (1-366).")] = None,
):
    """Run an ETL pipeline for a specific dataset."""
    log.info(f"Received request to run ETL for '{dataset}' for year {year}.")
    try:
        stats = ingest(
            dataset_name=dataset,
            year=year,
            bbox=bbox,
            overwrite=overwrite,
            day_of_year=day_of_year,
        )
        log.info(f"Ingestion successful for dataset '{dataset}'.")
        print("\n--- Ingestion Report ---")
        print(json.dumps(stats, indent=2))
        print("--- End of Report ---")

    except Exception as e:
        log.error(f"ETL pipeline for '{dataset}' failed: {e}", exc_info=True)
        raise typer.Exit(code=1)
