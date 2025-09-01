"""Utility functions for the ETL pipeline."""

import hashlib
import time
from pathlib import Path

import requests
from tqdm import tqdm
from fastclime.core.logging import get_logger
import rasterio
from rasterio.merge import merge
from rasterio.warp import calculate_default_transform, reproject, Resampling
from rasterio.mask import mask
from shapely.geometry import box
import geopandas as gpd
import h5py
import pandas as pd
import numpy as np

from .constants import TARGET_CRS

log = get_logger(__name__)


def download_file(
    url: str, dst: Path, expected_sha: str | None = None, retries: int = 3
):
    """
    Downloads a file with retries, progress bar, and optional SHA256 verification.
    Skips download if a file with the correct SHA already exists.
    """
    dst.parent.mkdir(parents=True, exist_ok=True)

    if dst.exists() and expected_sha:
        log.debug(f"File {dst} exists. Verifying SHA...")
        local_sha = hashlib.sha256(dst.read_bytes()).hexdigest()
        if local_sha == expected_sha:
            log.info(
                f"File '{dst.name}' already exists with matching SHA. Skipping download."
            )
            return
        else:
            log.warning(
                f"File '{dst.name}' exists but SHA is incorrect. Re-downloading."
            )

    log.info(f"Downloading '{url}' to '{dst}'...")
    for attempt in range(retries):
        try:
            with requests.get(url, stream=True, timeout=60) as r:
                r.raise_for_status()
                total_size = int(r.headers.get("content-length", 0))

                with (
                    open(dst, "wb") as f,
                    tqdm(
                        total=total_size,
                        unit="iB",
                        unit_scale=True,
                        desc=f"Downloading {dst.name}",
                    ) as pbar,
                ):
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                        pbar.update(len(chunk))

            if expected_sha:
                local_sha = hashlib.sha256(dst.read_bytes()).hexdigest()
                if local_sha != expected_sha:
                    raise ValueError(
                        f"SHA mismatch for {dst.name}. Expected {expected_sha}, got {local_sha}"
                    )
                else:
                    log.info(f"Successfully downloaded and verified {dst.name}.")
            return  # Success
        except (requests.exceptions.RequestException, ValueError) as e:
            log.warning(f"Attempt {attempt + 1}/{retries} failed for '{url}': {e}")
            if attempt + 1 < retries:
                time.sleep(5 * (2**attempt))  # Exponential backoff
            else:
                log.error(f"Failed to download '{url}' after {retries} attempts.")
                raise


def merge_rasters(raster_paths: list[Path], out_path: Path):
    """Merges multiple raster files into a single mosaic."""
    log.info(f"Merging {len(raster_paths)} rasters into '{out_path}'...")
    to_merge = [rasterio.open(p) for p in raster_paths]
    mosaic, out_trans = merge(to_merge)

    out_meta = to_merge[0].meta.copy()
    out_meta.update(
        {
            "driver": "GTiff",
            "height": mosaic.shape[1],
            "width": mosaic.shape[2],
            "transform": out_trans,
        }
    )

    with rasterio.open(out_path, "w", **out_meta) as dest:
        dest.write(mosaic)

    for src in to_merge:
        src.close()
    log.info("Merging complete.")


def reproject_raster(
    src: Path, dst: Path, crs: str = TARGET_CRS, bbox: list | None = None
):
    """
    Reprojects a raster to a new CRS and optionally clips it to a bounding box.
    """
    log.info(f"Reprojecting '{src}' to '{dst}' (CRS: {crs}, Bbox: {bbox})...")
    dst.parent.mkdir(parents=True, exist_ok=True)

    with rasterio.open(src) as dataset:
        # Use a clipping mask if bbox is provided
        if bbox:
            clip_geom = box(*bbox)
            gdf = gpd.GeoDataFrame([1], geometry=[clip_geom], crs=TARGET_CRS)

            # Ensure the geometry CRS matches the dataset CRS before clipping
            gdf = gdf.to_crs(dataset.crs)

            out_image, out_transform = rasterio.mask.mask(
                dataset, gdf.geometry, crop=True
            )
            out_meta = dataset.meta.copy()
            out_meta.update(
                {
                    "driver": "GTiff",
                    "height": out_image.shape[1],
                    "width": out_image.shape[2],
                    "transform": out_transform,
                }
            )
            # Write clipped raster to a temporary file for reprojection
            temp_clipped_path = dst.with_suffix(".clipped.tif")
            with rasterio.open(temp_clipped_path, "w", **out_meta) as f:
                f.write(out_image)

            # The source for reprojection is now the clipped file
            src_for_reprojection = temp_clipped_path
        else:
            # No clipping, reproject the original source
            src_for_reprojection = src

        with rasterio.open(src_for_reprojection) as reproj_src:
            transform, width, height = calculate_default_transform(
                reproj_src.crs,
                crs,
                reproj_src.width,
                reproj_src.height,
                *reproj_src.bounds,
            )
            kwargs = reproj_src.meta.copy()
            kwargs.update(
                {
                    "crs": crs,
                    "transform": transform,
                    "width": width,
                    "height": height,
                }
            )

            with rasterio.open(dst, "w", **kwargs) as dest:
                for i in range(1, reproj_src.count + 1):
                    reproject(
                        source=rasterio.band(reproj_src, i),
                        destination=rasterio.band(dest, i),
                        src_transform=reproj_src.transform,
                        src_crs=reproj_src.crs,
                        dst_transform=transform,
                        dst_crs=crs,
                        resampling=Resampling.bilinear,
                    )

    # Clean up temporary clipped file if it was created
    if "temp_clipped_path" in locals() and temp_clipped_path.exists():
        temp_clipped_path.unlink()

    log.info("Reprojection complete.")


