import typer, subprocess, os
app = typer.Typer(help="Dashboard & API commands")

@app.command()
def run(host: str = "0.0.0.0", port: int = 8501):
    """Arranca Streamlit + FastAPI."""
    os.environ["FASTCLIME_ALLOW_EXEC"] = "1"
    subprocess.run(["streamlit", "run", "src/fastclime/m4_dashboard/app.py", "--server.port", str(port)])

@app.command()
def openapi():
    """Imprime la URL de la documentación interactiva."""
    typer.echo("http://localhost:8501/api/docs")
