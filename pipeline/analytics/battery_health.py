from typing import Any

import pandas as pd


def first_cycle_where(
    group: pd.DataFrame,
    condition_column: str,
) -> int | None:
    matched = group[group[condition_column]]

    if matched.empty:
        return None

    return int(matched["discharge_cycle_number"].min())


def compute_duration_loss_percent(group: pd.DataFrame) -> float | None:
    early = group[group["life_stage"] == "early"]
    late = group[group["life_stage"] == "late"]

    if early.empty or late.empty:
        return None

    early_avg = early["duration_seconds"].mean()
    late_avg = late["duration_seconds"].mean()

    if early_avg == 0:
        return None

    return float(((early_avg - late_avg) / early_avg) * 100.0)


def build_battery_health_summary(
    discharge_cycles: pd.DataFrame,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    for battery_id, group in discharge_cycles.groupby("battery_id"):
        group = group.sort_values("discharge_cycle_number")

        first_capacity = float(group["capacity_ah"].iloc[0])
        final_capacity = float(group["capacity_ah"].iloc[-1])

        capacity_loss_ah = first_capacity - final_capacity
        capacity_loss_percent = (
            capacity_loss_ah / first_capacity
        ) * 100.0

        initial_soh = float(group["soh"].iloc[0])
        final_soh = float(group["soh"].iloc[-1])

        below_80 = group[group["soh"] <= 0.80]
        eol = group[group["soh"] <= 0.70]

        cycle_below_80_soh = (
            int(below_80["discharge_cycle_number"].min())
            if not below_80.empty
            else None
        )

        eol_cycle = (
            int(eol["discharge_cycle_number"].min())
            if not eol.empty
            else None
        )

        total_discharge_cycles = int(len(group))

        avg_degradation_rate_per_cycle = (
            capacity_loss_ah / total_discharge_cycles
            if total_discharge_cycles > 0
            else None
        )

        row = {
            "battery_id": battery_id,
            "first_capacity_ah": first_capacity,
            "final_capacity_ah": final_capacity,
            "capacity_loss_ah": capacity_loss_ah,
            "capacity_loss_percent": capacity_loss_percent,
            "initial_soh": initial_soh,
            "final_soh": final_soh,
            "total_discharge_cycles": total_discharge_cycles,
            "cycle_below_80_soh": cycle_below_80_soh,
            "eol_cycle": eol_cycle,
            "reached_eol": eol_cycle is not None,
            "avg_degradation_rate_per_cycle": avg_degradation_rate_per_cycle,
            "avg_discharge_duration_seconds": float(
                group["duration_seconds"].mean()
            ),
            "duration_loss_percent": compute_duration_loss_percent(group),
        }

        rows.append(row)

    summary = pd.DataFrame(rows)

    summary = summary.sort_values(
        by=[
            "final_soh",
            "capacity_loss_percent",
        ],
        ascending=[False, True],
    ).reset_index(drop=True)

    summary["health_rank"] = range(1, len(summary) + 1)

    return summary