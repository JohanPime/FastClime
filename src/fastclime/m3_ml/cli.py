import json
import typer
from .train import train_one, train_all
from .serve import predict_batch
from pathlib import Path
from typing import Optional
from fastclime.m0_storage.catalog import DataCatalog, get_catalog

app = typer.Typer(help="Train and run ML prediction models.")

@app.command()
def train(
    model: str = typer.Argument(..., help="'stress_clf' or 'lamina_reg'"),
    n_estimators: Optional[int] = typer.Option(
        None, help="Number of estimators for the model."
    ),
    learning_rate: Optional[float] = typer.Option(
        None, help="Learning rate for the model."
    ),
    overwrite: bool = typer.Option(False, help="Overwrite existing models."),
    all: bool = typer.Option(False, help="Train all models"),
    output_dir: Optional[Path] = typer.Option(
        None, help="Directory to save the model artifacts."
    ),
    db_path: Optional[Path] = typer.Option(None, help="Path to the DuckDB database."),
):
    """Train a specified ML model."""
    catalog = DataCatalog(db_path) if db_path else get_catalog()
    kwargs = {"catalog": catalog}
    if n_estimators:
        kwargs["n_estimators"] = n_estimators
    if learning_rate:
        kwargs["learning_rate"] = learning_rate
    if output_dir:
        kwargs["output_dir"] = output_dir

    if all:
        metrics = train_all(overwrite=True, **kwargs)
    else:
        metrics = {model: train_one(model, overwrite=overwrite, **kwargs)}
    typer.echo(json.dumps(metrics, indent=2))


@app.command()
def batch(model: str, csv_in: Path, csv_out: Path, db_path: Optional[Path] = typer.Option(None, help="Path to the DuckDB database.")):
    catalog = DataCatalog(db_path) if db_path else get_catalog()
    predict_batch(model, csv_in, csv_out, catalog=catalog)
    typer.echo(f"Saved predictions -> {csv_out}")
