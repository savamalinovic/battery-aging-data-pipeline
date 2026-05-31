from pathlib import Path

import pandas as pd

from pipeline.analytics.battery_health import build_battery_health_summary
from pipeline.analytics.correlations import build_correlation_summary
from pipeline.analytics.dashboard_manifest import build_dashboard_manifest
from pipeline.analytics.data_quality import build_data_quality_summary
from pipeline.analytics.degradation import build_degradation_summary
from pipeline.analytics.discharge_duration import build_discharge_duration_summary
from pipeline.analytics.life_stage import build_life_stage_summary
from pipeline.analytics.rolling_degradation import build_rolling_degradation_summary
from pipeline.analytics.soh_eol import build_soh_eol_summary
from pipeline.analytics.temperature import build_temperature_summary
from pipeline.analytics.voltage import build_voltage_summary
from pipeline.raw.mat_loader import load_battery_mat
from pipeline.transforms.build_charge_cycles import build_charge_cycles
from pipeline.transforms.build_cycle_summary import build_cycle_summary_for_battery
from pipeline.transforms.build_discharge_cycles import build_discharge_cycles
from pipeline.transforms.build_measurement_readings import (
    build_measurement_readings_for_battery,
)
from pipeline.transforms.build_discharge_cycles_health import (
    build_discharge_cycles_health,
)


RAW_DIR = Path("data/raw")
CLEANED_DIR = Path("data/cleaned")
ANALYTICS_DIR = Path("data/analytics")
QUALITY_DIR = Path("data/quality")
DASHBOARD_DIR = Path("data/dashboard")


def ensure_output_directories() -> None:
    CLEANED_DIR.mkdir(parents=True, exist_ok=True)
    ANALYTICS_DIR.mkdir(parents=True, exist_ok=True)
    QUALITY_DIR.mkdir(parents=True, exist_ok=True)
    DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)


