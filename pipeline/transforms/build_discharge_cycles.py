from typing import Any

import pandas as pd


def classify_life_stage(soh: float | None) -> str | None:
    if soh is None:
        return None

    if soh >= 0.90:
        return "early"

    if soh >= 0.80:
        return "middle"

    return "late"


def build_discharge_cycles(
    cycle_summary: pd.DataFrame,
) -> pd.DataFrame:
    discharge = cycle_summary[
        cycle_summary["operation_type"] == "discharge"
    ].copy()

    discharge = discharge.sort_values(
        by=["battery_id", "cycle_index"]
    ).reset_index(drop=True)

    discharge["discharge_cycle_number"] = (
        discharge.groupby("battery_id")
        .cumcount()
        + 1
    )

    discharge["initial_capacity_ah"] = (
        discharge.groupby("battery_id")["capacity_ah"]
        .transform("first")
    )

    discharge["capacity_fade_ah"] = (
        discharge["initial_capacity_ah"]
        - discharge["capacity_ah"]
    )

    discharge["capacity_fade_percent"] = (
        discharge["capacity_fade_ah"]
        / discharge["initial_capacity_ah"]
    ) * 100.0

    discharge["life_stage"] = discharge["soh"].apply(
        classify_life_stage
    )

    discharge["rul_cycles_actual"] = None

    output_columns = [
        "battery_id",
        "discharge_cycle_number",
        "cycle_index",
        "start_time",
        "capacity_ah",
        "soh",
        "eol_flag",
        "capacity_fade_ah",
        "capacity_fade_percent",
        "duration_seconds",
        "voltage_drop",
        "avg_voltage",
        "avg_current",
        "avg_temperature",
        "max_temperature",
        "temperature_delta_to_ambient",
        "life_stage",
        "rul_cycles_actual",
        "is_valid",
    ]

    return discharge[output_columns]