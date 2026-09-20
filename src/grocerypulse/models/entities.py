"""Canonical GroceryPulse retail entity models.

Code Owner:
    Vijay Krishna Paidipati

Component:
    Retail Domain Model / Canonical Data Contracts

Purpose:
    Defines validated representations of core retail entities including
    stores, suppliers, products, and customers.

Developer Notes:
    These models are authoritative contracts for the initial GroceryPulse
    domain. Changes can affect generated JSON Schemas and downstream
    producers, consumers, transformations, APIs, and tests.

    Breaking changes should therefore be treated as explicit schema
    evolution rather than casual field modifications.
"""

from datetime import UTC, date, datetime
from decimal import Decimal
from typing import Self

from pydantic import Field, field_validator, model_validator

from grocerypulse.models.base import GroceryPulseModel
from grocerypulse.models.enums import (
    CustomerSegment,
    ProductCategory,
    SalesChannel,
    StoreFormat,
    SupplierType,
    UnitMeasure,
)


class Store(GroceryPulseModel):
    """Represent one GroceryPulse retail or fulfilment location.

    Grain:
        One model instance represents one physical or fulfilment location.

    Primary Key:
        ``store_id``

    Notes:
        Geographic coordinates are validated against globally valid latitude
        and longitude ranges. Future planned stores may require extending the
        lifecycle model rather than weakening the current opening-date rule.
    """

    store_id: str = Field(
        pattern=r"^STORE_\d{4}$",
        description="Unique identifier for the store, e.g., STORE_0001",
    )

    store_name: str = Field(
        min_length=2,
        max_length=120,
        description="Name of the store, e.g., 'Downtown Supermarket'",
    )

    store_format: StoreFormat

    region: str = Field(
        min_length=2,
        max_length=80,
    )

    city: str = Field(
        min_length=2,
        max_length=80,
    )

    postcode: str = Field(
        min_length=5,
        max_length=10,
    )

    latitude: Decimal = Field(
        ge=-90,
        le=90,
    )

    longitude: Decimal = Field(
        ge=-180,
        le=180,
    )

    open_date: date

    floor_area_sqm: int | None = Field(
        ge=0,
        default=None,
    )

    is_active: bool = True

    created_at: datetime

    @field_validator("open_date")
    @classmethod
    def open_date_cannot_be_future(cls, value: date) -> date:
        """Reject opening dates later than the current calendar date.

        Args:
        value:
            Store opening date supplied by the producer.

        Returns:
        The validated opening date.

        Raises:
        ValueError:
            If the opening date is in the future.
        """
        if value > datetime.now(UTC).date():
            raise ValueError("Open date cannot be in the future")
        return value


class Supplier(GroceryPulseModel):
    """Represent one GroceryPulse product supplier.

    Grain:
        One model instance represents one product supplier.

    Primary Key:
        ``supplier_id``

    Notes:
        Supplier reliability scores are represented as a decimal between 0.0
        and 1.0, where 1.0 indicates the highest reliability.
        Future planned suppliers may require extending the lifecycle model rather than weakening
        the current reliability score rule.

    """

    supplier_id: str = Field(
        pattern=r"^SUP_\d{4}$",
    )
    supplier_name: str = Field(
        min_length=2,
        max_length=120,
    )
    supplier_type: SupplierType
    country: str = Field(
        min_length=2,
        max_length=80,
    )
    lead_time_days: int = Field(ge=0, le=365)
    min_order_qty: int | None = Field(
        ge=0,
        default=None,
    )
    reliability_score: Decimal | None = Field(
        ge=Decimal("0.0"),
        le=Decimal("1.0"),
        default=None,
    )
    is_active: bool = True
    created_at: datetime


class Product(GroceryPulseModel):
    """Represent one sellable GroceryPulse stock-keeping unit (SKU).

    Grain:
        One model instance represents one sellable SKU.

    Primary Key:
        ``product_id``

    Business Key:
        ``sku``

    Notes:
        Standard product pricing is stored here. Promotional checkout pricing
        will be modelled separately rather than modifying canonical list price.
    """

    product_id: str = Field(
        pattern=r"^PROD_\d{6}$",
    )
    sku: str = Field(
        pattern=r"^SKU_\d{6}$",
    )
    product_name: str = Field(
        min_length=2,
        max_length=120,
    )
    brand: str | None = Field(
        max_length=120,
        default=None,
    )
    category: ProductCategory
    subcategory: str = Field(
        min_length=2,
        max_length=100,
    )
    unit_size: Decimal | None = Field(
        ge=0,
        default=None,
    )
    unit_measure: UnitMeasure | None = None
    unit_price: Decimal = Field(
        ge=0,
        decimal_places=2,
    )
    cost_price: Decimal = Field(ge=0, decimal_places=2)
    vat_rate: Decimal = Field(
        ge=0,
        le=1,
    )
    shelf_life_days: int | None = Field(
        ge=0,
        default=None,
    )
    is_perishable: bool
    supplier_id: str | None = Field(
        pattern=r"^SUP_\d{4}$",
        default=None,
    )
    is_active: bool = True
    created_at: datetime

    @model_validator(mode="after")
    def validate_perishable_product(self) -> Self:
        """Ensure perishable products have a defined shelf life.

        Returns:
            The validated product instance.

        Raises:
            ValueError: If a perishable product does not have a defined shelf life.

        """
        if self.is_perishable and self.shelf_life_days is None:
            raise ValueError("Perishable products must have a shelf life defined")
        return self

    @model_validator(mode="after")
    def validate_product_margin(self) -> Self:
        """Ensure canonical cost does not exceed standard selling price.

        Promotional discounts and loss-leader behaviour will be represented in
        separate promotional and transactional datasets. This rule therefore
        applies only to the canonical standard product price.

        Returns:
            The validated product instance.

        Raises:
            ValueError: If a perishable product has no shelf-life value.
        """
        if self.is_perishable and self.shelf_life_days is None:
            raise ValueError("Perishable products must define shelf_life_days")

        return self


class Customer(GroceryPulseModel):
    """Represent one GroceryPulse retail customer.

    Grain:
        One model instance represents one retail customer.

    Primary Key:
        ``customer_id``

    Business Key:
        ``loyalty_id``

    Notes:
        Customer segmentation and marketing preferences are stored here. Future
        transactional and behavioural datasets will be modelled separately rather than
        modifying canonical customer attributes.
    """

    customer_id: str = Field(
        pattern=r"^CUST_\d{6}$",
    )
    loyalty_id: str | None = Field(
        pattern=r"^LOY_\d{6}$",
        default=None,
    )
    customer_segment: CustomerSegment
    home_region: str | None = Field(
        max_length=80,
        default=None,
    )
    signup_date: date
    preferred_channel: SalesChannel | None = None
    marketing_opt_in: bool = False
    is_active: bool = True
    created_at: datetime

    @field_validator("signup_date")
    @classmethod
    def signup_date_cannot_be_future(cls, value: date) -> date:
        """Reject signup dates later than the current calendar date.

        Args:
            value: Customer signup date supplied by the producer.
        returns:
            The validated signup date.
        raises:
            ValueError: If the signup date is in the future.

        """
        if value > datetime.now(UTC).date():
            raise ValueError("Signup date cannot be in the future")
        return value
