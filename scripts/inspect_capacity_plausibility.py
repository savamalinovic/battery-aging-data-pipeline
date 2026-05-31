import pandas as pd


LOWER_CAPACITY_AH = 0.5
UPPER_CAPACITY_AH = 2.2
MAX_ABS_JUMP_AH = 0.5


def main() -> None:
    df = pd.read_parquet("data/cleaned/discharge_cycles.parquet")

    df = df.sort_values(
        ["battery_id", "discharge_cycle_number"]
    ).copy()

    df["capacity_change_from_previous_ah"] = (
        df.groupby("battery_id")["capacity_ah"].diff()
    )

    df["bad_capacity_low_or_zero"] = df["capacity_ah"] <= 0
    df["bad_capacity_too_low"] = df["capacity_ah"] < LOWER_CAPACITY_AH
    df["bad_capacity_too_high"] = df["capacity_ah"] > UPPER_CAPACITY_AH
    df["bad_capacity_jump"] = (
        df["capacity_change_from_previous_ah"].abs() > MAX_ABS_JUMP_AH
    )

    df["bad_for_soh"] = (
        df["bad_capacity_low_or_zero"]
        | df["bad_capacity_too_low"]
        | df["bad_capacity_too_high"]
        | df["bad_capacity_jump"]
    )

    summary = (
        df.groupby("battery_id")
        .agg(
            discharge_cycles=("capacity_ah", "count"),
            min_capacity=("capacity_ah", "min"),
            p05_capacity=("capacity_ah", lambda s: s.quantile(0.05)),
            median_capacity=("capacity_ah", "median"),
            p95_capacity=("capacity_ah", lambda s: s.quantile(0.95)),
            max_capacity=("capacity_ah", "max"),
            bad_cycles=("bad_for_soh", "sum"),
            too_low_cycles=("bad_capacity_too_low", "sum"),
            too_high_cycles=("bad_capacity_too_high", "sum"),
            jump_cycles=("bad_capacity_jump", "sum"),
        )
        .reset_index()
    )

    summary["bad_cycle_percent"] = (
        summary["bad_cycles"] / summary["discharge_cycles"] * 100.0
    )

    summary["usable_for_soh_candidate"] = (
        (summary["bad_cycle_percent"] <= 20.0)
        & (summary["discharge_cycles"] >= 20)
        & (summary["max_capacity"] <= UPPER_CAPACITY_AH)
    )

    print("=" * 120)
    print("Most suspicious batteries")
    print("=" * 120)
    print(
        summary.sort_values(
            ["bad_cycle_percent", "max_capacity"],
            ascending=[False, False],
        )
        .head(30)
        .to_string(index=False)
    )

    print()
    print("=" * 120)
    print("B0050 discharge cycles")
    print("=" * 120)

    b0050 = df[df["battery_id"] == "B0050"].copy()

    if b0050.empty:
        print("B0050 not found.")
    else:
        columns = [
            "battery_id",
            "discharge_cycle_number",
            "cycle_index",
            "start_time",
            "capacity_ah",
            "capacity_change_from_previous_ah",
            "duration_seconds",
            "voltage_drop",
            "avg_temperature",
            "bad_capacity_too_low",
            "bad_capacity_too_high",
            "bad_capacity_jump",
            "bad_for_soh",
        ]

        print(b0050[columns].to_string(index=False))

    print()
    print("=" * 120)
    print("All batteries summary")
    print("=" * 120)
    print(summary.sort_values("battery_id").to_string(index=False))


if __name__ == "__main__":
    main()