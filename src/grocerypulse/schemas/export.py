"""Export GroceryPulse Pydantic contracts as JSON Schema documents.

Code Owner:
    Vijay Krishna Paidipati

Component:
    Schema Registry / Contract Export

Purpose:
    Converts canonical Pydantic domain models into portable JSON Schema files.

Developer Notes:
    Generated files should not be manually edited. Their source of truth is
    the corresponding canonical Pydantic model.
"""

import json
from pathlib import Path

from pydantic import BaseModel

from grocerypulse.models.entities import (
    Customer,
    Product,
    Store,
    Supplier,
)

SCHEMAS: dict[str, type[BaseModel]] = {
    "store": Store,
    "product": Product,
    "customer": Customer,
    "supplier": Supplier,
}


def export_json_schemas(output_dir: Path) -> None:
    """Export all canonical models into JSON Schema files.

    Args:
        output_dir (Path):
            Destination directory for generated ``*.schema.json`` files.

    Raises:
        OSError:
            If the output directory or generated files cannot be written.
    """
    # Schema generation is intentionally idempotent so developers and CI can
    # regenerate contracts without manually preparing the directory.
    output_dir.mkdir(parents=True, exist_ok=True)

    for schema_name, model in SCHEMAS.items():
        output_path = output_dir / f"{schema_name}.json"
        with output_path.open("w", encoding="utf-8") as file:
            json.dump(
                model.model_json_schema(),
                file,
                indent=2,
            )
            file.write("\n")


if __name__ == "__main__":
    export_json_schemas(Path("schemas/json"))