def to_cog(src: Path, dst: Path):
    """Converts a GeoTIFF to a Cloud Optimized GeoTIFF (COG)."""
    log.info(f"Converting '{src}' to COG format at '{dst}'...")
    dst.parent.mkdir(parents=True, exist_ok=True)

    with rasterio.open(src, "r") as src_dataset:
        profile = src_dataset.profile.copy()
        profile.update(
            {
                "driver": "COG",
                "compress": "LZW",
                "blocksize": 512,
            }
        )
        overview_level = 6
        overviews = [2**j for j in range(1, overview_level + 1)]

        with rasterio.open(dst, "w", **profile) as dst_dataset:
            dst_dataset.write(src_dataset.read())
            dst_dataset.build_overviews(overviews, Resampling.average)

    log.info("COG conversion complete.")


def hdf4_to_geotiff(src: Path, dst: Path, subdataset_index: int):
    """
    Extracts a specific subdataset from an HDF4 file and saves it as a GeoTIFF.
    """
    log.info(
        f"Extracting subdataset index {subdataset_index} from HDF4 '{src}' to '{dst}'..."
    )
    dst.parent.mkdir(parents=True, exist_ok=True)

    with rasterio.open(f"HDF4_EOS:EOS_GRID:{src}:{subdataset_index}") as band:
        meta = band.meta
        meta["driver"] = "GTiff"
        with rasterio.open(dst, "w", **meta) as dst_dataset:
            dst_dataset.write(band.read(1))
    log.info("HDF4 to GeoTIFF conversion complete.")


def hdf5_to_parquet(src: Path, dst: Path, var_name: str):
    """
    Extracts a variable from an HDF5 file, handles fill values, and saves as Parquet.
    """
    log.info(f"Extracting variable '{var_name}' from HDF5 '{src}' to '{dst}'...")
    dst.parent.mkdir(parents=True, exist_ok=True)

    with h5py.File(src, "r") as hf:
        dataset = hf[var_name]
        data = dataset[:]

        # Handle fill values, which are common in NASA datasets
        fill_value = dataset.attrs.get("_FillValue")
        if fill_value is not None:
            data = np.where(data == fill_value, np.nan, data)

        # For simplicity, we flatten the 2D array and save it as a single column.
        # A more advanced implementation could preserve lat/lon.
        flat_data = data.flatten()
        df = pd.DataFrame({"value": flat_data})
        df.dropna(inplace=True)

        df.to_parquet(dst)
    log.info("HDF5 to Parquet conversion complete.")


def search_nasa_cmr(
    short_name: str, version: str, temporal_range: tuple[str, str], bbox: list[float]
) -> list[str]:
    """
    Searches the NASA CMR for data granules and returns their download URLs.
    """
    cmr_url = "https://cmr.earthdata.nasa.gov/search/granules.json"
    params = {
        "short_name": short_name,
        "version": version,
        "temporal": f"{temporal_range[0]},{temporal_range[1]}",
        "bounding_box": ",".join(map(str, bbox)),
        "page_size": 200,  # Max allowed page size
    }
    log.info(f"Searching CMR with params: {params}")

    response = requests.get(cmr_url, params=params)
    response.raise_for_status()
    data = response.json()

    urls = []
    if "feed" in data and "entry" in data["feed"]:
        for entry in data["feed"]["entry"]:
            # Find the download link, usually of type 'GET DATA' via HTTPS
            for link in entry.get("links", []):
                if link.get("rel", "").endswith("#data") and "https" in link.get(
                    "href", ""
                ):
                    urls.append(link["href"])
                    break

    if not urls:
        log.warning(f"No granules found for {short_name} with the given parameters.")

    return urls
