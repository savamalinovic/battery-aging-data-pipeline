from pathlib import Path

import boto3


def get_s3_client(region_name: str | None = None):
    return boto3.client("s3", region_name=region_name)


def download_s3_prefix(
    bucket: str,
    prefix: str,
    local_dir: Path,
    region_name: str | None = None,
    suffix_filter: str | None = None,
) -> list[Path]:
    local_dir.mkdir(parents=True, exist_ok=True)

    s3 = get_s3_client(region_name)

    paginator = s3.get_paginator("list_objects_v2")

    downloaded_files: list[Path] = []

    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get("Contents", []):
            key = obj["Key"]

            if key.endswith("/"):
                continue

            if suffix_filter is not None and not key.endswith(suffix_filter):
                continue

            filename = Path(key).name
            local_path = local_dir / filename

            print(f"Downloading s3://{bucket}/{key} -> {local_path}")

            s3.download_file(
                Bucket=bucket,
                Key=key,
                Filename=str(local_path),
            )

            downloaded_files.append(local_path)

    return downloaded_files


def upload_directory_to_s3(
    local_dir: Path,
    bucket: str,
    prefix: str,
    region_name: str | None = None,
    suffix_filter: str | None = None,
) -> list[str]:
    if not local_dir.exists():
        raise FileNotFoundError(f"Local directory does not exist: {local_dir}")

    s3 = get_s3_client(region_name)

    uploaded_keys: list[str] = []

    for file_path in sorted(local_dir.rglob("*")):
        if not file_path.is_file():
            continue

        if suffix_filter is not None and not file_path.name.endswith(suffix_filter):
            continue

        relative_path = file_path.relative_to(local_dir)
        s3_key = f"{prefix.rstrip('/')}/{relative_path.as_posix()}"

        print(f"Uploading {file_path} -> s3://{bucket}/{s3_key}")

        s3.upload_file(
            Filename=str(file_path),
            Bucket=bucket,
            Key=s3_key,
        )

        uploaded_keys.append(s3_key)

    return uploaded_keys