def build_cycle_summary_outputs() -> tuple[pd.DataFrame, pd.DataFrame]:
    all_cycle_summary_frames: list[pd.DataFrame] = []
    all_invalid_cycle_frames: list[pd.DataFrame] = []
    all_measurement_readings_frames: list[pd.DataFrame] = []

    mat_files = sorted(RAW_DIR.glob("*.mat"))

    if not mat_files:
        raise FileNotFoundError(f"No .mat files found in {RAW_DIR}")

    for file_path in mat_files:
        loaded = load_battery_mat(file_path)

        cycle_summary, invalid_cycles = build_cycle_summary_for_battery(
            battery_id=loaded["battery_id"],
            cycles=loaded["cycles"],
        )
        measurement_readings = build_measurement_readings_for_battery(
            battery_id=loaded["battery_id"],
            cycles=loaded["cycles"],
        )

        all_cycle_summary_frames.append(cycle_summary)
        all_measurement_readings_frames.append(measurement_readings)

        if not invalid_cycles.empty:
            all_invalid_cycle_frames.append(invalid_cycles)

        print(
            f"{loaded['battery_id']}: "
            f"cycle_summary_rows={len(cycle_summary)}, "
            f"measurement_rows={len(measurement_readings)}, "
            f"invalid_rows={len(invalid_cycles)}"
        )

    cycle_summary = pd.concat(
        all_cycle_summary_frames,
        ignore_index=True,
    )

    if all_invalid_cycle_frames:
        invalid_cycles = pd.concat(
            all_invalid_cycle_frames,
            ignore_index=True,
        )
    else:
        invalid_cycles = pd.DataFrame(
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

    cycle_summary.to_parquet(
        CLEANED_DIR / "cycle_summary.parquet",
        index=False,
    )
    cycle_summary.to_parquet(
        CLEANED_DIR / "cycle_metadata.parquet",
        index=False,
    )

    measurement_readings = pd.concat(
        all_measurement_readings_frames,
        ignore_index=True,
    )
    measurement_readings.to_parquet(
        CLEANED_DIR / "measurement_readings.parquet",
        index=False,
    )

    invalid_cycles.to_parquet(
        QUALITY_DIR / "invalid_cycles.parquet",
        index=False,
    )

    return cycle_summary, invalid_cycles


def build_cleaned_outputs(
    cycle_summary: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    discharge_cycles = build_discharge_cycles(cycle_summary)

    discharge_cycles.to_parquet(
        CLEANED_DIR / "discharge_cycles.parquet",
        index=False,
    )

    discharge_cycles_health, health_quality_summary = (
        build_discharge_cycles_health(discharge_cycles)
    )

    discharge_cycles_health.to_parquet(
        CLEANED_DIR / "discharge_cycles_health.parquet",
        index=False,
    )

    health_quality_summary.to_parquet(
        QUALITY_DIR / "health_quality_summary.parquet",
        index=False,
    )

    return discharge_cycles, discharge_cycles_health, health_quality_summary


def build_analytics_outputs(
    cycle_summary: pd.DataFrame,
    discharge_cycles: pd.DataFrame,
    invalid_cycles: pd.DataFrame,
) -> None:
    battery_health_summary = build_battery_health_summary(discharge_cycles)
    battery_health_summary.to_parquet(
        ANALYTICS_DIR / "battery_health_summary.parquet",
        index=False,
    )

    degradation_summary = build_degradation_summary(discharge_cycles)
    degradation_summary.to_parquet(
        ANALYTICS_DIR / "degradation_summary.parquet",
        index=False,
    )

    rolling_degradation_summary = build_rolling_degradation_summary(
        discharge_cycles
    )
    rolling_degradation_summary.to_parquet(
        ANALYTICS_DIR / "rolling_degradation_summary.parquet",
        index=False,
    )

    soh_eol_summary = build_soh_eol_summary(discharge_cycles)
    soh_eol_summary.to_parquet(
        ANALYTICS_DIR / "soh_eol_summary.parquet",
        index=False,
    )

    life_stage_summary = build_life_stage_summary(discharge_cycles)
    life_stage_summary.to_parquet(
        ANALYTICS_DIR / "life_stage_summary.parquet",
        index=False,
    )

    temperature_summary = build_temperature_summary(discharge_cycles)
    temperature_summary.to_parquet(
        ANALYTICS_DIR / "temperature_summary.parquet",
        index=False,
    )

    voltage_summary = build_voltage_summary(discharge_cycles)
    voltage_summary.to_parquet(
        ANALYTICS_DIR / "voltage_summary.parquet",
        index=False,
    )

    discharge_duration_summary = build_discharge_duration_summary(
        discharge_cycles
    )
    discharge_duration_summary.to_parquet(
        ANALYTICS_DIR / "discharge_duration_summary.parquet",
        index=False,
    )

    correlation_summary = build_correlation_summary(discharge_cycles)
    correlation_summary.to_parquet(
        ANALYTICS_DIR / "correlation_summary.parquet",
        index=False,
    )

    data_quality_summary = build_data_quality_summary(
        cycle_summary=cycle_summary,
        invalid_cycles=invalid_cycles,
    )
    data_quality_summary.to_parquet(
        ANALYTICS_DIR / "data_quality_summary.parquet",
        index=False,
    )


def build_dashboard_outputs() -> None:
    dashboard_manifest = build_dashboard_manifest()

    dashboard_manifest.to_parquet(
        DASHBOARD_DIR / "dashboard_manifest.parquet",
        index=False,
    )


def main() -> None:
    print("Starting NASA Battery Pipeline")
    print("=" * 80)

    ensure_output_directories()

    print("Building cycle summary outputs...")
    cycle_summary, invalid_cycles = build_cycle_summary_outputs()

    print("Building cleaned cycle outputs...")
    discharge_cycles, discharge_cycles_health, health_quality_summary = (
    build_cleaned_outputs(cycle_summary)
    )

    print("Building analytics outputs...")
    build_analytics_outputs(
        cycle_summary=cycle_summary,
        discharge_cycles=discharge_cycles_health,
        invalid_cycles=invalid_cycles,
    )

    print("Building dashboard outputs...")
    build_dashboard_outputs()

    print("=" * 80)
    print("Pipeline completed successfully.")
    print()
    print(f"cycle_summary rows: {len(cycle_summary)}")
    print(f"discharge_cycles rows: {len(discharge_cycles)}")
    print(f"discharge_cycles_health rows: {len(discharge_cycles_health)}")
    print(f"health_quality_summary rows: {len(health_quality_summary)}")
    print(f"invalid_cycles rows: {len(invalid_cycles)}")


if __name__ == "__main__":
    main()
