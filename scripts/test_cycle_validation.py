from pathlib import Path

from pipeline.raw.cycle_parser import parse_cycle
from pipeline.raw.mat_loader import load_battery_mat
from pipeline.validation.cycle_validation import validate_cycle


RAW_FILE = Path("data/raw/B0005.mat")


def main() -> None:
    loaded = load_battery_mat(RAW_FILE)

    valid_count = 0
    invalid_count = 0

    for cycle_index, cycle in enumerate(loaded["cycles"]):
        parsed = parse_cycle(
            cycle=cycle,
            battery_id=loaded["battery_id"],
            cycle_index=cycle_index,
        )

        validation = validate_cycle(parsed)

        if validation["is_valid"]:
            valid_count += 1
        else:
            invalid_count += 1

            print("=" * 80)
            print(f"Invalid cycle: {cycle_index}")
            print(f"Type: {parsed['operation_type']}")

            for error in validation["errors"]:
                print(error)

    print()
    print("=" * 80)
    print(f"Valid cycles: {valid_count}")
    print(f"Invalid cycles: {invalid_count}")


if __name__ == "__main__":
    main()