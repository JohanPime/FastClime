"""
Dataset definition for Copernicus DEM GLO-30.
"""

import math
from pathlib import Path

from .. import utils
from fastclime.core.logging import get_logger

log = get_logger(__name__)

DESCRIPTION = "Copernicus 30 m DEM"


def download(year: int, bbox: list[float], temp_dir: Path, **kwargs) -> list[Path]:
    """
    Downloads Copernicus GLO-30 DEM tiles for a given bounding box.
    """
    base_url = "https://copernicus-dem-30m.s3.amazonaws.com"
    downloaded_files = []

    min_lon, min_lat, max_lon, max_lat = bbox
    start_lon = math.floor(min_lon)
    end_lon = math.ceil(max_lon)
    start_lat = math.floor(min_lat)
    end_lat = math.ceil(max_lat)

    for lon in range(start_lon, end_lon):
        for lat in range(start_lat, end_lat):
            ns = "N" if lat >= 0 else "S"
            ew = "E" if lon >= 0 else "W"
            lat_str = f"{abs(lat):02d}"
            lon_str = f"{abs(lon):03d}"

            tile_name = f"Copernicus_DSM_COG_10_{ns}{lat_str}_00_{ew}{lon_str}_00_DEM"
            file_url = f"{base_url}/{tile_name}/{tile_name}.tif"
            dst_path = temp_dir / f"{tile_name}.tif"

            try:
                utils.download_file(url=file_url, dst=dst_path)
                downloaded_files.append(dst_path)
            except Exception as e:
                log.warning(
                    f"Could not download tile {tile_name}: {e}. Likely an ocean tile."
                )

    if not downloaded_files:
        raise FileNotFoundError(
            f"No DEM tiles found for the given bounding box: {bbox}"
        )

    return downloaded_files


def process(
    raw_files: list[Path],
    processed_dir: Path,
    year: int,
    bbox: list[float],
    temp_dir: Path,
    **kwargs,
) -> Path:
    """
    Merges, reprograms, clips, and converts DEM tiles to a final COG.
    """
    log.info(f"Starting processing for {len(raw_files)} DEM tiles...")
    merged_path = temp_dir / "dem_merged.tif"
    reprojected_path = temp_dir / "dem_reprojected.tif"
    final_cog_path = processed_dir / str(year) / f"DEM_{'_'.join(map(str, bbox))}.tif"
    final_cog_path.parent.mkdir(parents=True, exist_ok=True)

    utils.merge_rasters(raw_files, merged_path)
    utils.reproject_raster(merged_path, reprojected_path, bbox=bbox)
    utils.to_cog(reprojected_path, final_cog_path)

    merged_path.unlink()
    reprojected_path.unlink()

    log.info(f"Successfully processed DEM and saved to {final_cog_path}")
    return final_cog_path
