"""
Dataset definition for SMAP L3 Daily Soil Moisture.
"""

from pathlib import Path
import datetime

from .. import utils
from ..constants import NETRC_PATH
from fastclime.core.logging import get_logger

log = get_logger(__name__)

DESCRIPTION = "SMAP L3 Daily 9km Soil Moisture"


def download(
    year: int, day_of_year: int, bbox: list[float], temp_dir: Path, **kwargs
) -> list[Path]:
    """
    Finds and downloads daily SMAP L3 HDF5 files using the CMR API.
    """
    if not NETRC_PATH.exists():
        raise FileNotFoundError(
            f"Earthdata login required. Please create a '{NETRC_PATH}' file."
        )

    date = datetime.datetime(year, 1, 1) + datetime.timedelta(day_of_year - 1)
    temporal_range = (
        date.strftime("%Y-%m-%dT00:00:00Z"),
        date.strftime("%Y-%m-%dT23:59:59Z"),
    )

    urls = utils.search_nasa_cmr(
        short_name="SPL3SMP",
        version="009",
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
        raise FileNotFoundError(f"No SMAP files found for {date.date()}")

    return downloaded_files


def process(
    raw_files: list[Path], processed_dir: Path, year: int, day_of_year: int, **kwargs
) -> Path:
    """
    Extracts the soil moisture data from HDF5 and saves as Parquet.
    """
    raw_file = raw_files[0]
    var_name = "Soil_Moisture_Retrieval_Data/soil_moisture"

    final_path = processed_dir / str(year) / f"SMAP_{year}{day_of_year:03d}.parquet"
    final_path.parent.mkdir(parents=True, exist_ok=True)

    utils.hdf5_to_parquet(raw_file, final_path, var_name=var_name)

    log.info(f"Successfully processed SMAP and saved to {final_path}")
    return final_path
