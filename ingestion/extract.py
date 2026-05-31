import hashlib
import zipfile
from pathlib import Path


def calculate_sha256(path: Path) -> str:
    sha256 = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            sha256.update(chunk)

    return sha256.hexdigest()


def calculate_bytes_sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def is_zip_file(name: str) -> bool:
    return name.lower().endswith(".zip")


def is_mat_file(name: str) -> bool:
    return name.lower().endswith(".mat")


def write_mat_file(
    filename: str,
    content: bytes,
    raw_output_dir: Path,
    overwrite: bool,
) -> Path:
    raw_output_dir.mkdir(parents=True, exist_ok=True)

    output_path = raw_output_dir / filename

    if not content:
        raise ValueError(f"Empty .mat file content: {filename}")

    if output_path.exists() and not overwrite:
        existing_hash = calculate_sha256(output_path)
        new_hash = calculate_bytes_sha256(content)

        if existing_hash == new_hash:
            print(f"Skipping duplicate identical .mat file: {output_path}")
            return output_path

        raise FileExistsError(
            f"File already exists with different content: {output_path}. "
            "Set INGESTION_OVERWRITE=true only if replacement is intentional."
        )

    output_path.write_bytes(content)
    print(f"Extracted .mat file: {output_path}")

    return output_path


def extract_nested_zip_file(
    zip_content: bytes,
    zip_name: str,
    raw_output_dir: Path,
    nested_zip_dir: Path,
    overwrite: bool,
) -> list[Path]:
    nested_zip_dir.mkdir(parents=True, exist_ok=True)

    nested_zip_path = nested_zip_dir / Path(zip_name).name
    nested_zip_path.write_bytes(zip_content)

    print(f"Extracting nested ZIP: {nested_zip_path}")

    return extract_mat_files_from_zip(
        zip_path=nested_zip_path,
        raw_output_dir=raw_output_dir,
        nested_zip_dir=nested_zip_dir,
        overwrite=overwrite,
    )


def extract_mat_files_from_zip(
    zip_path: Path,
    raw_output_dir: Path,
    nested_zip_dir: Path,
    overwrite: bool = False,
) -> list[Path]:
    extracted_files: list[Path] = []

    print(f"Reading ZIP: {zip_path}")

    with zipfile.ZipFile(zip_path, "r") as archive:
        for member in archive.namelist():
            if member.endswith("/"):
                continue

            filename = Path(member).name

            if not filename:
                continue

            with archive.open(member) as source:
                content = source.read()

            if is_mat_file(filename):
                extracted_path = write_mat_file(
                    filename=filename,
                    content=content,
                    raw_output_dir=raw_output_dir,
                    overwrite=overwrite,
                )
                extracted_files.append(extracted_path)

            elif is_zip_file(filename):
                nested_extracted = extract_nested_zip_file(
                    zip_content=content,
                    zip_name=filename,
                    raw_output_dir=raw_output_dir,
                    nested_zip_dir=nested_zip_dir,
                    overwrite=overwrite,
                )
                extracted_files.extend(nested_extracted)

    return extracted_files