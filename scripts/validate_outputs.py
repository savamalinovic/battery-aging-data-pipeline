from pathlib import Path

import pandas as pd


REQUIRED_OUTPUTS: dict[str, list[str]] = {
    "data/cleaned/cycle_summary.parquet": [
        "battery_id",
        "cycle_index",
        "operation_type",
        "start_time",
        "ambient_temperature",
        "duration_seconds",
        "sample_count",
        "capacity_ah",
        "soh",
        "eol_flag",
        "avg_voltage",
        "start_voltage",
        "end_voltage",
        "voltage_drop",
        "avg_current",
        "avg_temperature",
        "max_temperature",
        "temperature_delta_to_ambient",
        "is_valid",
    ],
    "data/cleaned/discharge_cycles.parquet": [
        "battery_id",
        "discharge_cycle_number",
        "cycle_index",
        "start_time",
        "capacity_ah",
        "initial_capacity_ah",
        "previous_capacity_ah",
        "soh",
        "eol_flag",
        "capacity_change_from_initial_ah",
        "capacity_change_from_initial_percent",
        "capacity_fade_from_initial_ah",
        "capacity_fade_from_initial_percent",
        "capacity_change_from_previous_ah",
        "capacity_change_from_previous_percent",
        "capacity_fade_from_previous_ah",
        "capacity_fade_from_previous_percent",
        "capacity_fade_ah",
        "capacity_fade_percent",
        "duration_seconds",
        "start_voltage",
        "end_voltage",
        "voltage_drop",
        "avg_voltage",
        "avg_current",
        "avg_temperature",
        "max_temperature",
        "temperature_delta_to_ambient",
        "life_stage",
        "rul_cycles_actual",
        "is_valid",
    ],
    "data/quality/invalid_cycles.parquet": [
        "battery_id",
        "cycle_index",
        "operation_type",
        "error_code",
        "error_description",
        "severity",
        "excluded_from_analytics",
    ],
    "data/analytics/battery_health_summary.parquet": [
        "battery_id",
        "first_capacity_ah",
        "final_capacity_ah",
        "capacity_loss_ah",
        "capacity_loss_percent",
        "initial_soh",
        "final_soh",
        "total_discharge_cycles",
        "cycle_below_80_soh",
        "eol_cycle",
        "reached_eol",
        "avg_degradation_rate_per_cycle",
        "avg_discharge_duration_seconds",
        "duration_loss_percent",
        "health_rank",
    ],
    "data/analytics/degradation_summary.parquet": [
        "battery_id",
        "initial_capacity_ah",
        "final_capacity_ah",
        "absolute_capacity_change_ah",
        "relative_capacity_change_percent",
        "absolute_capacity_drop_ah",
        "relative_capacity_drop_percent",
        "avg_drop_per_cycle_ah",
        "early_avg_capacity_ah",
        "late_avg_capacity_ah",
        "early_to_late_capacity_change_ah",
        "early_to_late_capacity_change_percent",
    ],
    "data/analytics/rolling_degradation_summary.parquet": [
        "battery_id",
        "discharge_cycle_number",
        "capacity_ah",
        "soh",
        "rolling_capacity_5",
        "rolling_soh_5",
        "capacity_fade_from_previous_percent",
        "capacity_fade_from_initial_percent",
        "degradation_acceleration_percent",
        "absolute_capacity_drop_percent",
        "avg_temperature",
        "temperature_delta_to_ambient",
        "duration_seconds",
        "life_stage",
        "eol_flag",
    ],
    "data/analytics/soh_eol_summary.parquet": [
        "battery_id",
        "initial_soh_percent",
        "final_soh_percent",
        "min_soh_percent",
        "avg_soh_percent",
        "cycle_below_80_soh",
        "eol_cycle",
        "capacity_at_eol_ah",
        "soh_at_eol_percent",
        "rul_available",
    ],
    "data/analytics/life_stage_summary.parquet": [
        "battery_id",
        "life_stage",
        "cycle_count",
        "avg_capacity_ah",
        "avg_soh_percent",
        "avg_duration_seconds",
        "avg_voltage_drop",
        "avg_temperature",
        "avg_temperature_delta_to_ambient",
        "avg_re_ohm",
        "avg_rct_ohm",
    ],
    "data/analytics/temperature_summary.parquet": [
        "battery_id",
        "life_stage",
        "avg_working_temperature",
        "max_working_temperature",
        "avg_temperature_delta_to_ambient",
        "temperature_change_within_stage",
        "delta_to_ambient_change_within_stage",
    ],
    "data/analytics/voltage_summary.parquet": [
        "battery_id",
        "life_stage",
        "avg_start_voltage",
        "avg_end_voltage",
        "avg_voltage",
        "avg_voltage_drop",
        "voltage_drop_change_within_stage",
        "correlation_voltage_drop_capacity",
        "correlation_voltage_drop_soh",
    ],
    "data/analytics/discharge_duration_summary.parquet": [
        "battery_id",
        "initial_duration_seconds",
        "final_duration_seconds",
        "avg_duration_seconds",
        "duration_loss_seconds",
        "duration_loss_percent",
        "corr_duration_capacity",
        "corr_duration_soh",
    ],
    "data/analytics/correlation_summary.parquet": [
        "scope",
        "battery_id",
        "x_metric",
        "y_metric",
        "correlation_method",
        "correlation_value",
        "sample_count",
        "interpretation",
    ],
    "data/analytics/data_quality_summary.parquet": [
        "battery_id",
        "total_cycles",
        "valid_cycles",
        "invalid_cycles",
        "quality_score_percent",
        "invalid_discharge_cycles",
        "invalid_impedance_cycles",
        "top_error_code",
        "usable_for_health_analytics",
    ],
    "data/dashboard/dashboard_manifest.parquet": [
        "dataset_name",
        "file_path",
        "required_for_mvp",
        "dashboard_section",
        "grain",
        "description",
    ],
}


def validate_file(path: str, required_columns: list[str]) -> list[str]:
    errors: list[str] = []

    file_path = Path(path)

    if not file_path.exists():
        return [f"Missing file: {path}"]

    try:
        df = pd.read_parquet(file_path)
    except Exception as exc:
        return [f"Could not read {path}: {exc}"]

    missing_columns = [
        column for column in required_columns if column not in df.columns
    ]

    if missing_columns:
        errors.append(
            f"{path}: missing columns: {missing_columns}"
        )

    if df.empty and path != "data/quality/invalid_cycles.parquet":
        errors.append(f"{path}: file is empty")

    print(f"OK: {path} shape={df.shape}")

    return errors


def main() -> None:
    print("Validating pipeline outputs...")
    print("=" * 80)

    all_errors: list[str] = []

    for path, required_columns in REQUIRED_OUTPUTS.items():
        errors = validate_file(path, required_columns)
        all_errors.extend(errors)

    print("=" * 80)

    if all_errors:
        print("Validation failed:")
        for error in all_errors:
            print(f"- {error}")

        raise SystemExit(1)

    print("All required outputs are valid.")


if __name__ == "__main__":
    main()