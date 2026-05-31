import pandas as pd

from pipeline.reference_capacity import normalize_battery_id
from pipeline.transforms.build_discharge_cycles import build_discharge_cycles


def test_normalize_battery_id_supports_short_aliases() -> None:
    assert normalize_battery_id("B033") == "B0033"
    assert normalize_battery_id("b34") == "B0034"
    assert normalize_battery_id("B0033") == "B0033"


def test_discharge_soh_uses_reference_capacity() -> None:
    cycle_summary = pd.DataFrame(
        [
            {
                "battery_id": "B0033",
                "cycle_index": 2,
                "operation_type": "discharge",
                "start_time": "2010-01-01 00:00:00",
                "capacity_ah": 1.90,
                "duration_seconds": 100.0,
                "start_voltage": 4.2,
                "end_voltage": 3.0,
                "voltage_drop": 1.2,
                "avg_voltage": 3.6,
                "avg_current": 1.0,
                "avg_temperature": 25.0,
                "max_temperature": 28.0,
                "temperature_delta_to_ambient": 1.0,
                "is_valid": True,
            },
            {
                "battery_id": "B0033",
                "cycle_index": 5,
                "operation_type": "discharge",
                "start_time": "2010-01-02 00:00:00",
                "capacity_ah": 2.05,
                "duration_seconds": 120.0,
                "start_voltage": 4.2,
                "end_voltage": 3.0,
                "voltage_drop": 1.2,
                "avg_voltage": 3.6,
                "avg_current": 1.0,
                "avg_temperature": 26.0,
                "max_temperature": 29.0,
                "temperature_delta_to_ambient": 2.0,
                "is_valid": True,
            },
        ]
    )

    discharge = build_discharge_cycles(cycle_summary)

    assert discharge["initial_capacity_ah"].tolist() == [1.90, 1.90]
    assert discharge["soh"].round(3).tolist() == [0.95, 1.025]
    assert discharge["soh_relative_to_initial"].round(3).tolist() == [
        1.0,
        1.079,
    ]
