from pathlib import Path

import numpy as np

from pipeline.raw.mat_loader import load_battery_mat


RAW_FILE = Path("data/raw/B0005.mat")


def public_fields(obj: object) -> list[str]:
    return sorted(
        field
        for field in dir(obj)
        if not field.startswith("_")
    )


def preview_value(value: object, max_items: int = 5) -> str:
    """
    Create readable preview for arrays/scalars.
    """

    if isinstance(value, np.ndarray):
        flat = value.flatten()

        preview = flat[:max_items]

        return (
            f"ndarray | shape={value.shape} | "
            f"first_values={preview}"
        )

    if isinstance(value, (list, tuple)):
        preview = value[:max_items]

        return (
            f"{type(value).__name__} | "
            f"len={len(value)} | "
            f"first_values={preview}"
        )

    return repr(value)


def main() -> None:
    loaded = load_battery_mat(RAW_FILE)

    seen_types: set[str] = set()

    for cycle_index, cycle in enumerate(loaded["cycles"]):
        cycle_type = str(cycle.type)

        if cycle_type in seen_types:
            continue

        seen_types.add(cycle_type)

        print("=" * 100)
        print(f"Cycle type: {cycle_type}")
        print(f"Example cycle index: {cycle_index}")
        print()

        print("Cycle fields:")
        cycle_fields = public_fields(cycle)

        for field in cycle_fields:
            value = getattr(cycle, field)

            print(f"  {field}:")
            print(f"    {preview_value(value)}")

        print()
        print("-" * 100)
        print()

        print("Data fields:")
        data_fields = public_fields(cycle.data)

        for field in data_fields:
            value = getattr(cycle.data, field)

            print(f"  {field}:")
            print(f"    {preview_value(value)}")

        print()
        print("=" * 100)
        print()

        if len(seen_types) == 3:
            break


if __name__ == "__main__":
    main()