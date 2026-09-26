"""Generate deterministic synthetic master data for GroceryPulse.

Code Owner:
    Vijay Krishna Paidipati

Component:
    GroceryPulse Synthetic Data Generation

Purpose:
    Provide deterministic generation of synthetic grocery retail master data
    that conforms to the canonical GroceryPulse domain contracts.

Developer Notes:
    Randomness is isolated within each generator instance by using a dedicated
    random.Random object. Supplying the same seed allows generated datasets to
    be reproduced for testing, debugging, and development.
"""

import random
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal

from grocerypulse.models.entities import Customer, Product, Store, Supplier
from grocerypulse.models.enums import (
    CustomerSegment,
    ProductCategory,
    SalesChannel,
    StoreFormat,
    SupplierType,
    UnitMeasure,
)

_SUPPLIER_NAMES = (
    "Nandi Fresh Produce",
    "Deccan Harvest Foods",
    "Malnad Coffee Traders",
    "Kaveri Dairy Supplies",
    "Bengaluru Artisan Foods",
    "Nilgiri Fresh Farms",
    "Godavari Agro Foods",
    "Western Ghats Organics",
    "Himalayan Specialty Foods",
    "Bharat Grocery Distributors",
    "Dutch Floral Exports",
    "Thai Tropical Foods",
    "Swargam Organic FoodsKenya Fresh Exports",
    "Vietnam Specialty Foods",
)

_STORE_LOCATIONS = (
    ("Jakkur", "Bengaluru", "Karnataka", "560064", "13.0785", "77.6068"),
    ("Yelahanka", "Bengaluru", "Karnataka", "560064", "13.1007", "77.5963"),
    ("Hebbal", "Bengaluru", "Karnataka", "560024", "13.0358", "77.5970"),
    ("Whitefield", "Bengaluru", "Karnataka", "560066", "12.9698", "77.7500"),
    ("Indiranagar", "Bengaluru", "Karnataka", "560038", "12.9784", "77.6408"),
    ("Jayanagar", "Bengaluru", "Karnataka", "560041", "12.9250", "77.5938"),
    ("Koramangala", "Bengaluru", "Karnataka", "560034", "12.9352", "77.6245"),
    ("Electronic City", "Bengaluru", "Karnataka", "560100", "12.8452", "77.6602"),
)

_PRODUCT_TEMPLATES = (
    ("Tender Coconut", ProductCategory.PRODUCE, "Coconut", UnitMeasure.EACH, True, 7),
    ("Banana", ProductCategory.PRODUCE, "Fresh Fruit", UnitMeasure.KG, True, 5),
    ("Apple", ProductCategory.PRODUCE, "Fresh Fruit", UnitMeasure.KG, True, 21),
    ("Mango", ProductCategory.PRODUCE, "Fresh Fruit", UnitMeasure.KG, True, 7),
    ("Tomato", ProductCategory.PRODUCE, "Vegetables", UnitMeasure.KG, True, 7),
    ("Potato", ProductCategory.PRODUCE, "Vegetables", UnitMeasure.KG, True, 30),
    ("Fresh Milk", ProductCategory.DAIRY, "Milk", UnitMeasure.L, True, 5),
    ("Greek Yogurt", ProductCategory.DAIRY, "Yogurt", UnitMeasure.G, True, 14),
    ("Sourdough Bread", ProductCategory.BAKERY, "Bread", UnitMeasure.EACH, True, 3),
    ("Chocolate Cookies", ProductCategory.BAKERY, "Cookies", UnitMeasure.G, True, 30),
    ("Arabica Coffee Beans", ProductCategory.BEVERAGES, "Coffee", UnitMeasure.G, False, 180),
    ("Cold Pressed Juice", ProductCategory.BEVERAGES, "Juice", UnitMeasure.ML, True, 5),
    ("Basmati Rice", ProductCategory.GROCERY, "Rice", UnitMeasure.KG, False, 365),
    ("Toor Dal", ProductCategory.GROCERY, "Pulses", UnitMeasure.KG, False, 365),
    ("Extra Virgin Olive Oil", ProductCategory.GROCERY, "Cooking Oil", UnitMeasure.L, False, 365),
)

_DOMESTIC_COUNTRIES = ("India",)

_INTERNATIONAL_COUNTRIES = (
    "Netherlands",
    "Spain",
    "Italy",
    "Thailand",
    "Kenya",
    "Vietnam",
)

_CUSTOMER_REGIONS = (
    "Karnataka",
    "Tamil Nadu",
    "Andhra Pradesh",
    "Telangana",
    "Kerala",
    "Maharashtra",
)

