import pandas as pd

from pipeline.reference_capacity import get_reference_capacity_ah


def classify_life_stage(soh: float | None) -> str | None:
    if soh is None:
        return None

    if soh >= 0.90:
        return "early"

    if soh >= 0.80:
        return "middle"

    return "late"


def build_discharge_cycles(cycle_summary: pd.DataFrame) -> pd.DataFrame:
    discharge = cycle_summary[
        cycle_summary["operation_type"] == "discharge"
    ].copy()

    discharge = discharge.sort_values(
        by=["battery_id", "cycle_index"]
    ).reset_index(drop=True)

    discharge["discharge_cycle_number"] = (
        discharge.groupby("battery_id").cumcount() + 1
    )

    discharge["initial_capacity_ah"] = (
        discharge.groupby("battery_id")["capacity_ah"].transform("first")
    )

    discharge["previous_capacity_ah"] = (
        discharge.groupby("battery_id")["capacity_ah"].shift(1)
    )

    discharge["reference_capacity_ah"] = discharge["battery_id"].map(
        get_reference_capacity_ah
    )

    # Primary SOH uses the configured reference capacity for the battery.
    discharge["soh"] = (
        discharge["capacity_ah"] / discharge["reference_capacity_ah"]
    )

    # Keep the first-discharge-relative baseline separately for debugging.
    discharge["soh_relative_to_initial"] = (
        discharge["capacity_ah"] / discharge["initial_capacity_ah"]
    )

    discharge["eol_flag"] = discharge["soh"] <= 0.70

    # Signed change from initial capacity.
    # Positive = capacity is above initial.
    # Negative = capacity is below initial.
    discharge["capacity_change_from_initial_ah"] = (
        discharge["capacity_ah"] - discharge["initial_capacity_ah"]
    )

    discharge["capacity_change_from_initial_percent"] = (
        discharge["capacity_change_from_initial_ah"]
        / discharge["initial_capacity_ah"]
    ) * 100.0

    # Keep fade columns with the same signed convention.
    # Positive = recovery/increase.
    # Negative = degradation/drop.
    discharge["capacity_fade_from_initial_ah"] = (
        discharge["capacity_change_from_initial_ah"]
    )

    discharge["capacity_fade_from_initial_percent"] = (
        discharge["capacity_change_from_initial_percent"]
    )

    # Signed change from previous discharge cycle.
    # Positive = capacity increased compared to previous cycle.
    # Negative = capacity dropped compared to previous cycle.
    discharge["capacity_change_from_previous_ah"] = (
        discharge["capacity_ah"] - discharge["previous_capacity_ah"]
    )

    discharge["capacity_change_from_previous_percent"] = (
        discharge["capacity_change_from_previous_ah"]
        / discharge["previous_capacity_ah"]
    ) * 100.0

    # Same signed convention for fade columns.
    discharge["capacity_fade_from_previous_ah"] = (
        discharge["capacity_change_from_previous_ah"]
    )

    discharge["capacity_fade_from_previous_percent"] = (
        discharge["capacity_change_from_previous_percent"]
    )

    # Backward-compatible aliases.
    # These now also use signed convention:
    # positive = recovery, negative = drop.
    discharge["capacity_fade_ah"] = discharge[
        "capacity_fade_from_initial_ah"
    ]

    discharge["capacity_fade_percent"] = discharge[
        "capacity_fade_from_initial_percent"
    ]

    discharge["life_stage"] = discharge["soh"].apply(classify_life_stage)

    discharge["rul_cycles_actual"] = None

    output_columns = [
        "battery_id",
        "discharge_cycle_number",
        "cycle_index",
        "start_time",
        "capacity_ah",
        "reference_capacity_ah",
        "initial_capacity_ah",
        "previous_capacity_ah",
        "soh",
        "soh_relative_to_initial",
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
    ]

    return discharge[output_columns]
