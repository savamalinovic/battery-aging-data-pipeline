from pathlib import Path

from pipeline.raw.cycle_parser import parse_cycle
from pipeline.raw.mat_loader import load_battery_mat


RAW_FILE = Path("data/raw/B0005.mat")


def main() -> None:
    loaded = load_battery_mat(RAW_FILE)

    for cycle_index, cycle in enumerate(loaded["cycles"][:5]):
        parsed = parse_cycle(
            cycle=cycle,
            battery_id=loaded["battery_id"],
            cycle_index=cycle_index,
        )

        print("=" * 80)
        print(f"battery_id: {parsed['battery_id']}")
        print(f"cycle_index: {parsed['cycle_index']}")
        print(f"operation_type: {parsed['operation_type']}")
        print(f"start_time: {parsed['start_time']}")
        print(f"ambient_temperature: {parsed['ambient_temperature']}")
        print("data fields:")

        for field_name, value in parsed["data"].items():
            if hasattr(value, "shape"):
                print(f"  {field_name}: shape={value.shape}")
            else:
                print(f"  {field_name}: {value}")


if __name__ == "__main__":
    main()