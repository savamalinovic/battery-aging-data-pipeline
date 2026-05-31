from typing import Any

import pandas as pd


MIN_CAPACITY_AH = 0.5
MAX_CAPACITY_AH = 2.2
MAX_ABS_CAPACITY_JUMP_AH = 0.5
MIN_PLAUSIBLE_DISCHARGE_CYCLES = 20
MAX_BAD_CYCLE_PERCENT = 20.0


def classify_life_stage(soh: float | None) -> str | None:
    if soh is None:
        return None

    if soh >= 0.90:
        return "early"

    if soh >= 0.80:
        return "middle"

    return "late"


def build_exclusion_reason(row: pd.Series) -> str | None:
    reasons: list[str] = []

    if row["bad_capacity_non_positive"]:
        reasons.append("capacity_non_positive")

    if row["bad_capacity_too_low"]:
        reasons.append("capacity_too_low")

    if row["bad_capacity_too_high"]:
        reasons.append("capacity_too_high")

    if row["bad_capacity_jump"]:
        reasons.append("capacity_jump_too_large")

    if row["bad_duration"]:
        reasons.append("invalid_duration")

    if not reasons:
        return None

    return ",".join(reasons)


def build_discharge_cycles_health(
    discharge_cycles: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = discharge_cycles.copy()

    df = df.sort_values(
        by=["battery_id", "discharge_cycle_number"]
    ).reset_index(drop=True)

    df["raw_previous_capacity_ah"] = (
        df.groupby("battery_id")["capacity_ah"].shift(1)
    )

    df["raw_capacity_change_from_previous_ah"] = (
        df["capacity_ah"] - df["raw_previous_capacity_ah"]
    )

    df["bad_capacity_non_positive"] = df["capacity_ah"] <= 0
    df["bad_capacity_too_low"] = df["capacity_ah"] < MIN_CAPACITY_AH
    df["bad_capacity_too_high"] = df["capacity_ah"] > MAX_CAPACITY_AH
    df["bad_capacity_jump"] = (
        df["raw_capacity_change_from_previous_ah"].abs()
        > MAX_ABS_CAPACITY_JUMP_AH
    )
    df["bad_duration"] = df["duration_seconds"] <= 0

    df["excluded_from_health_analytics"] = (
        df["bad_capacity_non_positive"]
        | df["bad_capacity_too_low"]
        | df["bad_capacity_too_high"]
        | df["bad_capacity_jump"]
        | df["bad_duration"]
    )

    df["health_exclusion_reason"] = df.apply(
        build_exclusion_reason,
        axis=1,
    )

    battery_rows: list[dict[str, Any]] = []

    for battery_id, group in df.groupby("battery_id"):
        total_discharge_cycles = int(len(group))
        excluded_discharge_cycles = int(
            group["excluded_from_health_analytics"].sum()
        )
        plausible_discharge_cycles = (
            total_discharge_cycles - excluded_discharge_cycles
        )

        bad_cycle_percent = (
            excluded_discharge_cycles / total_discharge_cycles * 100.0
            if total_discharge_cycles > 0
            else 100.0
        )

        usable_for_health_analytics = (
            plausible_discharge_cycles >= MIN_PLAUSIBLE_DISCHARGE_CYCLES
            and bad_cycle_percent < MAX_BAD_CYCLE_PERCENT
        )

        if usable_for_health_analytics:
            health_exclusion_reason = None
        elif plausible_discharge_cycles < MIN_PLAUSIBLE_DISCHARGE_CYCLES:
            health_exclusion_reason = "too_few_plausible_discharge_cycles"
        else:
            health_exclusion_reason = "too_many_implausible_discharge_cycles"

        battery_rows.append(
            {
                "battery_id": battery_id,
                "total_discharge_cycles": total_discharge_cycles,
                "plausible_discharge_cycles": plausible_discharge_cycles,
                "excluded_discharge_cycles": excluded_discharge_cycles,
                "bad_cycle_percent": bad_cycle_percent,
                "usable_for_health_analytics": usable_for_health_analytics,
                "health_exclusion_reason": health_exclusion_reason,
            }
        )

    health_quality = pd.DataFrame(battery_rows)

    usable_batteries = set(
        health_quality[
            health_quality["usable_for_health_analytics"]
        ]["battery_id"]
    )

    health_df = df[
        (~df["excluded_from_health_analytics"])
        & (df["battery_id"].isin(usable_batteries))
    ].copy()

    health_df = health_df.sort_values(
        by=["battery_id", "discharge_cycle_number"]
    ).reset_index(drop=True)

    health_df["original_discharge_cycle_number"] = health_df[
        "discharge_cycle_number"
    ]

    health_df["discharge_cycle_number"] = (
        health_df.groupby("battery_id").cumcount() + 1
    )

    health_df["reference_capacity_ah"] = (
        health_df.groupby("battery_id")["capacity_ah"].transform("max")
    )

    health_df["initial_capacity_ah"] = (
        health_df.groupby("battery_id")["capacity_ah"].transform("first")
    )

    health_df["previous_capacity_ah"] = (
        health_df.groupby("battery_id")["capacity_ah"].shift(1)
    )

    health_df["soh"] = (
        health_df["capacity_ah"] / health_df["reference_capacity_ah"]
    )

    health_df["eol_flag"] = health_df["soh"] <= 0.70

    health_df["capacity_change_from_reference_ah"] = (
        health_df["capacity_ah"] - health_df["reference_capacity_ah"]
    )

    health_df["capacity_change_from_reference_percent"] = (
        health_df["capacity_change_from_reference_ah"]
        / health_df["reference_capacity_ah"]
    ) * 100.0

    health_df["capacity_change_from_initial_ah"] = (
        health_df["capacity_ah"] - health_df["initial_capacity_ah"]
    )

    health_df["capacity_change_from_initial_percent"] = (
        health_df["capacity_change_from_initial_ah"]
        / health_df["initial_capacity_ah"]
    ) * 100.0

    health_df["capacity_change_from_previous_ah"] = (
        health_df["capacity_ah"] - health_df["previous_capacity_ah"]
    )

    health_df["capacity_change_from_previous_percent"] = (
        health_df["capacity_change_from_previous_ah"]
        / health_df["previous_capacity_ah"]
    ) * 100.0

    # Backward-compatible aliases used by existing analytics.
    # Signed convention:
    # positive = capacity increased/recovered
    # negative = capacity decreased/degraded
    health_df["capacity_fade_from_initial_ah"] = health_df[
        "capacity_change_from_reference_ah"
    ]

    health_df["capacity_fade_from_initial_percent"] = health_df[
        "capacity_change_from_reference_percent"
    ]

    health_df["capacity_fade_from_previous_ah"] = health_df[
        "capacity_change_from_previous_ah"
    ]

    health_df["capacity_fade_from_previous_percent"] = health_df[
        "capacity_change_from_previous_percent"
    ]

    health_df["capacity_fade_ah"] = health_df[
        "capacity_fade_from_initial_ah"
    ]

    health_df["capacity_fade_percent"] = health_df[
        "capacity_fade_from_initial_percent"
    ]

    health_df["life_stage"] = health_df["soh"].apply(classify_life_stage)

    health_df["rul_cycles_actual"] = None

    return health_df, health_quality