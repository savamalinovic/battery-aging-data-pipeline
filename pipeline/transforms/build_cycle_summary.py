from typing import Any

import numpy as np
import pandas as pd

from pipeline.raw.cycle_parser import parse_cycle
from pipeline.validation.cycle_validation import validate_cycle


RATED_CAPACITY_AH = 2.0


def safe_mean(value: Any) -> float | None:
    if not isinstance(value, np.ndarray) or len(value) == 0:
        return None

    return float(np.mean(value))


def safe_max(value: Any) -> float | None:
    if not isinstance(value, np.ndarray) or len(value) == 0:
        return None

    return float(np.max(value))


def safe_first(value: Any) -> float | None:
    if not isinstance(value, np.ndarray) or len(value) == 0:
        return None

    return float(value[0])


def safe_last(value: Any) -> float | None:
    if not isinstance(value, np.ndarray) or len(value) == 0:
        return None

    return float(value[-1])


def safe_duration(time_values: Any) -> float | None:
    if not isinstance(time_values, np.ndarray) or len(time_values) == 0:
        return None

    return float(np.max(time_values) - np.min(time_values))


def safe_float(value: Any) -> float | None:
    if value is None:
        return None

    if isinstance(value, np.ndarray):
        if len(value) == 0:
            return None

        return float(value.flatten()[0])

    return float(value)


def build_cycle_summary_for_battery(
    battery_id: str,
    cycles: list[Any],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    summary_rows: list[dict[str, Any]] = []
    invalid_rows: list[dict[str, Any]] = []

    for cycle_index, cycle in enumerate(cycles):
        parsed = parse_cycle(
            cycle=cycle,
            battery_id=battery_id,
            cycle_index=cycle_index,
        )

        validation = validate_cycle(parsed)

        data = parsed["data"]
        operation_type = parsed["operation_type"]

        time_values = data.get("Time")
        voltage_values = data.get("Voltage_measured")
        current_values = data.get("Current_measured")
        temperature_values = data.get("Temperature_measured")

        capacity_ah = None
        soh = None
        eol_flag = False

        if operation_type == "discharge" and "Capacity" in data:
            capacity_ah = safe_float(data.get("Capacity"))

            if capacity_ah is not None:
                soh = capacity_ah / RATED_CAPACITY_AH
                eol_flag = capacity_ah <= 1.4 or soh <= 0.70

        avg_voltage = safe_mean(voltage_values)
        start_voltage = safe_first(voltage_values)
        end_voltage = safe_last(voltage_values)

        voltage_drop = None
        if operation_type == "discharge" and start_voltage is not None and end_voltage is not None:
            voltage_drop = start_voltage - end_voltage

        avg_temperature = safe_mean(temperature_values)
        max_temperature = safe_max(temperature_values)

        ambient_temperature = parsed["ambient_temperature"]

        temperature_delta_to_ambient = None
        if avg_temperature is not None and ambient_temperature is not None:
            temperature_delta_to_ambient = avg_temperature - float(ambient_temperature)

        row = {
            "battery_id": battery_id,
            "cycle_index": cycle_index,
            "operation_type": operation_type,
            "start_time": parsed["start_time"],
            "ambient_temperature": ambient_temperature,
            "duration_seconds": safe_duration(time_values),
            "sample_count": len(time_values) if isinstance(time_values, np.ndarray) else None,
            "capacity_ah": capacity_ah,
            "soh": soh,
            "eol_flag": eol_flag,
            "avg_voltage": avg_voltage,
            "start_voltage": start_voltage,
            "end_voltage": end_voltage,
            "voltage_drop": voltage_drop,
            "avg_current": safe_mean(current_values),
            "avg_temperature": avg_temperature,
            "max_temperature": max_temperature,
            "temperature_delta_to_ambient": temperature_delta_to_ambient,
            "is_valid": validation["is_valid"],
        }

        summary_rows.append(row)

        if not validation["is_valid"]:
            for error in validation["errors"]:
                invalid_rows.append(
                    {
                        "battery_id": battery_id,
                        "cycle_index": cycle_index,
                        "operation_type": operation_type,
                        "error_code": error["error_code"],
                        "error_description": error["error_description"],
                        "severity": error["severity"],
                        "excluded_from_analytics": True,
                    }
                )

    return pd.DataFrame(summary_rows), pd.DataFrame(invalid_rows)