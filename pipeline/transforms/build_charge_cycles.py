import pandas as pd


def build_charge_cycles(cycle_summary: pd.DataFrame) -> pd.DataFrame:
    charge = cycle_summary[
        cycle_summary["operation_type"] == "charge"
    ].copy()

    charge = charge.sort_values(
        by=["battery_id", "cycle_index"]
    ).reset_index(drop=True)

    charge["charge_cycle_number"] = (
        charge.groupby("battery_id").cumcount() + 1
    )

    output_columns = [
        "battery_id",
        "charge_cycle_number",
        "cycle_index",
        "start_time",
        "ambient_temperature",
        "duration_seconds",
        "sample_count",
        "avg_voltage",
        "start_voltage",
        "end_voltage",
        "avg_current",
        "avg_temperature",
        "max_temperature",
        "temperature_delta_to_ambient",
        "is_valid",
    ]

    return charge[output_columns]
