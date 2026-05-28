from pathlib import Path

from pipeline.analytics.dashboard_manifest import build_dashboard_manifest


OUTPUT_DIR = Path("data/dashboard")
OUTPUT_PATH = OUTPUT_DIR / "dashboard_manifest.parquet"


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    manifest = build_dashboard_manifest()

    manifest.to_parquet(OUTPUT_PATH, index=False)

    print(f"Wrote: {OUTPUT_PATH}")
    print()
    print(manifest)


if __name__ == "__main__":
    main()