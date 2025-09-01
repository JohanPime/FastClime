import typer
from typing_extensions import Annotated

from . import __version__
from .m0_storage.cli import app as storage_app
from .m1_etl.cli import app as etl_app
from .m2_dynamic.cli import app as dynamic_app
from .m3_ml.cli import app as ml_app
from .m4_dashboard.cli import app as dashboard_app
from .core.logging import get_logger

log = get_logger(__name__)

app = typer.Typer(
    name="fastclime",
    help="A toolkit for climate simulation and irrigation management.",
    no_args_is_help=True,
)

# Add sub-commands from each module
app.add_typer(storage_app, name="storage", help="Manage data storage and artifacts.")
app.add_typer(
    etl_app,
    name="ingest",
    help="ETL pipelines for ingesting and cleaning geospatial data.",
)
app.add_typer(
    dynamic_app, name="model", help="Run dynamic soil-plant-atmosphere models."
)
app.add_typer(ml_app, name="predict", help="Train and run ML prediction models.")
app.add_typer(
    dashboard_app, name="visualize", help="Launch visualization dashboards and APIs."
)


def version_callback(value: bool):
    """Prints the version of the application and exits."""
    if value:
        print(f"FastClime CLI Version: {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            "-v",
            callback=version_callback,
            is_eager=True,
            help="Show the application's version and exit.",
        ),
    ] = False,
):
    """
    FastClime CLI. Use a subcommand to perform an action.
    """
    log.debug("FastClime CLI started.")
