from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from pathlib import Path
import os


class Settings(BaseSettings):
    """Manages application-wide settings, reading from .env files and environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_prefix="FASTCLIME_",  # Looks for FASTCLIME_DATA_DIR
    )

    # Project paths
    # The data directory can be overridden by the FASTCLIME_DATA_DIR env var.
    # Defaults to ~/.fastclime/data
    DATA_DIR: Path = Field(default_factory=lambda: Path.home() / ".fastclime" / "data")

    # Internal paths are derived from DATA_DIR
    @property
    def DIR_RAW(self) -> Path:
        return self.DATA_DIR / "raw"

    @property
    def DIR_PROCESSED(self) -> Path:
        return self.DATA_DIR / "processed"

    @property
    def DIR_MODELS(self) -> Path:
        return self.DATA_DIR / "models"

    @property
    def DIR_TMP(self) -> Path:
        return self.DATA_DIR / "tmp"

    @property
    def DIR_LOGS(self) -> Path:
        return self.DATA_DIR / "logs"

    # GDAL/PROJ environment variables
    GDAL_DATA: str | None = os.environ.get("GDAL_DATA")
    PROJ_LIB: str | None = os.environ.get("PROJ_LIB")

    def __init__(self, **values):
        super().__init__(**values)
        # If GDAL/PROJ paths are provided in settings, set them as environment variables
        if self.GDAL_DATA:
            os.environ["GDAL_DATA"] = str(self.GDAL_DATA)
        if self.PROJ_LIB:
            os.environ["PROJ_LIB"] = str(self.PROJ_LIB)


# Instantiate a global settings object to be used across the application
settings = Settings()
