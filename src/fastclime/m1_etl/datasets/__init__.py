from . import dem, smap, ndvi

DATASETS = {
    "dem": {"download": dem.download, "process": dem.process, "desc": dem.DESCRIPTION},
    "smap": {
        "download": smap.download,
        "process": smap.process,
        "desc": smap.DESCRIPTION,
    },
    "ndvi": {
        "download": ndvi.download,
        "process": ndvi.process,
        "desc": ndvi.DESCRIPTION,
    },
}
__all__ = ["DATASETS"]
