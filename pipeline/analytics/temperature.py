from typing import Any

import pandas as pd


def build_temperature_summary(
    discharge_cycles: pd.DataFrame,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    for battery_id, battery_group in discharge_cycles.groupby("battery_id"):
        early = battery_group[battery_group["life_stage"] == "early"]
        late = battery_group[battery_group["life_stage"] == "late"]

        early_avg_temperature = (
            float(early["avg_temperature"].mean())
            if not early.empty
            else None
        )

        late_avg_temperature = (
            float(late["avg_temperature"].mean())
            if not late.empty
            else None
        )

        early_avg_delta = (
            float(early["temperature_delta_to_ambient"].mean())
            if not early.empty
            else None
        )

        late_avg_delta = (
            float(late["temperature_delta_to_ambient"].mean())
            if not late.empty
            else None
        )

        late_vs_early_temperature_change = None
        if early_avg_temperature is not None and late_avg_temperature is not None:
            late_vs_early_temperature_change = (
                late_avg_temperature - early_avg_temperature
            )

        late_vs_early_delta_change = None
        if early_avg_delta is not None and late_avg_delta is not None:
            late_vs_early_delta_change = late_avg_delta - early_avg_delta

        for life_stage, stage_group in battery_group.groupby("life_stage"):
            rows.append(
                {
                    "battery_id": battery_id,
                    "life_stage": life_stage,
                    "avg_working_temperature": float(
                        stage_group["avg_temperature"].mean()
                    ),
                    "max_working_temperature": float(
                        stage_group["max_temperature"].max()
                    ),
                    "avg_temperature_delta_to_ambient": float(
                        stage_group["temperature_delta_to_ambient"].mean()
                    ),
                    "late_vs_early_temperature_change": late_vs_early_temperature_change,
                    "late_vs_early_delta_change": late_vs_early_delta_change,
                }
            )

        rows.append(
            {
                "battery_id": battery_id,
                "life_stage": "all",
                "avg_working_temperature": float(
                    battery_group["avg_temperature"].mean()
                ),
                "max_working_temperature": float(
                    battery_group["max_temperature"].max()
                ),
                "avg_temperature_delta_to_ambient": float(
                    battery_group["temperature_delta_to_ambient"].mean()
                ),
                "late_vs_early_temperature_change": late_vs_early_temperature_change,
                "late_vs_early_delta_change": late_vs_early_delta_change,
            }
        )

    summary = pd.DataFrame(rows)

    stage_order = {
        "early": 1,
        "middle": 2,
        "late": 3,
        "all": 4,
    }

    summary["life_stage_order"] = summary["life_stage"].map(stage_order)

    summary = summary.sort_values(
        by=["battery_id", "life_stage_order"]
    ).reset_index(drop=True)

    summary = summary.drop(columns=["life_stage_order"])

    return summary