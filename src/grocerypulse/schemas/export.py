import json
from pathlib import Path

from grocerypulse.models.entities import (
    Customer,
    Product,
    Store,
    Supplier,
)

SCHEMAS = {
    "store": Store,
    "product": Product,
    "customer": Customer,
    "supplier": Supplier,
}

def export_json_schemas(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    for schema_name, model in SCHEMAS.items():
        output_path = output_dir / f"{schema_name}.json"
        with output_path.open("w", encoding="utf-8") as file:
            json.dump(model.model_json_schema(), 
                      file, 
                      indent=2,
                      )

if __name__ == "__main__":
    export_json_schemas(Path("schemas/json"))