"""Tests for canonical GroceryPulse retail entity validation.

Code Owner:
    Vijay Krishna Paidipati

Component:
    Canonical Data Contract Tests

Purpose:
    Verifies that valid retail entities are accepted and invalid domain data is
    rejected before entering trusted GroceryPulse processing layers.
"""

from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

import pytest
from pydantic import ValidationError

from grocerypulse.models.entities import Customer, Product, Store, Supplier
from grocerypulse.models.enums import (
    CustomerSegment,
    ProductCategory,
    StoreFormat,
    SupplierType,
    UnitMeasure,
)


def test_store_can_be_created() -> None:
    """Verify that valid canonical store data produces a Store model."""
    store = Store(
        store_id="STORE_0042",
        store_name="Belfast Central",
        store_format=StoreFormat.SUPERMARKET,
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
    assert store.store_format == StoreFormat.SUPERMARKET


def test_invalid_store_id_is_rejected() -> None:
    """Verify that store identifiers violating the contract are rejected."""
    with pytest.raises(ValidationError):
        Store(
            store_id="INVALID_STORE_ID",
            store_name="Belfast Central",
            store_format=StoreFormat.SUPERMARKET,
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


def test_product_can_reference_supplier() -> None:
    """Verify that a valid product entity can be instantiated with a supplier reference."""
    product = Product(
        product_id="PROD_000291",
        sku="SKU_100291",
        product_name="Whole Milk 2L",
        brand="GroceryPulse",
        category=ProductCategory.DAIRY,
        subcategory="MILK",
        unit_size=Decimal(2),
        unit_measure=UnitMeasure.L,
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


def test_invalid_latitude_is_rejected() -> None:
    """Reject store entities with latitude values outside the valid range."""
    with pytest.raises(ValidationError):
        Store(
            store_id="STORE_0042",
            store_name="Belfast Central",
            store_format=StoreFormat.SUPERMARKET,
            region="NORTHERN_IRELAND",
            city="Belfast",
            postcode="BT1 1AA",
            latitude=Decimal("100.0000"),  # Invalid latitude
            longitude=Decimal("-5.9301"),
            open_date=date(2018, 4, 16),
            floor_area_sqm=4320,
            is_active=True,
            created_at=datetime.now(UTC),
        )


def test_supplier_reliability_score_validation() -> None:
    """Reject supplier reliability scores outside the canonical 0-1 range."""
    with pytest.raises(ValidationError):
        Supplier(
            supplier_id="SUP_0012",
            supplier_name="Fresh Produce Ltd.",
            supplier_type=SupplierType.NATIONAL,
            reliability_score=Decimal("1.5"),  # Invalid reliability score
            is_active=True,
            country="UK",
            lead_time_days=5,
            min_order_qty=10,
            created_at=datetime.now(UTC),
        )


def test_valid_supplier_can_be_created() -> None:
    """Verify that a valid supplier entity can be instantiated."""
    supplier = Supplier(
        supplier_id="SUP_0012",
        supplier_name="Fresh Produce Ltd.",
        supplier_type=SupplierType.NATIONAL,
        reliability_score=Decimal("0.85"),
        country="UK",
        lead_time_days=5,
        min_order_qty=10,
        is_active=True,
        created_at=datetime.now(UTC),
    )

    assert supplier.supplier_id == "SUP_0012"
    assert supplier.reliability_score == Decimal("0.85")


def test_negative_product_price_is_rejected() -> None:
    """Reject product entities with negative unit prices."""
    with pytest.raises(ValidationError):
        Product(
            product_id="PROD_000291",
            sku="SKU_100291",
            product_name="Whole Milk 2L",
            brand="GroceryPulse",
            category=ProductCategory.DAIRY,
            subcategory="MILK",
            unit_size=Decimal(2),
            unit_measure=UnitMeasure.L,
            unit_price=Decimal("-1.85"),  # Invalid negative price
            cost_price=Decimal("1.12"),
            vat_rate=Decimal("0.00"),
            shelf_life_days=8,
            is_perishable=True,
            supplier_id="SUP_0012",
            is_active=True,
            created_at=datetime.now(UTC),
        )


def test_perishable_product_requires_shelf_life() -> None:
    """Reject perishable product entities that do not specify a shelf life."""
    with pytest.raises(ValidationError):
        Product(
            product_id="PROD_000292",
            sku="SKU_100292",
            product_name="Fresh Salad Mix",
            brand="GroceryPulse",
            category=ProductCategory.PRODUCE,
            subcategory="SALADS",
            unit_size=Decimal("0.5"),
            unit_measure=UnitMeasure.KG,
            unit_price=Decimal("3.50"),
            cost_price=Decimal("2.00"),
            vat_rate=Decimal("0.00"),
            shelf_life_days=None,  # Missing shelf life for perishable product
            is_perishable=True,
            supplier_id="SUP_0013",
            is_active=True,
            created_at=datetime.now(UTC),
        )


def test_future_customer_signup_date_is_rejected() -> None:
    """Reject customer entities with signup dates in the future."""
    with pytest.raises(ValidationError):
        Customer(
            customer_id="CUST_0001",
            customer_segment=CustomerSegment.FAMILY,
            signup_date=datetime.now(UTC).date() + timedelta(days=1),  # Future date
            is_active=True,
            created_at=datetime.now(UTC),
        )


def test_unknown_fields_are_rejected() -> None:
    """Verify that fields outside the canonical Store contract are rejected."""
    invalid_store_data = {
        "store_id": "STORE_0042",
        "store_name": "Belfast Central",
        "store_format": StoreFormat.SUPERMARKET,
        "region": "NORTHERN_IRELAND",
        "city": "Belfast",
        "postcode": "BT1 1AA",
        "latitude": Decimal("54.5973"),
        "longitude": Decimal("-5.9301"),
        "open_date": date(2018, 4, 16),
        "floor_area_sqm": 4320,
        "is_active": True,
        "created_at": datetime.now(UTC),
        "unknown_field": "This field does not exist",  # Unknown field
    }

    with pytest.raises(ValidationError):
        Store.model_validate(invalid_store_data)
