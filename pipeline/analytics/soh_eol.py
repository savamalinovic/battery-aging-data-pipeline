from typing import Any

import pandas as pd


def build_soh_eol_summary(
    discharge_cycles: pd.DataFrame,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    for battery_id, group in discharge_cycles.groupby("battery_id"):
        group = group.sort_values("discharge_cycle_number")

        initial_soh_percent = float(group["soh"].iloc[0] * 100.0)
        final_soh_percent = float(group["soh"].iloc[-1] * 100.0)
        min_soh_percent = float(group["soh"].min() * 100.0)
        avg_soh_percent = float(group["soh"].mean() * 100.0)

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

        capacity_at_eol_ah = None
        soh_at_eol_percent = None

        if eol_cycle is not None:
            eol_row = group[
                group["discharge_cycle_number"] == eol_cycle
            ].iloc[0]

            capacity_at_eol_ah = float(eol_row["capacity_ah"])
            soh_at_eol_percent = float(eol_row["soh"] * 100.0)

        rows.append(
            {
                "battery_id": battery_id,
                "initial_soh_percent": initial_soh_percent,
                "final_soh_percent": final_soh_percent,
                "min_soh_percent": min_soh_percent,
                "avg_soh_percent": avg_soh_percent,
                "cycle_below_80_soh": cycle_below_80_soh,
                "eol_cycle": eol_cycle,
                "capacity_at_eol_ah": capacity_at_eol_ah,
                "soh_at_eol_percent": soh_at_eol_percent,
                "rul_available": eol_cycle is not None,
            }
        )

    return pd.DataFrame(rows)