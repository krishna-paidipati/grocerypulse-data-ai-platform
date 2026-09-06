from datetime import UTC, date, datetime
from decimal import Decimal

from grocerypulse.models.entities import Product, Store


def test_store_can_be_created() -> None:
    store = Store(
        store_id="STORE_0042",
        store_name="Belfast Central",
        store_format="SUPERSTORE",
        region="NORTHERN_IRELAND",
        city="Belfast",
        postcode="BT1 1AA",
        latitude=Decimal("54.5973"),
        longitude=Decimal("-5.9301"),
        open_date=date(2018, 4, 16),
        floor_area_sqm=4320,
        is_active=True,
        created_at=datetime.now(UTC),
    )

    assert store.store_id == "STORE_0042"
    assert store.is_active is True


def test_product_can_reference_supplier() -> None:
    product = Product(
        product_id="PROD_000291",
        sku="SKU_100291",
        product_name="Whole Milk 2L",
        brand="GroceryPulse",
        category="DAIRY",
        subcategory="MILK",
        unit_size=Decimal(2),
        unit_measure="L",
        unit_price=Decimal("1.85"),
        cost_price=Decimal("1.12"),
        vat_rate=Decimal("0.00"),
        shelf_life_days=8,
        is_perishable=True,
        supplier_id="SUP_0012",
        is_active=True,
        created_at=datetime.now(UTC),
    )

    assert product.supplier_id == "SUP_0012"
    assert product.unit_price == Decimal("1.85")