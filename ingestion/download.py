from pathlib import Path
from urllib.parse import urlparse

import requests


def get_filename_from_url(url: str) -> str:
    parsed = urlparse(url)
    filename = Path(parsed.path).name

    if not filename:
        raise ValueError(f"Could not determine filename from URL: {url}")

    return filename


def download_file(
    url: str,
    output_dir: Path,
    overwrite: bool = False,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)

    filename = get_filename_from_url(url)
    output_path = output_dir / filename

    if output_path.exists() and not overwrite:
        print(f"Skipping existing download: {output_path}")
        return output_path

    print(f"Downloading: {url}")
    response = requests.get(url, timeout=120)
    response.raise_for_status()

    if not response.content:
        raise ValueError(f"Downloaded empty response from: {url}")

    output_path.write_bytes(response.content)

    file_size = output_path.stat().st_size

    if file_size == 0:
        raise ValueError(f"Downloaded empty file: {output_path}")

    print(f"Wrote: {output_path} ({file_size} bytes)")

    return output_path