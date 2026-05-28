from typing import Any

import pandas as pd


def build_data_quality_summary(
    cycle_summary: pd.DataFrame,
    invalid_cycles: pd.DataFrame,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    for battery_id, group in cycle_summary.groupby("battery_id"):
        total_cycles = int(len(group))
        valid_cycles = int(group["is_valid"].sum())
        invalid_cycles_count = total_cycles - valid_cycles

        quality_score_percent = (
            valid_cycles / total_cycles
        ) * 100.0 if total_cycles > 0 else None

        battery_invalid = invalid_cycles[
            invalid_cycles["battery_id"] == battery_id
        ]

        invalid_discharge_cycles = int(
            battery_invalid[
                battery_invalid["operation_type"] == "discharge"
            ]["cycle_index"].nunique()
        ) if not battery_invalid.empty else 0

        invalid_impedance_cycles = int(
            battery_invalid[
                battery_invalid["operation_type"] == "impedance"
            ]["cycle_index"].nunique()
        ) if not battery_invalid.empty else 0

        if battery_invalid.empty:
            top_error_code = None
        else:
            top_error_code = (
                battery_invalid["error_code"]
                .value_counts()
                .idxmax()
            )

        usable_for_health_analytics = (
            group[
                (group["operation_type"] == "discharge")
                & (group["is_valid"])
                & (group["capacity_ah"].notna())
            ].shape[0]
            > 0
        )

        rows.append(
            {
                "battery_id": battery_id,
                "total_cycles": total_cycles,
                "valid_cycles": valid_cycles,
                "invalid_cycles": invalid_cycles_count,
                "quality_score_percent": quality_score_percent,
                "invalid_discharge_cycles": invalid_discharge_cycles,
                "invalid_impedance_cycles": invalid_impedance_cycles,
                "top_error_code": top_error_code,
                "usable_for_health_analytics": usable_for_health_analytics,
            }
        )

    return pd.DataFrame(rows)