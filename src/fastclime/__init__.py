import importlib.metadata

try:
    __version__ = importlib.metadata.version("fastclime")
except importlib.metadata.PackageNotFoundError:
    # Fallback for when the package is not installed
    __version__ = "0.0.1"
