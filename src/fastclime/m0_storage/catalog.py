import duckdb
from pathlib import Path
import uuid
from datetime import datetime

from fastclime.config import settings
from fastclime.core.logging import get_logger

log = get_logger(__name__)


class DataCatalog:
    """Manages the DuckDB catalog for datasets and artifacts."""

    def __init__(self, db_path: Path | None = None):
        self.db_path = db_path or settings.DATA_DIR / "catalog.db"
        self._ensure_db_path_exists()

    def _ensure_db_path_exists(self):
        """Ensures the parent directory for the database exists."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def get_connection(self) -> duckdb.DuckDBPyConnection:
        """Returns a connection to the DuckDB database."""
        return duckdb.connect(database=str(self.db_path), read_only=False)

    def init_catalog(self):
        """Creates the necessary tables if they don't exist."""
        log.info(f"Initializing data catalog at: {self.db_path}")
        with self.get_connection() as con:
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS datasets (
                    name VARCHAR PRIMARY KEY,
                    source VARCHAR,
                    version VARCHAR,
                    description VARCHAR,
                    created_at TIMESTAMP DEFAULT current_timestamp
                );
            """
            )
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS artifacts (
                    id UUID PRIMARY KEY,
                    dataset_name VARCHAR,
                    stage VARCHAR, -- e.g., raw, processed
                    relative_path VARCHAR,
                    file_hash VARCHAR,
                    file_size_bytes BIGINT,
                    created_at TIMESTAMP DEFAULT current_timestamp,
                    FOREIGN KEY(dataset_name) REFERENCES datasets(name)
                );
            """
            )
            log.info("Catalog tables created successfully.")

    def register_dataset(self, name: str, source: str, version: str, description: str):
        """Registers a new dataset metadata."""
        with self.get_connection() as con:
            con.execute(
                "INSERT OR IGNORE INTO datasets (name, source, version, description) VALUES (?, ?, ?, ?)",
                (name, source, version, description),
            )
        log.info(f"Registered dataset '{name}' version '{version}'.")

    def register_artifact(
        self,
        dataset_name: str,
        stage: str,
        relative_path: str,
        file_hash: str,
        file_size_bytes: int,
    ) -> uuid.UUID:
        """Registers a file artifact and returns its UUID."""
        artifact_id = uuid.uuid4()
        with self.get_connection() as con:
            con.execute(
                """
                INSERT INTO artifacts (id, dataset_name, stage, relative_path, file_hash, file_size_bytes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    artifact_id,
                    dataset_name,
                    stage,
                    relative_path,
                    file_hash,
                    file_size_bytes,
                    datetime.now(),
                ),
            )
        log.info(
            f"Registered artifact for dataset '{dataset_name}' at '{relative_path}'."
        )
        return artifact_id
