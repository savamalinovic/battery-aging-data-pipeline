from pathlib import Path

import pandas as pd

from pipeline.analytics.discharge_duration import (
    build_discharge_duration_summary,
)


INPUT_PATH = Path("data/cleaned/discharge_cycles.parquet")
OUTPUT_DIR = Path("data/analytics")
OUTPUT_PATH = OUTPUT_DIR / "discharge_duration_summary.parquet"


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    discharge_cycles = pd.read_parquet(INPUT_PATH)

    summary = build_discharge_duration_summary(discharge_cycles)

    summary.to_parquet(OUTPUT_PATH, index=False)

    print(f"Wrote: {OUTPUT_PATH}")
    print()
    print(summary)


if __name__ == "__main__":
    main()