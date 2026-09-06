from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal


@dataclass
class Store:
    store_id: str
    store_name: str
    store_format: str
    region: str
    city: str
    postcode: str
    latitude: Decimal
    longitude: Decimal
    open_date: date
    floor_area_sqm: int | None
    is_active: bool
    created_at: datetime

@dataclass
class Supplier:
    supplier_id: str
    supplier_name: str
    supplier_type: str
    country: str
    lead_time_days: int
    min_order_qty: int | None
    reliability_score: Decimal | None
    is_active: bool
    created_at: datetime

@dataclass
class Product:
    product_id: str
    sku: str
    product_name: str
    brand: str | None
    category: str
    subcategory: str
    unit_size: Decimal | None
    unit_measure: str | None
    unit_price: Decimal
    cost_price: Decimal
    vat_rate: Decimal
    shelf_life_days: int | None
    is_perishable: bool
    supplier_id: str | None
    is_active: bool
    created_at: datetime

@dataclass
class Customer:
    customer_id: str
    loyalty_id: str | None
    customer_segment: str
    home_region: str | None
    signup_date: date
    preferred_channel: str | None
    marketing_opt_in: bool
    is_active: bool
    created_at: datetime