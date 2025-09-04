"""Tests for the M1 ETL Ingest pipeline."""

from pathlib import Path
from fastclime.m1_etl import ingest
from fastclime.m0_storage.catalog import DataCatalog


def test_dem_ingest_pipeline(mocker, mock_etl_env, db_path):
    """
    Tests the full DEM ingest pipeline using mocked downloads and processing.
    """
    # Arrange
    BBOX = [-78.5, 8.5, -78.0, 9.0]
    YEAR = 2021

    # Mock the download function to create dummy files
    mocker.patch(
        "fastclime.m1_etl.datasets.dem.download",
        return_value=[mock_etl_env["temp_dir"] / "dummy_dem.tif"],
    )
    # Mock the process function to create a dummy final file
    final_file = mock_etl_env["processed_dir"] / "dem" / str(YEAR) / "final_dem.tif"
    final_file.parent.mkdir(parents=True, exist_ok=True)
    final_file.touch()

    mocker.patch(
        "fastclime.m1_etl.datasets.dem.process",
        return_value=final_file,
    )

    # Act
    stats = ingest(dataset_name="dem", year=YEAR, bbox=BBOX)

    # Assert
    # Check that the final file exists
    final_path = Path(stats["processed_file_path"])
    assert final_path.exists()

    # Check the catalog
    catalog = DataCatalog(db_path=db_path)
    with catalog.get_connection() as con:
        dataset_entry = con.execute(
            "SELECT * FROM datasets WHERE name = 'dem'"
        ).fetchone()
        assert dataset_entry is not None

        artifact_entry = con.execute(
            "SELECT * FROM artifacts WHERE dataset_name = 'dem'"
        ).fetchone()
        assert artifact_entry is not None
        assert artifact_entry[3] == str(
            final_path.relative_to(mock_etl_env["data_dir"])
        )
