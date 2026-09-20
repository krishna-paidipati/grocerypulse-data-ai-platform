"""Tests for the schema export functionality in the GroceryPulse project."""

import json
from pathlib import Path

import pytest

from grocerypulse.schemas.export import export_json_schemas


def test_export_json_schemas_creates_expected_files(tmp_path: Path) -> None:
    """Verify that JSON Schema files are generated correctly."""
    # Call the export function with a temporary directory
    output_dir = tmp_path / "schemas"
    export_json_schemas(output_dir)

    # Check that the expected schema files are created
    expected_files = {"store.json", "product.json", "customer.json", "supplier.json"}
    generated_files = {path.name for path in output_dir.iterdir()}
    assert generated_files == expected_files


def test_generated_product_schema_is_valid_json(tmp_path: Path) -> None:
    """Verify that the generated product schema is valid JSON."""
    output_dir = tmp_path / "schemas"
    export_json_schemas(output_dir)

    product_schema_path = output_dir / "product.json"
    assert product_schema_path.exists(), "Product schema file was not created."

    # Load the generated JSON schema and verify it's valid JSON
    with product_schema_path.open("r", encoding="utf-8") as file:
        try:
            schema_data = json.load(file)
        except json.JSONDecodeError as e:
            pytest.fail(f"Generated product schema is not valid JSON: {e}")

    # Optionally, check for expected keys in the schema
    expected_keys = {"title", "type", "properties", "required"}
    assert expected_keys.issubset(schema_data.keys()), (
        f"Schema is missing expected keys: {expected_keys - set(schema_data.keys())}"
    )
