import typer
from fastclime.core.logging import get_logger

log = get_logger(__name__)
app = typer.Typer(help="Train and run ML prediction models.")


@app.command()
def train(
    model_name: str = typer.Argument("lightgbm", help="Name of the model to train.")
):
    """Train a specified ML model (placeholder)."""
    log.info(f"Training ML model: {model_name}...")
    print(f"Training ML model: {model_name}... (placeholder)")


@app.command()
def predict():
    """Generate predictions from a trained model (placeholder)."""
    log.info("Generating predictions...")
    print("Generating predictions... (placeholder)")
