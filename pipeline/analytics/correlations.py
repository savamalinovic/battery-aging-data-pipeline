from typing import Any

import pandas as pd


CORRELATION_PAIRS = [
    ("avg_temperature", "capacity_ah"),
    ("avg_temperature", "soh"),
    ("avg_temperature", "capacity_fade_from_initial_percent"),
    ("temperature_delta_to_ambient", "capacity_ah"),
    ("temperature_delta_to_ambient", "soh"),
    ("temperature_delta_to_ambient", "capacity_fade_from_initial_percent"),
    ("duration_seconds", "capacity_ah"),
    ("duration_seconds", "soh"),
    ("voltage_drop", "capacity_ah"),
    ("voltage_drop", "soh"),
]


def interpret_correlation(value: float | None) -> str:
    if value is None:
        return "not_enough_data"

    abs_value = abs(value)

    if abs_value >= 0.80:
        strength = "strong"
    elif abs_value >= 0.50:
        strength = "moderate"
    elif abs_value >= 0.30:
        strength = "weak"
    else:
        strength = "very_weak"

    direction = "positive" if value > 0 else "negative"

    return f"{strength}_{direction}"


def calculate_correlation(
    df: pd.DataFrame,
    x_metric: str,
    y_metric: str,
) -> tuple[float | None, int]:
    clean = df[[x_metric, y_metric]].dropna()

    sample_count = len(clean)

    if sample_count < 2:
        return None, sample_count

    if clean[x_metric].nunique() < 2 or clean[y_metric].nunique() < 2:
        return None, sample_count

    correlation_value = clean[x_metric].corr(clean[y_metric], method="pearson")

    return float(correlation_value), sample_count


def build_correlation_summary(
    discharge_cycles: pd.DataFrame,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    scopes: list[tuple[str, str, pd.DataFrame]] = []

    scopes.append(
        (
            "all_batteries",
            "all",
            discharge_cycles,
        )
    )

    for battery_id, battery_group in discharge_cycles.groupby("battery_id"):
        scopes.append(
            (
                "battery",
                battery_id,
                battery_group,
            )
        )

    for scope, battery_id, scope_df in scopes:
        for x_metric, y_metric in CORRELATION_PAIRS:
            if x_metric not in scope_df.columns or y_metric not in scope_df.columns:
                continue

            correlation_value, sample_count = calculate_correlation(
                scope_df,
                x_metric,
                y_metric,
            )

            rows.append(
                {
                    "scope": scope,
                    "battery_id": battery_id,
                    "x_metric": x_metric,
                    "y_metric": y_metric,
                    "correlation_method": "pearson",
                    "correlation_value": correlation_value,
                    "sample_count": sample_count,
                    "interpretation": interpret_correlation(correlation_value),
                }
            )

    return pd.DataFrame(rows)