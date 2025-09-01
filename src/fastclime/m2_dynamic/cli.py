import typer
from fastclime.core.logging import get_logger

log = get_logger(__name__)
app = typer.Typer(help="Run dynamic soil-plant-atmosphere models.")


@app.command()
def run(
    model_name: str = typer.Argument(
        "eto", help="Name of the model to run (e.g., 'eto', 'etc')."
    ),
):
    """Run a specific dynamic model (placeholder)."""
    log.info(f"Running dynamic model: {model_name}...")
    print(f"Running dynamic model: {model_name}... (placeholder)")
