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


def calculate_start_minus_end(
    start_value: float | None,
    end_value: float | None,
) -> float | None:
    if start_value is None or end_value is None:
        return None

    return start_value - end_value


def safe_correlation(
    group: pd.DataFrame,
    x_column: str,
    y_column: str,
) -> float | None:
    clean = group[[x_column, y_column]].dropna()

    if len(clean) < 2:
        return None

    if clean[x_column].nunique() < 2 or clean[y_column].nunique() < 2:
        return None

    return float(clean[x_column].corr(clean[y_column]))


def build_voltage_summary(
    discharge_cycles: pd.DataFrame,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    for battery_id, battery_group in discharge_cycles.groupby("battery_id"):
        battery_group = battery_group.sort_values("discharge_cycle_number")

        stage_groups = {
            "early": battery_group[battery_group["life_stage"] == "early"],
            "middle": battery_group[battery_group["life_stage"] == "middle"],
            "late": battery_group[battery_group["life_stage"] == "late"],
        }

        for life_stage, stage_group in stage_groups.items():
            if stage_group.empty:
                continue

            first_voltage_drop = get_first_value(
                stage_group,
                "voltage_drop",
            )
            last_voltage_drop = get_last_value(
                stage_group,
                "voltage_drop",
            )

            rows.append(
                {
                    "battery_id": battery_id,
                    "life_stage": life_stage,
                    "avg_start_voltage": float(
                        stage_group["start_voltage"].mean()
                    ),
                    "avg_end_voltage": float(
                        stage_group["end_voltage"].mean()
                    ),
                    "avg_voltage": float(
                        stage_group["avg_voltage"].mean()
                    ),
                    "avg_voltage_drop": float(
                        stage_group["voltage_drop"].mean()
                    ),
                    "voltage_drop_change_within_stage": calculate_start_minus_end(
                        first_voltage_drop,
                        last_voltage_drop,
                    ),
                    "correlation_voltage_drop_capacity": safe_correlation(
                        stage_group,
                        "voltage_drop",
                        "capacity_ah",
                    ),
                    "correlation_voltage_drop_soh": safe_correlation(
                        stage_group,
                        "voltage_drop",
                        "soh",
                    ),
                }
            )

        first_voltage_drop = get_first_value(
            battery_group,
            "voltage_drop",
        )
        final_voltage_drop = get_last_value(
            battery_group,
            "voltage_drop",
        )

        rows.append(
            {
                "battery_id": battery_id,
                "life_stage": "all",
                "avg_start_voltage": float(
                    battery_group["start_voltage"].mean()
                ),
                "avg_end_voltage": float(
                    battery_group["end_voltage"].mean()
                ),
                "avg_voltage": float(
                    battery_group["avg_voltage"].mean()
                ),
                "avg_voltage_drop": float(
                    battery_group["voltage_drop"].mean()
                ),
                "voltage_drop_change_within_stage": calculate_start_minus_end(
                    first_voltage_drop,
                    final_voltage_drop,
                ),
                "correlation_voltage_drop_capacity": safe_correlation(
                    battery_group,
                    "voltage_drop",
                    "capacity_ah",
                ),
                "correlation_voltage_drop_soh": safe_correlation(
                    battery_group,
                    "voltage_drop",
                    "soh",
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