import os
from pathlib import Path

from dotenv import load_dotenv

from pipeline.main import main as run_local_pipeline
from pipeline.s3_io import download_s3_prefix, upload_directory_to_s3


def require_env(name: str) -> str:
    value = os.getenv(name, "").strip()

    if not value:
        raise ValueError(f"Missing required environment variable: {name}")

    return value


def main() -> None:
    load_dotenv()

    aws_region = os.getenv("AWS_REGION", "eu-central-1")
    bucket = require_env("S3_BUCKET")

    local_data_dir = Path(os.getenv("LOCAL_DATA_DIR", "data"))

    raw_local_dir = local_data_dir / "raw"
    cleaned_local_dir = local_data_dir / "cleaned"
    analytics_local_dir = local_data_dir / "analytics"
    quality_local_dir = local_data_dir / "quality"
    dashboard_local_dir = local_data_dir / "dashboard"

    s3_raw_prefix = os.getenv("S3_RAW_PREFIX", "raw/mat/")
    s3_cleaned_prefix = os.getenv("S3_CLEANED_PREFIX", "output/cleaned/")
    s3_analytics_prefix = os.getenv("S3_ANALYTICS_PREFIX", "output/analytics/")
    s3_quality_prefix = os.getenv("S3_QUALITY_PREFIX", "output/quality/")
    s3_dashboard_prefix = os.getenv("S3_DASHBOARD_PREFIX", "output/dashboard/")

    print("Starting cloud pipeline wrapper")
    print("=" * 80)

    print("Downloading raw .mat files from S3...")
    downloaded_files = download_s3_prefix(
        bucket=bucket,
        prefix=s3_raw_prefix,
        local_dir=raw_local_dir,
        region_name=aws_region,
        suffix_filter=".mat",
    )

    if not downloaded_files:
        raise FileNotFoundError(
            f"No .mat files found in s3://{bucket}/{s3_raw_prefix}"
        )

    print(f"Downloaded .mat files: {len(downloaded_files)}")

    print("=" * 80)
    print("Running local pipeline inside container...")
    run_local_pipeline()

    print("=" * 80)
    print("Uploading outputs to S3...")

    upload_directory_to_s3(
        local_dir=cleaned_local_dir,
        bucket=bucket,
        prefix=s3_cleaned_prefix,
        region_name=aws_region,
        suffix_filter=".parquet",
    )

    upload_directory_to_s3(
        local_dir=analytics_local_dir,
        bucket=bucket,
        prefix=s3_analytics_prefix,
        region_name=aws_region,
        suffix_filter=".parquet",
    )

    upload_directory_to_s3(
        local_dir=quality_local_dir,
        bucket=bucket,
        prefix=s3_quality_prefix,
        region_name=aws_region,
        suffix_filter=".parquet",
    )

    upload_directory_to_s3(
        local_dir=dashboard_local_dir,
        bucket=bucket,
        prefix=s3_dashboard_prefix,
        region_name=aws_region,
        suffix_filter=".parquet",
    )

    print("=" * 80)
    print("Cloud pipeline completed successfully.")


if __name__ == "__main__":
    main()