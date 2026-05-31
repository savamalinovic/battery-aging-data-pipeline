from ingestion.config import load_config
from ingestion.download import download_file
from ingestion.extract import extract_mat_files_from_zip


def main() -> None:
    config = load_config()

    if not config.source_archive_url:
        raise ValueError(
            "No SOURCE_ARCHIVE_URL configured. Add the outer dataset ZIP URL to .env."
        )

    print("Starting nested ZIP ingestion")
    print("=" * 80)

    outer_zip_path = download_file(
        url=config.source_archive_url,
        output_dir=config.download_local_dir,
        overwrite=config.overwrite,
    )

    nested_zip_dir = config.download_local_dir / "nested_zips"

    extracted_mat_files = extract_mat_files_from_zip(
        zip_path=outer_zip_path,
        raw_output_dir=config.raw_local_dir,
        nested_zip_dir=nested_zip_dir,
        overwrite=config.overwrite,
    )

    unique_mat_files = sorted(set(extracted_mat_files))

    print("=" * 80)
    print("Ingestion completed successfully.")
    print(f"Outer ZIP file: {outer_zip_path}")
    print(f"Available .mat files: {len(unique_mat_files)}")

    for file_path in unique_mat_files:
        print(f"- {file_path}")


if __name__ == "__main__":
    main()