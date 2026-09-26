"""Export generated GroceryPulse master data.

Code Owner:
    Vijay Krishna Paidipati

Component:
    GroceryPulse Synthetic Data Generation

Purpose:
    Persist validated synthetic master data as deterministic JSON Lines
    datasets for local development, testing, and downstream processing.

Developer Notes:
    JSON Lines is used as the initial interchange format because records can
    be processed independently and streamed without loading an entire dataset
    into memory.
"""

from collections.abc import Sequence
from pathlib import Path

from pydantic import BaseModel

from grocerypulse.generators.master_data import MasterDataset


def _write_jsonl(records: Sequence[BaseModel], output_path: Path) -> None:
    """Write validated Pydantic records to a JSON Lines file.

    Args:
        records: Validated records to serialize.
        output_path: Destination JSON Lines file.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8", newline="\n") as output_file:
        for record in records:
            output_file.write(record.model_dump_json())
            output_file.write("\n")


def export_master_dataset(
    dataset: MasterDataset,
    output_dir: Path,
) -> None:
    """Export a complete GroceryPulse master dataset as JSON Lines files.

    Args:
        dataset: Validated master dataset to export.
        output_dir: Directory receiving the exported entity files.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    _write_jsonl(dataset.suppliers, output_dir / "suppliers.jsonl")
    _write_jsonl(dataset.stores, output_dir / "stores.jsonl")
    _write_jsonl(dataset.products, output_dir / "products.jsonl")
    _write_jsonl(dataset.customers, output_dir / "customers.jsonl")
