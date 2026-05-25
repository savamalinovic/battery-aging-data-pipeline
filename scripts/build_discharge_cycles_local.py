from pathlib import Path

import pandas as pd

from pipeline.transforms.build_discharge_cycles import (
    build_discharge_cycles,
)


CYCLE_SUMMARY_PATH = Path(
    "data/cleaned/cycle_summary.parquet"
)

OUTPUT_PATH = Path(
    "data/cleaned/discharge_cycles.parquet"
)


def main() -> None:
    cycle_summary = pd.read_parquet(
        CYCLE_SUMMARY_PATH
    )

    discharge_cycles = build_discharge_cycles(
        cycle_summary
    )

    discharge_cycles.to_parquet(
        OUTPUT_PATH,
        index=False,
    )

    print()
    print(f"Wrote: {OUTPUT_PATH}")
    print()

    print("Shape:")
    print(discharge_cycles.shape)

    print()
    print("Columns:")
    print(discharge_cycles.columns.tolist())

    print()
    print("Life stage counts:")
    print(
        discharge_cycles["life_stage"]
        .value_counts(dropna=False)
    )

    print()
    print(discharge_cycles.head())


if __name__ == "__main__":
    main()