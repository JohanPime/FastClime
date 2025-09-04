"""Global fixtures for the test suite."""

import pytest
from pathlib import Path
import duckdb
import pathlib

from fastclime.config import settings
from fastclime.m0_storage.catalog import DataCatalog
from fastclime.m3_ml.train import _ensure_tables

@pytest.fixture(scope="function")
def mock_etl_env(tmp_path: Path, monkeypatch, db_path):
    """
    Creates a self-contained, temporary environment for ETL tests.

    This fixture provides:
    - A temporary DATA_DIR.
    - An initialized DataCatalog within that directory.
    - Mocks for file system structures (raw, processed, temp dirs).
    - Patches config settings to use the temporary directory.

    Returns:
        A dictionary with paths to the created directories and files.
    """
    # 1. Create temporary directories
    data_dir = tmp_path / "data"
    raw_dir = data_dir / "raw"
    processed_dir = data_dir / "processed"
    temp_dir = tmp_path / "temp"

    data_dir.mkdir()
    raw_dir.mkdir()
    processed_dir.mkdir()
    temp_dir.mkdir()

    # 2. Patch the settings to use this temporary data directory
    monkeypatch.setattr(settings, "DATA_DIR", data_dir)

    # The modules that use settings.DATA_DIR might have already been imported.
    # We need to reload them to pick up the patched setting.
    # This is a bit of a hack, but necessary for this kind of patching.
    import importlib
    from fastclime.m1_etl import constants
    from fastclime.m1_etl import orchestrator

    importlib.reload(constants)
    importlib.reload(orchestrator)

    # 3. The catalog is handled by the autouse patch_catalog fixture.
    # We just need to ensure the schema is initialized for this test's db.
    catalog = DataCatalog(db_path=db_path)
    catalog.init_catalog()

    # 4. Return paths for the test to use
    env = {
        "data_dir": data_dir,
        "raw_dir": raw_dir,
        "processed_dir": processed_dir,
        "temp_dir": temp_dir,
    }
    return env


@pytest.fixture(scope="session")
def db_path(tmp_path_factory) -> pathlib.Path:
    """Ruta temporal para la base DuckDB usada en integración."""
    return tmp_path_factory.mktemp("db") / "catalog.db"

@pytest.fixture(scope="session", autouse=True)
def bootstrap_catalog(db_path):
    import fastclime.m0_storage.catalog as cat_mod
    con = duckdb.connect(str(db_path))
    _ensure_tables(con)
    con.close()
    cat_mod._CATALOG_SINGLETON = cat_mod.DataCatalog(db_path)