_CUSTOMER_SEGMENTS = (
    CustomerSegment.VALUE,
    CustomerSegment.FAMILY,
    CustomerSegment.PREMIUM,
    CustomerSegment.CONVENIENCE,
    CustomerSegment.OTHER,
)

_CUSTOMER_CHANNELS = (
    SalesChannel.STORE,
    SalesChannel.WEB,
    SalesChannel.APP,
)


@dataclass(frozen=True)
class MasterDataset:
    """Container for a generated GroceryPulse master-data dataset.

    Attributes:
        suppliers: Generated supplier master records.
        stores: Generated store master records.
        products: Generated product master records.
        customers: Generated customer master records.
    """

    suppliers: list[Supplier]
    stores: list[Store]
    products: list[Product]
    customers: list[Customer]


class MasterDataGenerator:
    """Generate deterministic synthetic GroceryPulse master data.

    Each generator instance owns an independent pseudo-random number generator.
    This avoids dependence on Python's module-level random state and makes the
    generated data reproducible when the same seed is supplied.

    Args:
        seed: Seed used to initialise the pseudo-random number generator.
    """

    def __init__(self, seed: int) -> None:
        """Initialise the master-data generator.

        Args:
            seed: Seed controlling the deterministic pseudo-random sequence.
        """
        # A deterministic PRNG is intentional here because synthetic datasets must be
        # reproducible. This generator must never be used for security-sensitive values.
        self._rng = random.Random(seed)  # noqa: S311

    def generate_suppliers(self, count: int) -> list[Supplier]:
        """Generate deterministic synthetic suppliers.

        The generated supplier population is India-first while retaining
        international sourcing capability. Supplier records are validated through
        the canonical Supplier contract before being returned.

        Args:
            count: Number of supplier records to generate.

        Returns:
            Validated synthetic suppliers.

        Raises:
            ValueError: If count is negative.
        """
        if count < 0:
            raise ValueError("Supplier count must be non-negative")

        suppliers: list[Supplier] = []

        for index in range(1, count + 1):
            supplier_type = self._rng.choices(
                population=tuple(SupplierType),
                weights=(35, 30, 25, 10),
                k=1,
            )[0]

            country = (
                self._rng.choice(_INTERNATIONAL_COUNTRIES)
                if supplier_type is SupplierType.IMPORTER
                else self._rng.choice(_DOMESTIC_COUNTRIES)
            )

            supplier = Supplier(
                supplier_id=f"SUP_{index:04d}",
                supplier_name=self._supplier_name(index),
                supplier_type=supplier_type,
                country=country,
                lead_time_days=self._supplier_lead_time(supplier_type),
                min_order_qty=self._rng.randint(10, 500),
                reliability_score=Decimal(str(round(self._rng.uniform(0.75, 0.99), 3))),
                is_active=True,
                created_at=datetime(2026, 1, 1, tzinfo=UTC),
            )
            suppliers.append(supplier)

        return suppliers

    def _supplier_name(self, index: int) -> str:
        """Return a deterministic synthetic supplier name."""
        base_name = _SUPPLIER_NAMES[(index - 1) % len(_SUPPLIER_NAMES)]
        return f"{base_name} {index:04d}"

    def _supplier_lead_time(self, supplier_type: SupplierType) -> int:
        """Generate a realistic lead time for a supplier type."""
        lead_time_ranges = {
            SupplierType.LOCAL: (1, 3),
            SupplierType.REGIONAL: (2, 7),
            SupplierType.NATIONAL: (4, 14),
            SupplierType.IMPORTER: (14, 60),
        }

        minimum, maximum = lead_time_ranges[supplier_type]
        return self._rng.randint(minimum, maximum)

    def generate_stores(self, count: int) -> list[Store]:
        """Generate deterministic synthetic GroceryPulse stores in Bengaluru.

        Args:
            count: Number of store records to generate.

        Returns:
            Validated synthetic Store instances.

        Raises:
            ValueError: If count is negative or exceeds available locations.
        """
        if count < 0:
            raise ValueError("Store count must be non-negative")

        if count > len(_STORE_LOCATIONS):
            raise ValueError(
                f"Store count cannot exceed {len(_STORE_LOCATIONS)} configured locations"
            )

        stores: list[Store] = []

        for index, location in enumerate(_STORE_LOCATIONS[:count], start=1):
            locality, city, region, postcode, latitude, longitude = location

            store = Store(
                store_id=f"STORE_{index:04d}",
                store_name=f"GroceryPulse {locality}",
                store_format=self._rng.choice(
                    (
                        StoreFormat.EXPRESS,
                        StoreFormat.SUPERMARKET,
                        StoreFormat.SUPERSTORE,
                    )
                ),
                region=region,
                city=city,
                postcode=postcode,
                latitude=Decimal(latitude),
                longitude=Decimal(longitude),
                open_date=datetime(2024, 1, 1, tzinfo=UTC).date(),
                floor_area_sqm=self._rng.randint(150, 2_500),
                is_active=True,
                created_at=datetime(2026, 1, 1, tzinfo=UTC),
            )
            stores.append(store)

        return stores

    def generate_products(
        self,
        count: int,
        suppliers: list[Supplier],
    ) -> list[Product]:
        """Generate deterministic synthetic products linked to suppliers.

        Args:
            count: Number of product records to generate.
            suppliers: Validated suppliers available for product assignment.

        Returns:
            Validated synthetic Product instances.

        Raises:
            ValueError: If count is negative, suppliers are unavailable, or the
                requested count exceeds the configured product templates.
        """
        if count < 0:
            raise ValueError("Product count must be non-negative")

        if count == 0:
            return []

        if not suppliers:
            raise ValueError("Products cannot be generated without suppliers")

        if count > len(_PRODUCT_TEMPLATES):
            raise ValueError(
                f"Product count cannot exceed {len(_PRODUCT_TEMPLATES)} configured templates"
            )

        products: list[Product] = []

        for index, template in enumerate(_PRODUCT_TEMPLATES[:count], start=1):
            (
                product_name,
                category,
                subcategory,
                unit_measure,
                is_perishable,
                shelf_life_days,
            ) = template

            cost_price = Decimal(self._rng.randint(20, 1_000))
            margin_percentage = Decimal(self._rng.randint(15, 45)) / Decimal("100")
            unit_price = (cost_price * (Decimal("1") + margin_percentage)).quantize(Decimal("0.01"))

            supplier = self._rng.choice(suppliers)

            product = Product(
                product_id=f"PROD_{index:06d}",
                sku=f"SKU_{index:06d}",
                product_name=product_name,
                brand=None,
                category=category,
                subcategory=subcategory,
                unit_size=Decimal("1"),
                unit_measure=unit_measure,
                unit_price=unit_price,
                cost_price=cost_price,
                vat_rate=Decimal("0"),
                shelf_life_days=shelf_life_days,
                is_perishable=is_perishable,
                supplier_id=supplier.supplier_id,
                is_active=True,
                created_at=datetime(2026, 1, 1, tzinfo=UTC),
            )
            products.append(product)

        return products

    def generate_customers(self, count: int) -> list[Customer]:
        """Generate deterministic synthetic customers for the India scenario.

        Args:
            count: Number of customer records to generate.

        Returns:
            Validated synthetic Customer instances.

        Raises:
            ValueError: If count is negative.
        """
        if count < 0:
            raise ValueError("Customer count must be non-negative")

        customers: list[Customer] = []

        for index in range(1, count + 1):
            # Some customers shop anonymously and have no loyalty account.
            has_loyalty = self._rng.random() < 0.65

            customer = Customer(
                customer_id=f"CUST_{index:06d}",
                loyalty_id=f"LOY_{index:06d}" if has_loyalty else None,
                customer_segment=self._rng.choice(_CUSTOMER_SEGMENTS),
                home_region=self._rng.choice(_CUSTOMER_REGIONS),
                signup_date=datetime(
                    self._rng.randint(2020, 2025),
                    self._rng.randint(1, 12),
                    self._rng.randint(1, 28),
                    tzinfo=UTC,
                ).date(),
                preferred_channel=self._rng.choice(_CUSTOMER_CHANNELS),
                marketing_opt_in=self._rng.random() < 0.40,
                is_active=True,
                created_at=datetime(2026, 1, 1, tzinfo=UTC),
            )

            customers.append(customer)

        return customers

    def generate_dataset(
        self,
        *,
        supplier_count: int,
        store_count: int,
        product_count: int,
        customer_count: int,
    ) -> MasterDataset:
        """Generate a complete deterministic GroceryPulse master dataset.

        Args:
            supplier_count: Number of suppliers to generate.
            store_count: Number of stores to generate.
            product_count: Number of products to generate.
            customer_count: Number of customers to generate.

        Returns:
            A complete validated GroceryPulse master dataset.

        Raises:
            ValueError: If an entity generator receives an invalid count or
                products are requested without suppliers.
        """
        suppliers = self.generate_suppliers(supplier_count)
        stores = self.generate_stores(store_count)
        products = self.generate_products(product_count, suppliers)
        customers = self.generate_customers(customer_count)

        return MasterDataset(
            suppliers=suppliers,
            stores=stores,
            products=products,
            customers=customers,
        )
