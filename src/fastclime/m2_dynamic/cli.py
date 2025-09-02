import typer
from typing_extensions import Annotated

from fastclime.core.logging import get_logger
from .orchestrator import run_hourly, project_deficit

log = get_logger(__name__)
app = typer.Typer(
    help="Run the dynamic water balance model.",
    add_completion=False,
)


@app.command()
def run(
    start: Annotated[
        str,
        typer.Option(
            help="Start timestamp in ISO format (e.g., '2025-01-01T00:00:00')."
        ),
    ],
    end: Annotated[
        str,
        typer.Option(help="End timestamp in ISO format (e.g., '2025-01-07T23:00:00')."),
    ],
    parcel_id: Annotated[
        str, typer.Option(help="ID of the parcel to simulate.")
    ] = "default",
):
    """Runs the hourly water balance simulation for a given period and parcel."""
    log.info(f"CLI command: model run from {start} to {end} for parcel {parcel_id}")
    run_hourly(start_ts=start, end_ts=end, parcel_id=parcel_id)
    log.info("Hourly simulation complete.")


@app.command()
def project(
    days: Annotated[
        int,
        typer.Option(help="Number of days to project the deficit forward."),
    ] = 7,
):
    """Projects the water deficit for a future period assuming no irrigation."""
    log.info(f"CLI command: model project for {days} days")
    project_deficit(days=days)
    log.info("Deficit projection complete.")
