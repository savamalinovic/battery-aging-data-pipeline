from pathlib import Path
from typing import Any

from scipy.io import loadmat


def load_battery_mat(file_path: str | Path) -> dict[str, Any]:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    mat = loadmat(path, squeeze_me=True, struct_as_record=False)

    battery_id = path.stem

    if battery_id not in mat:
        raise KeyError(f"Expected key '{battery_id}' not found in {path.name}")

    battery_data = mat[battery_id]

    if not hasattr(battery_data, "cycle"):
        raise KeyError(f"No 'cycle' field found in {path.name}")

    cycles = battery_data.cycle

    if cycles.ndim == 0:
        cycles = [cycles]
    else:
        cycles = list(cycles)

    return {
        "battery_id": battery_id,
        "cycles": cycles,
    }


def get_cycle_type(cycle: Any) -> str:
    return str(cycle.type)


def summarize_battery_file(file_path: str | Path) -> dict[str, int | str]:
    loaded = load_battery_mat(file_path)

    counts = {
        "battery_id": loaded["battery_id"],
        "total_cycles": len(loaded["cycles"]),
        "charge_cycles": 0,
        "discharge_cycles": 0,
        "impedance_cycles": 0,
        "unknown_cycles": 0,
    }

    for cycle in loaded["cycles"]:
        cycle_type = get_cycle_type(cycle)

        if cycle_type == "charge":
            counts["charge_cycles"] += 1
        elif cycle_type == "discharge":
            counts["discharge_cycles"] += 1
        elif cycle_type == "impedance":
            counts["impedance_cycles"] += 1
        else:
            counts["unknown_cycles"] += 1

    return counts