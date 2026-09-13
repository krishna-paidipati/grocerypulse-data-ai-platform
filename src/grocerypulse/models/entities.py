from datetime import UTC, date, datetime
from decimal import Decimal

from pydantic import Field, field_validator, model_validator

from grocerypulse.models.base import GroceryPuluseModel
from grocerypulse.models.enums import (
    CustomerSegment,
    ProductCategory,
    SalesChannel,
    StoreFormat,
    SupplierType,
    UnitMeasure,
)


class Store(GroceryPuluseModel):
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

    longitude: Decimal  = Field(
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

class Supplier(GroceryPuluseModel):
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
    lead_time_days: int = Field(
        ge=0,
        le=365
    )
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

class Product(GroceryPuluseModel):
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
    cost_price: Decimal = Field(
        ge=0,
        decimal_places=2
    )
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
    def validate_perishable_product(self):
        if self.is_perishable and self.shelf_life_days is None:
            raise ValueError(
                "Perishable products must have a shelf life defined"
            )
        return self
    
    @model_validator(mode="after")
    def validate_product_margin(self):
        if self.unit_price < self.cost_price:
            raise ValueError(
                "Unit price must be greater than or equal to cost price"
            )
        return self


class Customer(GroceryPuluseModel):
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
        if value > datetime.now(UTC).date():
            raise ValueError("Signup date cannot be in the future")
        return value