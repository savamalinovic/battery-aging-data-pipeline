from typing import Any

import pandas as pd


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


def build_discharge_duration_summary(
    discharge_cycles: pd.DataFrame,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    for battery_id, group in discharge_cycles.groupby("battery_id"):
        group = group.sort_values("discharge_cycle_number")

        early = group[group["life_stage"] == "early"]
        late = group[group["life_stage"] == "late"]

        if not early.empty:
            initial_duration_seconds = float(early["duration_seconds"].mean())
        else:
            initial_duration_seconds = float(group["duration_seconds"].iloc[0])

        if not late.empty:
            final_duration_seconds = float(late["duration_seconds"].mean())
        else:
            final_duration_seconds = float(group["duration_seconds"].iloc[-1])

        avg_duration_seconds = float(group["duration_seconds"].mean())

        duration_loss_seconds = (
            initial_duration_seconds - final_duration_seconds
        )

        duration_loss_percent = None
        if initial_duration_seconds != 0:
            duration_loss_percent = (
                duration_loss_seconds / initial_duration_seconds
            ) * 100.0

        rows.append(
            {
                "battery_id": battery_id,
                "initial_duration_seconds": initial_duration_seconds,
                "final_duration_seconds": final_duration_seconds,
                "avg_duration_seconds": avg_duration_seconds,
                "duration_loss_seconds": duration_loss_seconds,
                "duration_loss_percent": duration_loss_percent,
                "corr_duration_capacity": safe_correlation(
                    group,
                    "duration_seconds",
                    "capacity_ah",
                ),
                "corr_duration_soh": safe_correlation(
                    group,
                    "duration_seconds",
                    "soh",
                ),
            }
        )

    return pd.DataFrame(rows)