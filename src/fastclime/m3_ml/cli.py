import json
import typer
from .train import train_one, train_all
from .serve import predict_batch
from pathlib import Path
from typing import Optional

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
    all: bool = typer.Option(False, help="Train all models"),
):
    """Train a specified ML model."""
    kwargs = {}
    if n_estimators:
        kwargs["n_estimators"] = n_estimators
    if learning_rate:
        kwargs["learning_rate"] = learning_rate

    if all:
        metrics = train_all(**kwargs)
    else:
        metrics = {model: train_one(model, **kwargs)}
    typer.echo(json.dumps(metrics, indent=2))


@app.command()
def batch(model: str, csv_in: Path, csv_out: Path):
    predict_batch(model, csv_in, csv_out)
    typer.echo(f"Saved predictions -> {csv_out}")
