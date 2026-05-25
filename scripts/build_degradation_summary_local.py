from pathlib import Path

import pandas as pd

from pipeline.analytics.degradation import (
    build_degradation_summary,
)


INPUT_PATH = Path("data/cleaned/discharge_cycles.parquet")
OUTPUT_DIR = Path("data/analytics")
OUTPUT_PATH = OUTPUT_DIR / "degradation_summary.parquet"


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    discharge_cycles = pd.read_parquet(INPUT_PATH)

    degradation = build_degradation_summary(
        discharge_cycles
    )

    degradation.to_parquet(
        OUTPUT_PATH,
        index=False,
    )

    print(f"Wrote: {OUTPUT_PATH}")
    print()
    print(degradation)


if __name__ == "__main__":
    main()