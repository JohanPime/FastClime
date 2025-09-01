"""Shared constants for the ETL module."""

from pathlib import Path
import tempfile

from fastclime.config import settings

# --- Dirs ---
# Base data directory from global settings
DATA_DIR = settings.DATA_DIR
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
TMP_DIR = Path(tempfile.gettempdir()) / "fastclime_etl_tmp"

# --- CRS ---
TARGET_CRS = "EPSG:4326"  # WGS 84 (latitude/longitude)

# --- File Extensions ---
GEOTIFF_EXT = ".tif"
PARQUET_EXT = ".parquet"
HDF5_EXT = ".h5"
HDF4_EXT = ".hdf"

# --- Earthdata Login ---
# For downloading NASA datasets (e.g., SMAP, NDVI)
# A .netrc file in the user's home directory is the standard way.
NETRC_PATH = Path.home() / ".netrc"
