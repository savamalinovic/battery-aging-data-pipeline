from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data"

CLEANED_DIR = DATA_DIR / "cleaned"
ANALYTICS_DIR = DATA_DIR / "analytics"
QUALITY_DIR = DATA_DIR / "quality"
DASHBOARD_DIR = DATA_DIR / "dashboard"


FILES = {
    "cycle_summary": CLEANED_DIR / "cycle_summary.parquet",
    "discharge_cycles": CLEANED_DIR / "discharge_cycles.parquet",
    "battery_health_summary": ANALYTICS_DIR / "battery_health_summary.parquet",
    "degradation_summary": ANALYTICS_DIR / "degradation_summary.parquet",
    "rolling_degradation_summary": ANALYTICS_DIR / "rolling_degradation_summary.parquet",
    "soh_eol_summary": ANALYTICS_DIR / "soh_eol_summary.parquet",
    "life_stage_summary": ANALYTICS_DIR / "life_stage_summary.parquet",
    "temperature_summary": ANALYTICS_DIR / "temperature_summary.parquet",
    "voltage_summary": ANALYTICS_DIR / "voltage_summary.parquet",
    "discharge_duration_summary": ANALYTICS_DIR / "discharge_duration_summary.parquet",
    "correlation_summary": ANALYTICS_DIR / "correlation_summary.parquet",
    "data_quality_summary": ANALYTICS_DIR / "data_quality_summary.parquet",
    "invalid_cycles": QUALITY_DIR / "invalid_cycles.parquet",
    "dashboard_manifest": DASHBOARD_DIR / "dashboard_manifest.parquet",
    "discharge_cycles_health": CLEANED_DIR / "discharge_cycles_health.parquet",
    "health_quality_summary": QUALITY_DIR / "health_quality_summary.parquet",
}