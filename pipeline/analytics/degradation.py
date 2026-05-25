from typing import Any

import pandas as pd


def build_degradation_summary(
    discharge_cycles: pd.DataFrame,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    for battery_id, group in discharge_cycles.groupby("battery_id"):
        group = group.sort_values("discharge_cycle_number")

        first_capacity = float(group["capacity_ah"].iloc[0])
        final_capacity = float(group["capacity_ah"].iloc[-1])

        absolute_capacity_change_ah = final_capacity - first_capacity
        relative_capacity_change_percent = (
            absolute_capacity_change_ah / first_capacity
        ) * 100.0

        absolute_capacity_drop_ah = first_capacity - final_capacity
        relative_capacity_drop_percent = (
            absolute_capacity_drop_ah / first_capacity
        ) * 100.0

        early = group[group["life_stage"] == "early"]
        late = group[group["life_stage"] == "late"]

        early_avg_capacity = (
            float(early["capacity_ah"].mean())
            if not early.empty
            else None
        )

        late_avg_capacity = (
            float(late["capacity_ah"].mean())
            if not late.empty
            else None
        )

        early_to_late_capacity_change_ah = None
        early_to_late_capacity_change_percent = None

        if early_avg_capacity is not None and late_avg_capacity is not None:
            early_to_late_capacity_change_ah = (
                late_avg_capacity - early_avg_capacity
            )

            early_to_late_capacity_change_percent = (
                early_to_late_capacity_change_ah
                / early_avg_capacity
            ) * 100.0

        avg_drop_per_cycle_ah = (
            absolute_capacity_drop_ah / len(group)
            if len(group) > 0
            else None
        )

        rows.append(
            {
                "battery_id": battery_id,
                "initial_capacity_ah": first_capacity,
                "final_capacity_ah": final_capacity,
                "absolute_capacity_change_ah": absolute_capacity_change_ah,
                "relative_capacity_change_percent": relative_capacity_change_percent,
                "absolute_capacity_drop_ah": absolute_capacity_drop_ah,
                "relative_capacity_drop_percent": relative_capacity_drop_percent,
                "avg_drop_per_cycle_ah": avg_drop_per_cycle_ah,
                "early_avg_capacity_ah": early_avg_capacity,
                "late_avg_capacity_ah": late_avg_capacity,
                "early_to_late_capacity_change_ah": early_to_late_capacity_change_ah,
                "early_to_late_capacity_change_percent": early_to_late_capacity_change_percent,
            }
        )

    return pd.DataFrame(rows)