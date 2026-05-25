import pandas as pd


def build_rolling_degradation_summary(
    discharge_cycles: pd.DataFrame,
) -> pd.DataFrame:
    df = discharge_cycles.copy()

    df = df.sort_values(
        by=["battery_id", "discharge_cycle_number"]
    ).reset_index(drop=True)

    # Rolling averages smooth noisy degradation measurements.
    df["rolling_capacity_5"] = (
        df.groupby("battery_id")["capacity_ah"]
        .transform(
            lambda s: s.rolling(
                window=5,
                min_periods=1,
            ).mean()
        )
    )

    df["rolling_soh_5"] = (
        df.groupby("battery_id")["soh"]
        .transform(
            lambda s: s.rolling(
                window=5,
                min_periods=1,
            ).mean()
        )
    )

    # Degradation acceleration:
    # how much the cycle-to-cycle degradation itself changes.
    df["degradation_acceleration_percent"] = (
        df.groupby("battery_id")[
            "capacity_fade_from_previous_percent"
        ].diff()
    )

    # Absolute degradation magnitude.
    df["absolute_capacity_drop_percent"] = (
        df["capacity_fade_from_previous_percent"].abs()
    )

    output_columns = [
        "battery_id",
        "discharge_cycle_number",
        "capacity_ah",
        "soh",
        "rolling_capacity_5",
        "rolling_soh_5",
        "capacity_fade_from_previous_percent",
        "capacity_fade_from_initial_percent",
        "degradation_acceleration_percent",
        "absolute_capacity_drop_percent",
        "avg_temperature",
        "temperature_delta_to_ambient",
        "duration_seconds",
        "life_stage",
        "eol_flag",
    ]

    return df[output_columns]