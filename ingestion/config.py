import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class IngestionConfig:
    source_archive_url: str
    download_local_dir: Path
    raw_local_dir: Path
    overwrite: bool


def parse_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default

    return value.strip().lower() in {"1", "true", "yes", "y"}


def load_config() -> IngestionConfig:
    load_dotenv()

    source_archive_url = os.getenv("SOURCE_ARCHIVE_URL", "").strip()

    download_local_dir = Path(
        os.getenv("DOWNLOAD_LOCAL_DIR", "data/downloads")
    )

    raw_local_dir = Path(
        os.getenv("RAW_LOCAL_DIR", "data/raw")
    )

    overwrite = parse_bool(
        os.getenv("INGESTION_OVERWRITE"),
        default=False,
    )

    return IngestionConfig(
        source_archive_url=source_archive_url,
        download_local_dir=download_local_dir,
        raw_local_dir=raw_local_dir,
        overwrite=overwrite,
    )