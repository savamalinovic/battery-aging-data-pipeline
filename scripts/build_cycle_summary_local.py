from pathlib import Path

import pandas as pd

from pipeline.raw.mat_loader import load_battery_mat
from pipeline.transforms.build_cycle_summary import build_cycle_summary_for_battery


RAW_DIR = Path("data/raw")
CLEANED_DIR = Path("data/cleaned")
QUALITY_DIR = Path("data/quality")


def main() -> None:
    CLEANED_DIR.mkdir(parents=True, exist_ok=True)
    QUALITY_DIR.mkdir(parents=True, exist_ok=True)

    all_summary_frames: list[pd.DataFrame] = []
    all_invalid_frames: list[pd.DataFrame] = []

    for file_path in sorted(RAW_DIR.glob("*.mat")):
        loaded = load_battery_mat(file_path)

        cycle_summary, invalid_cycles = build_cycle_summary_for_battery(
            battery_id=loaded["battery_id"],
            cycles=loaded["cycles"],
        )

        all_summary_frames.append(cycle_summary)

        if not invalid_cycles.empty:
            all_invalid_frames.append(invalid_cycles)

        print(
            f"{loaded['battery_id']}: "
            f"cycle_summary_rows={len(cycle_summary)}, "
            f"invalid_rows={len(invalid_cycles)}"
        )

    full_cycle_summary = pd.concat(all_summary_frames, ignore_index=True)

    if all_invalid_frames:
        full_invalid_cycles = pd.concat(all_invalid_frames, ignore_index=True)
    else:
        full_invalid_cycles = pd.DataFrame(
            columns=[
                "battery_id",
                "cycle_index",
                "operation_type",
                "error_code",
                "error_description",
                "severity",
                "excluded_from_analytics",
            ]
        )

    cycle_summary_path = CLEANED_DIR / "cycle_summary.parquet"
    invalid_cycles_path = QUALITY_DIR / "invalid_cycles.parquet"

    full_cycle_summary.to_parquet(cycle_summary_path, index=False)
    full_invalid_cycles.to_parquet(invalid_cycles_path, index=False)

    print()
    print(f"Wrote: {cycle_summary_path}")
    print(f"Wrote: {invalid_cycles_path}")
    print()
    print("Cycle summary shape:", full_cycle_summary.shape)
    print("Invalid cycles shape:", full_invalid_cycles.shape)
    print()
    print(full_cycle_summary.head())


if __name__ == "__main__":
    main()