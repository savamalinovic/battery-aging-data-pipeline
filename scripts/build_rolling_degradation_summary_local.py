from pathlib import Path

import pandas as pd

from pipeline.analytics.rolling_degradation import (
    build_rolling_degradation_summary,
)


INPUT_PATH = Path("data/cleaned/discharge_cycles.parquet")
OUTPUT_DIR = Path("data/analytics")
OUTPUT_PATH = OUTPUT_DIR / "rolling_degradation_summary.parquet"


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    discharge_cycles = pd.read_parquet(INPUT_PATH)

    rolling_degradation = build_rolling_degradation_summary(
        discharge_cycles
    )

    rolling_degradation.to_parquet(
        OUTPUT_PATH,
        index=False,
    )

    print(f"Wrote: {OUTPUT_PATH}")
    print()

    print("Shape:")
    print(rolling_degradation.shape)

    print()
    print(rolling_degradation.head(20))


if __name__ == "__main__":
    main()