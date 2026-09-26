"""Tests for GroceryPulse synthetic master-data export."""

import json
from pathlib import Path

from grocerypulse.generators.export import export_master_dataset
from grocerypulse.generators.master_data import MasterDataGenerator, MasterDataset


def _generate_test_dataset() -> MasterDataset:
    """Generate a small deterministic master dataset for export tests."""
    generator = MasterDataGenerator(seed=42)

    return generator.generate_dataset(
        supplier_count=5,
        store_count=4,
        product_count=10,
        customer_count=25,
    )


def test_export_master_dataset_creates_expected_files(tmp_path: Path) -> None:
    """Create one JSON Lines file for every master-data entity."""
    dataset = _generate_test_dataset()

    export_master_dataset(dataset, tmp_path)

    assert (tmp_path / "suppliers.jsonl").is_file()
    assert (tmp_path / "stores.jsonl").is_file()
    assert (tmp_path / "products.jsonl").is_file()
    assert (tmp_path / "customers.jsonl").is_file()


def test_export_master_dataset_writes_expected_record_counts(
    tmp_path: Path,
) -> None:
    """Write one JSON line for every generated master-data record."""
    dataset = _generate_test_dataset()

    export_master_dataset(dataset, tmp_path)

    expected_counts = {
        "suppliers.jsonl": 5,
        "stores.jsonl": 4,
        "products.jsonl": 10,
        "customers.jsonl": 25,
    }

    for filename, expected_count in expected_counts.items():
        lines = (tmp_path / filename).read_text(encoding="utf-8").splitlines()

        assert len(lines) == expected_count


def test_exported_records_are_valid_json(tmp_path: Path) -> None:
    """Ensure every exported JSON Lines record is valid JSON."""
    dataset = _generate_test_dataset()

    export_master_dataset(dataset, tmp_path)

    for filename in (
        "suppliers.jsonl",
        "stores.jsonl",
        "products.jsonl",
        "customers.jsonl",
    ):
        lines = (tmp_path / filename).read_text(encoding="utf-8").splitlines()

        assert all(isinstance(json.loads(line), dict) for line in lines)


def test_exported_products_match_generated_products(tmp_path: Path) -> None:
    """Preserve generated Product records during serialization."""
    dataset = _generate_test_dataset()

    export_master_dataset(dataset, tmp_path)

    exported_products = [
        json.loads(line)
        for line in (tmp_path / "products.jsonl").read_text(encoding="utf-8").splitlines()
    ]

    expected_products = [product.model_dump(mode="json") for product in dataset.products]

    assert exported_products == expected_products


def test_export_master_dataset_is_deterministic(tmp_path: Path) -> None:
    """Produce byte-identical output from identical generated datasets."""
    first_dataset = MasterDataGenerator(seed=42).generate_dataset(
        supplier_count=5,
        store_count=4,
        product_count=10,
        customer_count=25,
    )
    second_dataset = MasterDataGenerator(seed=42).generate_dataset(
        supplier_count=5,
        store_count=4,
        product_count=10,
        customer_count=25,
    )

    first_dir = tmp_path / "first"
    second_dir = tmp_path / "second"

    export_master_dataset(first_dataset, first_dir)
    export_master_dataset(second_dataset, second_dir)

    for filename in (
        "suppliers.jsonl",
        "stores.jsonl",
        "products.jsonl",
        "customers.jsonl",
    ):
        assert (first_dir / filename).read_bytes() == (second_dir / filename).read_bytes()


def test_export_master_dataset_is_idempotent(tmp_path: Path) -> None:
    """Replace existing output instead of appending duplicate records."""
    dataset = _generate_test_dataset()

    export_master_dataset(dataset, tmp_path)
    export_master_dataset(dataset, tmp_path)

    assert len((tmp_path / "products.jsonl").read_text(encoding="utf-8").splitlines()) == len(
        dataset.products
    )


def test_export_empty_dataset_creates_empty_files(tmp_path: Path) -> None:
    """Create valid empty entity files for an empty master dataset."""
    dataset = MasterDataGenerator(seed=42).generate_dataset(
        supplier_count=0,
        store_count=0,
        product_count=0,
        customer_count=0,
    )

    export_master_dataset(dataset, tmp_path)

    for filename in (
        "suppliers.jsonl",
        "stores.jsonl",
        "products.jsonl",
        "customers.jsonl",
    ):
        assert (tmp_path / filename).is_file()
        assert (tmp_path / filename).read_text(encoding="utf-8") == ""
