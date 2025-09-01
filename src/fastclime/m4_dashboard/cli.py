import typer
from fastclime.core.logging import get_logger

log = get_logger(__name__)
app = typer.Typer(help="Launch visualization dashboards and APIs.")


@app.command()
def start(port: int = typer.Option(8501, help="Port to run the dashboard on.")):
    """Start the Streamlit/Gradio dashboard (placeholder)."""
    log.info(f"Starting dashboard on port {port}...")
    print(f"Starting dashboard on port {port}... (placeholder)")
    print("In a real scenario, this would run `streamlit run ...`")
