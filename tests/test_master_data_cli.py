"""Tests for the GroceryPulse synthetic master-data CLI."""

from pathlib import Path
from unittest.mock import patch

from grocerypulse.generators.generate import main


def test_main_generates_default_dataset(tmp_path: Path) -> None:
    """Generate the default master dataset through the CLI."""
    output_dir = tmp_path / "master"

    test_args = [
        "generate",
        "--output-dir",
        str(output_dir),
    ]

    with patch("sys.argv", test_args):
        main()

    assert (output_dir / "suppliers.jsonl").is_file()
    assert (output_dir / "stores.jsonl").is_file()
    assert (output_dir / "products.jsonl").is_file()
    assert (output_dir / "customers.jsonl").is_file()

    assert len((output_dir / "suppliers.jsonl").read_text(encoding="utf-8").splitlines()) == 10
    assert len((output_dir / "stores.jsonl").read_text(encoding="utf-8").splitlines()) == 8
    assert len((output_dir / "products.jsonl").read_text(encoding="utf-8").splitlines()) == 15
    assert len((output_dir / "customers.jsonl").read_text(encoding="utf-8").splitlines()) == 100


def test_main_respects_custom_counts(tmp_path: Path) -> None:
    """Apply entity counts supplied through command-line arguments."""
    output_dir = tmp_path / "custom"

    test_args = [
        "generate",
        "--seed",
        "99",
        "--suppliers",
        "3",
        "--stores",
        "2",
        "--products",
        "5",
        "--customers",
        "7",
        "--output-dir",
        str(output_dir),
    ]

    with patch("sys.argv", test_args):
        main()

    expected_counts = {
        "suppliers.jsonl": 3,
        "stores.jsonl": 2,
        "products.jsonl": 5,
        "customers.jsonl": 7,
    }

    for filename, expected_count in expected_counts.items():
        records = (output_dir / filename).read_text(encoding="utf-8").splitlines()

        assert len(records) == expected_count


def test_main_is_deterministic_for_same_seed(tmp_path: Path) -> None:
    """Produce byte-identical CLI output for the same seed and counts."""
    first_dir = tmp_path / "first"
    second_dir = tmp_path / "second"

    common_args = [
        "--seed",
        "42",
        "--suppliers",
        "5",
        "--stores",
        "4",
        "--products",
        "10",
        "--customers",
        "25",
    ]

    with patch(
        "sys.argv",
        ["generate", *common_args, "--output-dir", str(first_dir)],
    ):
        main()

    with patch(
        "sys.argv",
        ["generate", *common_args, "--output-dir", str(second_dir)],
    ):
        main()

    for filename in (
        "suppliers.jsonl",
        "stores.jsonl",
        "products.jsonl",
        "customers.jsonl",
    ):
        assert (first_dir / filename).read_bytes() == (second_dir / filename).read_bytes()
