from pathlib import Path

from pipeline.raw.mat_loader import summarize_battery_file

RAW_DIR = Path("data/raw")


def main() -> None:
    mat_files = sorted(RAW_DIR.glob("*.mat"))

    if not mat_files:
        raise FileNotFoundError(f"No .mat files found in {RAW_DIR}")

    for file_path in mat_files:
        summary = summarize_battery_file(file_path)
        print(
            f"{summary['battery_id']}: "
            f"total={summary['total_cycles']}, "
            f"charge={summary['charge_cycles']}, "
            f"discharge={summary['discharge_cycles']}, "
            f"impedance={summary['impedance_cycles']}, "
            f"unknown={summary['unknown_cycles']}"
        )


if __name__ == "__main__":
    main()