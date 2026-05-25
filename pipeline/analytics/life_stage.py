from typing import Any

import pandas as pd


def build_life_stage_summary(
    discharge_cycles: pd.DataFrame,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    grouped = discharge_cycles.groupby(["battery_id", "life_stage"])

    for (battery_id, life_stage), group in grouped:
        rows.append(
            {
                "battery_id": battery_id,
                "life_stage": life_stage,
                "cycle_count": int(len(group)),
                "avg_capacity_ah": float(group["capacity_ah"].mean()),
                "avg_soh_percent": float(group["soh"].mean() * 100.0),
                "avg_duration_seconds": float(group["duration_seconds"].mean()),
                "avg_voltage_drop": float(group["voltage_drop"].mean()),
                "avg_temperature": float(group["avg_temperature"].mean()),
                "avg_temperature_delta_to_ambient": float(
                    group["temperature_delta_to_ambient"].mean()
                ),
                "avg_re_ohm": None,
                "avg_rct_ohm": None,
            }
        )

    summary = pd.DataFrame(rows)

    stage_order = {
        "early": 1,
        "middle": 2,
        "late": 3,
    }

    summary["life_stage_order"] = summary["life_stage"].map(stage_order)

    summary = summary.sort_values(
        by=["battery_id", "life_stage_order"]
    ).reset_index(drop=True)

    summary = summary.drop(columns=["life_stage_order"])

    return summary