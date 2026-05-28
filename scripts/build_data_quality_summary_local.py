from pathlib import Path

import pandas as pd

from pipeline.analytics.data_quality import build_data_quality_summary


CYCLE_SUMMARY_PATH = Path("data/cleaned/cycle_summary.parquet")
INVALID_CYCLES_PATH = Path("data/quality/invalid_cycles.parquet")

OUTPUT_DIR = Path("data/analytics")
OUTPUT_PATH = OUTPUT_DIR / "data_quality_summary.parquet"


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    cycle_summary = pd.read_parquet(CYCLE_SUMMARY_PATH)
    invalid_cycles = pd.read_parquet(INVALID_CYCLES_PATH)

    summary = build_data_quality_summary(
        cycle_summary=cycle_summary,
        invalid_cycles=invalid_cycles,
    )

    summary.to_parquet(OUTPUT_PATH, index=False)

    print(f"Wrote: {OUTPUT_PATH}")
    print()
    print(summary)


if __name__ == "__main__":
    main()