from pathlib import Path
from typing import Any

from pipeline.raw.cycle_parser import parse_cycle
from pipeline.raw.mat_loader import load_battery_mat
from pipeline.reference_capacity import (
    get_reference_capacity_ah,
    normalize_battery_id,
)


RAW_DIR = Path("data/raw")
BATTERY_IDS = ["B033", "B034"]
PREVIEW_CYCLE_COUNT = 8


def safe_float(value: Any) -> float | None:
    if value is None:
        return None

    try:
        return float(value)
    except Exception:
        return None


def resolve_battery_path(battery_id: str) -> Path:
    normalized = normalize_battery_id(battery_id)
    path = RAW_DIR / f"{normalized}.mat"

    if not path.exists():
        raise FileNotFoundError(f"Battery file not found: {path}")

    return path


def print_battery_preview(battery_id: str) -> None:
    path = resolve_battery_path(battery_id)
    loaded = load_battery_mat(path)
    reference_capacity_ah = get_reference_capacity_ah(loaded["battery_id"])

    print("=" * 100)
    print(
        f"Battery request={battery_id} "
        f"resolved={loaded['battery_id']} "
        f"reference_capacity_ah={reference_capacity_ah}"
    )

    first_discharge_capacity_ah: float | None = None
    discharge_preview_count = 0

    for cycle_index, cycle in enumerate(loaded["cycles"]):
        parsed = parse_cycle(
            cycle=cycle,
            battery_id=loaded["battery_id"],
            cycle_index=cycle_index,
        )

        if parsed["operation_type"] != "discharge":
            continue

        capacity_ah = safe_float(parsed["data"].get("Capacity"))

        if capacity_ah is None:
            continue

        if first_discharge_capacity_ah is None:
            first_discharge_capacity_ah = capacity_ah

        soh_reference_percent = (
            capacity_ah / reference_capacity_ah
        ) * 100.0
        soh_initial_percent = (
            capacity_ah / first_discharge_capacity_ah
        ) * 100.0

        print(
            f"cycle_index={cycle_index} "
            f"start_time={parsed['start_time']} "
            f"capacity_ah={capacity_ah:.6f} "
            f"soh_reference_percent={soh_reference_percent:.2f} "
            f"soh_initial_percent={soh_initial_percent:.2f}"
        )

        discharge_preview_count += 1

        if discharge_preview_count >= PREVIEW_CYCLE_COUNT:
            break

    print()


def main() -> None:
    for battery_id in BATTERY_IDS:
        print_battery_preview(battery_id)


if __name__ == "__main__":
    main()
