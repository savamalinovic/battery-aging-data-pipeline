from pathlib import Path


def test_inspection_script_exists() -> None:
    assert Path("scripts/inspect_b033_b034_cycles.py").exists()
