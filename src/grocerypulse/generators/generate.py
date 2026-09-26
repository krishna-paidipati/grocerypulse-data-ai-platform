"""Generate GroceryPulse synthetic master-data files.

Code Owner:
    Vijay Krishna Paidipati

Component:
    GroceryPulse Synthetic Data Generation

Purpose:
    Provide a command-line entry point for generating deterministic synthetic
    GroceryPulse master data for development and downstream processing.

Developer Notes:
    Default values create a small reproducible local development dataset.
    The seed controls deterministic generation.
"""

import argparse
from pathlib import Path

from grocerypulse.generators.export import export_master_dataset
from grocerypulse.generators.master_data import MasterDataGenerator


def _parse_args() -> argparse.Namespace:
    """Parse command-line arguments for synthetic master-data generation.

    Returns:
        Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(description="Generate deterministic GroceryPulse master data.")

    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Deterministic random seed (default: 42).",
    )
    parser.add_argument(
        "--suppliers",
        type=int,
        default=10,
        help="Number of suppliers to generate (default: 10).",
    )
    parser.add_argument(
        "--stores",
        type=int,
        default=8,
        help="Number of stores to generate (default: 8).",
    )
    parser.add_argument(
        "--products",
        type=int,
        default=15,
        help="Number of products to generate (default: 15).",
    )
    parser.add_argument(
        "--customers",
        type=int,
        default=100,
        help="Number of customers to generate (default: 100).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/synthetic/master"),
        help="Output directory (default: data/synthetic/master).",
    )

    return parser.parse_args()


def main() -> None:
    """Generate and export a complete synthetic master dataset."""
    args = _parse_args()

    generator = MasterDataGenerator(seed=args.seed)
    dataset = generator.generate_dataset(
        supplier_count=args.suppliers,
        store_count=args.stores,
        product_count=args.products,
        customer_count=args.customers,
    )

    export_master_dataset(dataset, args.output_dir)

    print(
        "Generated GroceryPulse master data: "
        f"{len(dataset.suppliers)} suppliers, "
        f"{len(dataset.stores)} stores, "
        f"{len(dataset.products)} products, "
        f"{len(dataset.customers)} customers "
        f"-> {args.output_dir}"
    )


if __name__ == "__main__":
    main()
