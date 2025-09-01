"""
Dataset definition for MODIS/Terra 16-Day L3 Global 250m NDVI.
"""

from pathlib import Path
import datetime

from .. import utils
from ..constants import NETRC_PATH
from fastclime.core.logging import get_logger

log = get_logger(__name__)

DESCRIPTION = "MODIS 16-Day 250m NDVI"


def download(
    year: int, day_of_year: int, bbox: list[float], temp_dir: Path, **kwargs
) -> list[Path]:
    """
    Finds and downloads 16-day NDVI HDF4 files using the CMR API.
    The day_of_year should correspond to the start of a 16-day period.
    """
    if not NETRC_PATH.exists():
        raise FileNotFoundError(
            f"Earthdata login required. Please create a '{NETRC_PATH}' file."
        )

    start_date = datetime.datetime(year, 1, 1) + datetime.timedelta(day_of_year - 1)
    end_date = start_date + datetime.timedelta(days=15)
    temporal_range = (
        start_date.strftime("%Y-%m-%dT00:00:00Z"),
        end_date.strftime("%Y-%m-%dT23:59:59Z"),
    )

    urls = utils.search_nasa_cmr(
        short_name="MOD13Q1",
        version="061",  # Note: v006 is often specified as 061 in CMR
        temporal_range=temporal_range,
        bbox=bbox,
    )

    downloaded_files = []
    for url in urls:
        filename = url.split("/")[-1]
        dst_path = temp_dir / filename
        utils.download_file(url=url, dst=dst_path)
        downloaded_files.append(dst_path)

    if not downloaded_files:
        raise FileNotFoundError(
            f"No NDVI files found for period starting {start_date.date()}"
        )

    return downloaded_files


def process(
    raw_files: list[Path], processed_dir: Path, year: int, day_of_year: int, **kwargs
) -> Path:
    """
    Extracts NDVI from HDF4, merges, and saves as a single GeoTIFF.
    """
    # Placeholder: a real implementation would merge tiles before converting.
    # For now, we process only the first file found.
    log.warning(
        "NDVI processing is simplified and only processes the first tile found."
    )
    raw_file = raw_files[0]

    # The NDVI data is typically the first subdataset in MOD13Q1
    subdataset_index = 0

    final_path = processed_dir / str(year) / f"NDVI_{year}{day_of_year:03d}.tif"
    final_path.parent.mkdir(parents=True, exist_ok=True)

    utils.hdf4_to_geotiff(raw_file, final_path, subdataset_index=subdataset_index)

    log.info(f"Successfully processed NDVI and saved to {final_path}")
    return final_path
