import pytest
from typer.testing import CliRunner

from fastclime.cli import app

runner = CliRunner()


def test_app_exists():
    """Test that the main Typer app object can be imported."""
    assert app is not None, "The main Typer application object should not be None."


def test_version_flag():
    """Test the --version flag exits cleanly and shows version info."""
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "FastClime CLI Version" in result.stdout


def test_help_flag():
    """Test the --help flag shows all placeholder commands."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0

    # Check for the main help text
    assert "Usage: fastclime [OPTIONS] COMMAND [ARGS]..." in result.stdout

    # Check that all module commands are listed
    expected_commands = ["storage", "ingest", "model", "predict", "visualize"]
    for cmd in expected_commands:
        assert cmd in result.stdout, f"Command '{cmd}' not found in --help output."


@pytest.mark.parametrize(
    "command, is_placeholder",
    [
        (["storage", "info"], False),
        (["ingest", "list"], False),
        (["model", "project"], False),
        (["predict", "train"], True),
        (["visualize", "start"], True),
    ],
)
def test_subcommands_run(command, is_placeholder):
    """Test that subcommands run without error."""
    result = runner.invoke(app, command)
    assert result.exit_code == 0
    if is_placeholder:
        assert "placeholder" in result.stdout.lower()
