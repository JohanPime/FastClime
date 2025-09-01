import pytest
from typer.testing import CliRunner
import duckdb
import importlib

from fastclime.cli import app
from fastclime.m0_storage import (
    register_dataset,
    register_artifact,
    calculate_sha256,
    data_path,
)

# We need to reload the modules that use the settings object
# to make sure they get the patched DATA_DIR from the env var.
from fastclime import config
from fastclime.m0_storage import catalog, io, cli as storage_cli

runner = CliRunner()


@pytest.fixture
def temp_storage(tmp_path, monkeypatch):
    """
    A pytest fixture that creates a temporary data directory,
    sets the appropriate environment variable, and reloads the settings object
    to ensure the tests are isolated and use the temporary directory.
    """
    monkeypatch.setenv("FASTCLIME_DATA_DIR", str(tmp_path))

    # We must reload the settings module and any module that imports it
    # to ensure the patched environment variable is used.
    importlib.reload(config)
    importlib.reload(io)
    importlib.reload(catalog)
    importlib.reload(storage_cli)

    # Run the init command to set up the structure in the temp dir
    result = runner.invoke(app, ["storage", "init"])
    assert result.exit_code == 0, f"storage init failed: {result.stdout}"

    return tmp_path


def test_storage_init(temp_storage):
    """Test the 'storage init' command creates the expected structure."""
    data_dir = temp_storage

    # Check that directories were created
    assert (data_dir / "raw").is_dir()
    assert (data_dir / "processed").is_dir()
    assert (data_dir / "models").is_dir()
    assert (data_dir / "tmp").is_dir()

    # Check that the catalog was created
    db_path = data_dir / "catalog.db"
    assert db_path.is_file()

    # Check that tables were created in the catalog
    con = duckdb.connect(database=str(db_path), read_only=True)
    tables = con.execute("SHOW TABLES;").fetchall()
    table_names = {t[0] for t in tables}
    assert "datasets" in table_names
    assert "artifacts" in table_names


def test_register_and_data_path(temp_storage):
    """Test registering a dataset/artifact and using data_path to manage files."""
    data_dir = temp_storage

    # 1. Use data_path to get a path for a new raw file
    dummy_file_path = data_path(
        dataset_name="dummy_dataset", stage="raw", filename="data.txt"
    )

    # 2. Create a dummy file at that path
    dummy_file_path.write_text("hello world")
    assert dummy_file_path.exists()

    # 3. Register the dataset and artifact using the public API
    file_hash = calculate_sha256(dummy_file_path)
    file_size = dummy_file_path.stat().st_size

    register_dataset(
        name="dummy_dataset",
        source="local_test",
        version="1.0",
        description="A test dataset.",
    )

    register_artifact(
        dataset_name="dummy_dataset",
        stage="raw",
        relative_path=str(dummy_file_path.relative_to(data_dir)),
        file_hash=file_hash,
        file_size_bytes=file_size,
    )

    # 4. Verify registration in the database
    db_path = data_dir / "catalog.db"
    con = duckdb.connect(database=str(db_path), read_only=True)

    dataset_count = con.execute(
        "SELECT COUNT(*) FROM datasets WHERE name = 'dummy_dataset'"
    ).fetchone()[0]
    assert dataset_count == 1, "Dataset was not registered correctly."

    artifact_count = con.execute(
        "SELECT COUNT(*) FROM artifacts WHERE dataset_name = 'dummy_dataset'"
    ).fetchone()[0]
    assert artifact_count == 1, "Artifact was not registered correctly."

    artifact_hash_db = con.execute(
        "SELECT file_hash FROM artifacts WHERE dataset_name = 'dummy_dataset'"
    ).fetchone()[0]
    assert artifact_hash_db == file_hash, "Artifact hash does not match."
