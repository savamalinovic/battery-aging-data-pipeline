from typing import Any

import numpy as np


REQUIRED_DISCHARGE_FIELDS = [
    "Time",
    "Voltage_measured",
    "Current_measured",
    "Temperature_measured",
    "Capacity",
]

REQUIRED_CHARGE_FIELDS = [
    "Time",
    "Voltage_measured",
    "Current_measured",
    "Temperature_measured",
]

REQUIRED_IMPEDANCE_FIELDS = [
    "Battery_impedance",
    "Rectified_Impedance",
    "Re",
    "Rct",
]


def is_monotonic_increasing(values: np.ndarray) -> bool:
    if len(values) < 2:
        return True

    diffs = np.diff(values)

    return np.all(diffs >= 0)


def validate_cycle(parsed_cycle: dict[str, Any]) -> dict[str, Any]:
    operation_type = parsed_cycle["operation_type"]
    data = parsed_cycle["data"]

    errors: list[dict[str, str]] = []

    if operation_type == "discharge":
        required_fields = REQUIRED_DISCHARGE_FIELDS
    elif operation_type == "charge":
        required_fields = REQUIRED_CHARGE_FIELDS
    elif operation_type == "impedance":
        required_fields = REQUIRED_IMPEDANCE_FIELDS
    else:
        errors.append(
            {
                "error_code": "unknown_operation_type",
                "error_description": f"Unknown operation type: {operation_type}",
                "severity": "high",
            }
        )

        required_fields = []

    for field_name in required_fields:
        if field_name not in data:
            errors.append(
                {
                    "error_code": "missing_field",
                    "error_description": f"Missing required field: {field_name}",
                    "severity": "high",
                }
            )

            continue

        value = data[field_name]

        if isinstance(value, np.ndarray):
            if len(value) == 0:
                errors.append(
                    {
                        "error_code": "empty_array",
                        "error_description": f"Empty array: {field_name}",
                        "severity": "high",
                    }
                )

    if "Time" in data:
        time_values = data["Time"]

        if isinstance(time_values, np.ndarray):
            if not is_monotonic_increasing(time_values):
                errors.append(
                    {
                        "error_code": "non_monotonic_time",
                        "error_description": "Time array is not monotonic increasing",
                        "severity": "high",
                    }
                )

    measurement_fields = [
        "Time",
        "Voltage_measured",
        "Current_measured",
        "Temperature_measured",
    ]

    existing_lengths = []

    for field_name in measurement_fields:
        if field_name in data:
            value = data[field_name]

            if isinstance(value, np.ndarray):
                existing_lengths.append((field_name, len(value)))

    if existing_lengths:
        unique_lengths = {length for _, length in existing_lengths}

        if len(unique_lengths) > 1:
            errors.append(
                {
                    "error_code": "array_length_mismatch",
                    "error_description": str(existing_lengths),
                    "severity": "high",
                }
            )

    if operation_type == "discharge":
        capacity = data.get("Capacity")

        if capacity is None:
            errors.append(
                {
                    "error_code": "missing_capacity",
                    "error_description": "Discharge cycle missing Capacity",
                    "severity": "high",
                }
            )

        else:
            try:
                capacity_value = float(capacity)

                if capacity_value <= 0:
                    errors.append(
                        {
                            "error_code": "invalid_capacity",
                            "error_description": f"Invalid capacity: {capacity_value}",
                            "severity": "high",
                        }
                    )

            except Exception:
                errors.append(
                    {
                        "error_code": "invalid_capacity_type",
                        "error_description": "Capacity could not be converted to float",
                        "severity": "high",
                    }
                )

    return {
        "is_valid": len(errors) == 0,
        "errors": errors,
    }