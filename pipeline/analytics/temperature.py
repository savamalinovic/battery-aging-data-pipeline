from typing import Any

import pandas as pd


def get_first_value(group: pd.DataFrame, column: str) -> float | None:
    if group.empty:
        return None

    group = group.sort_values("discharge_cycle_number")

    return float(group[column].iloc[0])


def get_last_value(group: pd.DataFrame, column: str) -> float | None:
    if group.empty:
        return None

    group = group.sort_values("discharge_cycle_number")

    return float(group[column].iloc[-1])


def calculate_end_minus_start(
    start_value: float | None,
    end_value: float | None,
) -> float | None:
    if start_value is None or end_value is None:
        return None

    return end_value - start_value


def build_temperature_summary(
    discharge_cycles: pd.DataFrame,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    for battery_id, battery_group in discharge_cycles.groupby("battery_id"):
        battery_group = battery_group.sort_values("discharge_cycle_number")

        early = battery_group[battery_group["life_stage"] == "early"]
        middle = battery_group[battery_group["life_stage"] == "middle"]
        late = battery_group[battery_group["life_stage"] == "late"]

        stage_groups = {
            "early": early,
            "middle": middle,
            "late": late,
        }

        for life_stage, stage_group in stage_groups.items():
            if stage_group.empty:
                continue

            stage_start_temperature = get_first_value(
                stage_group,
                "avg_temperature",
            )
            stage_end_temperature = get_last_value(
                stage_group,
                "avg_temperature",
            )

            stage_start_delta = get_first_value(
                stage_group,
                "temperature_delta_to_ambient",
            )
            stage_end_delta = get_last_value(
                stage_group,
                "temperature_delta_to_ambient",
            )

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
                    "temperature_change_within_stage": calculate_end_minus_start(
                        stage_start_temperature,
                        stage_end_temperature,
                    ),
                    "delta_to_ambient_change_within_stage": calculate_end_minus_start(
                        stage_start_delta,
                        stage_end_delta,
                    ),
                }
            )

        early_start_temperature = get_first_value(
            early,
            "avg_temperature",
        )
        late_end_temperature = get_last_value(
            late,
            "avg_temperature",
        )

        early_start_delta = get_first_value(
            early,
            "temperature_delta_to_ambient",
        )
        late_end_delta = get_last_value(
            late,
            "temperature_delta_to_ambient",
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
                "temperature_change_within_stage": calculate_end_minus_start(
                    early_start_temperature,
                    late_end_temperature,
                ),
                "delta_to_ambient_change_within_stage": calculate_end_minus_start(
                    early_start_delta,
                    late_end_delta,
                ),
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