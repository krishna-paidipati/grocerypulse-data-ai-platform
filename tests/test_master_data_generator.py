"""Tests for deterministic GroceryPulse master-data generation."""

import pytest

from grocerypulse.generators.master_data import MasterDataGenerator, MasterDataset
from grocerypulse.models.enums import SalesChannel, StoreFormat, SupplierType


def test_generate_suppliers_returns_requested_count() -> None:
    """Generate exactly the requested number of suppliers."""
    generator = MasterDataGenerator(seed=42)

    suppliers = generator.generate_suppliers(10)

    assert len(suppliers) == 10


def test_generate_suppliers_is_deterministic_for_same_seed() -> None:
    """Produce identical supplier datasets when the seed is unchanged."""
    first_generator = MasterDataGenerator(seed=42)
    second_generator = MasterDataGenerator(seed=42)

    first_suppliers = first_generator.generate_suppliers(10)
    second_suppliers = second_generator.generate_suppliers(10)

    assert first_suppliers == second_suppliers


def test_generate_suppliers_changes_with_different_seed() -> None:
    """Produce different supplier data when the seed changes."""
    first_generator = MasterDataGenerator(seed=42)
    second_generator = MasterDataGenerator(seed=43)

    first_suppliers = first_generator.generate_suppliers(10)
    second_suppliers = second_generator.generate_suppliers(10)

    assert first_suppliers != second_suppliers


def test_generate_suppliers_creates_unique_identifiers() -> None:
    """Assign a unique canonical identifier to every generated supplier."""
    generator = MasterDataGenerator(seed=42)

    suppliers = generator.generate_suppliers(50)
    supplier_ids = {supplier.supplier_id for supplier in suppliers}

    assert len(supplier_ids) == len(suppliers)


def test_generate_suppliers_uses_expected_identifier_format() -> None:
    """Generate stable sequential supplier identifiers."""
    generator = MasterDataGenerator(seed=42)

    suppliers = generator.generate_suppliers(3)

    assert [supplier.supplier_id for supplier in suppliers] == [
        "SUP_0001",
        "SUP_0002",
        "SUP_0003",
    ]


def test_generate_suppliers_rejects_negative_count() -> None:
    """Reject requests for an impossible negative record count."""
    generator = MasterDataGenerator(seed=42)

    with pytest.raises(ValueError, match="Supplier count must be non-negative"):
        generator.generate_suppliers(-1)


def test_generate_suppliers_accepts_zero_count() -> None:
    """Return an empty dataset when zero suppliers are requested."""
    generator = MasterDataGenerator(seed=42)

    assert generator.generate_suppliers(0) == []


def test_non_import_suppliers_are_india_based() -> None:
    """Keep local, regional, and national suppliers India-based."""
    generator = MasterDataGenerator(seed=42)

    suppliers = generator.generate_suppliers(100)

    domestic_suppliers = [
        supplier for supplier in suppliers if supplier.supplier_type is not SupplierType.IMPORTER
    ]

    assert domestic_suppliers
    assert all(supplier.country == "India" for supplier in domestic_suppliers)


def test_import_suppliers_are_international() -> None:
    """Assign international countries to generated import suppliers."""
    generator = MasterDataGenerator(seed=42)

    suppliers = generator.generate_suppliers(100)
    import_suppliers = [
        supplier for supplier in suppliers if supplier.supplier_type is SupplierType.IMPORTER
    ]

    assert import_suppliers
    assert all(supplier.country != "India" for supplier in import_suppliers)


def test_supplier_lead_times_follow_supplier_type() -> None:
    """Generate lead times within the configured sourcing ranges."""
    generator = MasterDataGenerator(seed=42)

    suppliers = generator.generate_suppliers(100)

    expected_ranges = {
        SupplierType.LOCAL: (1, 3),
        SupplierType.REGIONAL: (2, 7),
        SupplierType.NATIONAL: (4, 14),
        SupplierType.IMPORTER: (14, 60),
    }

    for supplier in suppliers:
        minimum, maximum = expected_ranges[supplier.supplier_type]
        assert minimum <= supplier.lead_time_days <= maximum


def test_generate_stores_returns_requested_count() -> None:
    """Generate exactly the requested number of stores."""
    generator = MasterDataGenerator(seed=42)

    stores = generator.generate_stores(5)

    assert len(stores) == 5


def test_generate_stores_is_deterministic_for_same_seed() -> None:
    """Produce identical store datasets when the seed is unchanged."""
    first_generator = MasterDataGenerator(seed=42)
    second_generator = MasterDataGenerator(seed=42)

    first_stores = first_generator.generate_stores(5)
    second_stores = second_generator.generate_stores(5)

    assert first_stores == second_stores


def test_generate_stores_changes_with_different_seed() -> None:
    """Produce different store attributes when the seed changes."""
    first_generator = MasterDataGenerator(seed=42)
    second_generator = MasterDataGenerator(seed=43)

    first_stores = first_generator.generate_stores(5)
    second_stores = second_generator.generate_stores(5)

    assert first_stores != second_stores


def test_generate_stores_uses_expected_identifiers() -> None:
    """Generate stable sequential canonical store identifiers."""
    generator = MasterDataGenerator(seed=42)

    stores = generator.generate_stores(3)

    assert [store.store_id for store in stores] == [
        "STORE_0001",
        "STORE_0002",
        "STORE_0003",
    ]


def test_generate_stores_are_bengaluru_karnataka_locations() -> None:
    """Generate stores for the initial Bengaluru operating scenario."""
    generator = MasterDataGenerator(seed=42)

    stores = generator.generate_stores(8)

    assert all(store.city == "Bengaluru" for store in stores)
    assert all(store.region == "Karnataka" for store in stores)


def test_generate_stores_use_supported_retail_formats() -> None:
    """Use physical retail formats selected for the initial scenario."""
    generator = MasterDataGenerator(seed=42)

    stores = generator.generate_stores(8)

    supported_formats = {
        StoreFormat.EXPRESS,
        StoreFormat.SUPERMARKET,
        StoreFormat.SUPERSTORE,
    }

    assert all(store.store_format in supported_formats for store in stores)


def test_generate_stores_have_valid_indian_postcodes() -> None:
    """Generate six-digit postcodes for the Bengaluru scenario."""
    generator = MasterDataGenerator(seed=42)

    stores = generator.generate_stores(8)

    assert all(len(store.postcode) == 6 and store.postcode.isdigit() for store in stores)


def test_generate_stores_rejects_negative_count() -> None:
    """Reject requests for a negative number of stores."""
    generator = MasterDataGenerator(seed=42)

    with pytest.raises(ValueError, match="Store count must be non-negative"):
        generator.generate_stores(-1)


def test_generate_stores_rejects_count_above_configured_locations() -> None:
    """Reject requests exceeding the configured synthetic locations."""
    generator = MasterDataGenerator(seed=42)

    with pytest.raises(ValueError, match="Store count cannot exceed"):
        generator.generate_stores(9)


def test_generate_stores_accepts_zero_count() -> None:
    """Return an empty dataset when zero stores are requested."""
    generator = MasterDataGenerator(seed=42)

    assert generator.generate_stores(0) == []


def test_generate_products_returns_requested_count() -> None:
    """Generate exactly the requested number of products."""
    generator = MasterDataGenerator(seed=42)
    suppliers = generator.generate_suppliers(5)

    products = generator.generate_products(10, suppliers)

    assert len(products) == 10


def test_generate_products_is_deterministic_for_same_seed() -> None:
    """Produce identical product datasets when generation starts identically."""
    first_generator = MasterDataGenerator(seed=42)
    second_generator = MasterDataGenerator(seed=42)

    first_suppliers = first_generator.generate_suppliers(5)
    second_suppliers = second_generator.generate_suppliers(5)

    first_products = first_generator.generate_products(10, first_suppliers)
    second_products = second_generator.generate_products(10, second_suppliers)

    assert first_products == second_products


def test_generate_products_changes_with_different_seed() -> None:
    """Produce different product attributes when the seed changes."""
    first_generator = MasterDataGenerator(seed=42)
    second_generator = MasterDataGenerator(seed=43)

    first_suppliers = first_generator.generate_suppliers(5)
    second_suppliers = second_generator.generate_suppliers(5)

    first_products = first_generator.generate_products(10, first_suppliers)
    second_products = second_generator.generate_products(10, second_suppliers)

    assert first_products != second_products


def test_generate_products_uses_expected_identifiers() -> None:
    """Generate stable product identifiers and SKUs."""
    generator = MasterDataGenerator(seed=42)
    suppliers = generator.generate_suppliers(3)

    products = generator.generate_products(3, suppliers)

    assert [product.product_id for product in products] == [
        "PROD_000001",
        "PROD_000002",
        "PROD_000003",
    ]
    assert [product.sku for product in products] == [
        "SKU_000001",
        "SKU_000002",
        "SKU_000003",
    ]


def test_generate_products_have_unique_identifiers_and_skus() -> None:
    """Keep product primary and business keys unique."""
    generator = MasterDataGenerator(seed=42)
    suppliers = generator.generate_suppliers(5)

    products = generator.generate_products(15, suppliers)

    product_ids = {product.product_id for product in products}
    skus = {product.sku for product in products}

    assert len(product_ids) == len(products)
    assert len(skus) == len(products)


def test_generated_products_reference_existing_suppliers() -> None:
    """Maintain referential integrity between products and suppliers."""
    generator = MasterDataGenerator(seed=42)
    suppliers = generator.generate_suppliers(5)

    products = generator.generate_products(15, suppliers)
    supplier_ids = {supplier.supplier_id for supplier in suppliers}

    assert all(product.supplier_id in supplier_ids for product in products)


def test_generated_products_preserve_standard_margin_rule() -> None:
    """Keep canonical product cost at or below standard selling price."""
    generator = MasterDataGenerator(seed=42)
    suppliers = generator.generate_suppliers(5)

    products = generator.generate_products(15, suppliers)

    assert all(product.cost_price <= product.unit_price for product in products)


def test_generated_perishable_products_have_shelf_life() -> None:
    """Provide shelf-life metadata for every perishable product."""
    generator = MasterDataGenerator(seed=42)
    suppliers = generator.generate_suppliers(5)

    products = generator.generate_products(15, suppliers)
    perishable_products = [product for product in products if product.is_perishable]

    assert perishable_products
    assert all(product.shelf_life_days is not None for product in perishable_products)


def test_generate_products_rejects_negative_count() -> None:
    """Reject requests for a negative number of products."""
    generator = MasterDataGenerator(seed=42)
    suppliers = generator.generate_suppliers(3)

    with pytest.raises(ValueError, match="Product count must be non-negative"):
        generator.generate_products(-1, suppliers)


def test_generate_products_accepts_zero_count_without_suppliers() -> None:
    """Allow an empty product dataset without requiring suppliers."""
    generator = MasterDataGenerator(seed=42)

    assert generator.generate_products(0, []) == []


def test_generate_products_requires_suppliers() -> None:
    """Reject non-empty product generation without supplier master data."""
    generator = MasterDataGenerator(seed=42)

    with pytest.raises(
        ValueError,
        match="Products cannot be generated without suppliers",
    ):
        generator.generate_products(1, [])


def test_generate_products_rejects_count_above_templates() -> None:
    """Reject requests exceeding the configured product catalogue."""
    generator = MasterDataGenerator(seed=42)
    suppliers = generator.generate_suppliers(5)

    with pytest.raises(ValueError, match="Product count cannot exceed"):
        generator.generate_products(16, suppliers)


def test_generate_customers_returns_requested_count() -> None:
    """Generate exactly the requested number of customers."""
    generator = MasterDataGenerator(seed=42)

    customers = generator.generate_customers(25)

    assert len(customers) == 25


def test_generate_customers_is_deterministic_for_same_seed() -> None:
    """Produce identical customer datasets when the seed is unchanged."""
    first_generator = MasterDataGenerator(seed=42)
    second_generator = MasterDataGenerator(seed=42)

    first_customers = first_generator.generate_customers(25)
    second_customers = second_generator.generate_customers(25)

    assert first_customers == second_customers


def test_generate_customers_changes_with_different_seed() -> None:
    """Produce different customer attributes when the seed changes."""
    first_generator = MasterDataGenerator(seed=42)
    second_generator = MasterDataGenerator(seed=43)

    first_customers = first_generator.generate_customers(25)
    second_customers = second_generator.generate_customers(25)

    assert first_customers != second_customers


def test_generate_customers_uses_expected_identifiers() -> None:
    """Generate stable sequential canonical customer identifiers."""
    generator = MasterDataGenerator(seed=42)

    customers = generator.generate_customers(3)

    assert [customer.customer_id for customer in customers] == [
        "CUST_000001",
        "CUST_000002",
        "CUST_000003",
    ]


def test_generate_customers_have_unique_identifiers() -> None:
    """Keep generated customer primary keys unique."""
    generator = MasterDataGenerator(seed=42)

    customers = generator.generate_customers(100)
    customer_ids = {customer.customer_id for customer in customers}

    assert len(customer_ids) == len(customers)


def test_generated_loyalty_identifiers_are_unique() -> None:
    """Keep populated loyalty identifiers unique."""
    generator = MasterDataGenerator(seed=42)

    customers = generator.generate_customers(100)
    loyalty_ids = [customer.loyalty_id for customer in customers if customer.loyalty_id is not None]

    assert len(loyalty_ids) == len(set(loyalty_ids))


def test_generated_customers_include_loyalty_and_non_loyalty_members() -> None:
    """Represent both loyalty members and customers without loyalty membership."""
    generator = MasterDataGenerator(seed=42)

    customers = generator.generate_customers(100)

    assert any(customer.loyalty_id is not None for customer in customers)
    assert any(customer.loyalty_id is None for customer in customers)


def test_generated_customers_use_configured_india_regions() -> None:
    """Keep customer home regions within the initial India scenario."""
    generator = MasterDataGenerator(seed=42)

    customers = generator.generate_customers(100)

    expected_regions = {
        "Karnataka",
        "Tamil Nadu",
        "Andhra Pradesh",
        "Telangana",
        "Kerala",
        "Maharashtra",
    }

    assert all(customer.home_region in expected_regions for customer in customers)


def test_generated_customers_have_supported_preferred_channels() -> None:
    """Use channels supported by the current canonical contract."""
    generator = MasterDataGenerator(seed=42)

    customers = generator.generate_customers(100)

    assert all(
        customer.preferred_channel
        in {
            SalesChannel.STORE,
            SalesChannel.WEB,
            SalesChannel.APP,
        }
        for customer in customers
    )


def test_generated_customer_signup_dates_are_not_future_dates() -> None:
    """Keep generated signup dates valid under the canonical contract."""
    generator = MasterDataGenerator(seed=42)

    customers = generator.generate_customers(100)

    assert all(customer.signup_date.year <= 2025 for customer in customers)


def test_generate_customers_rejects_negative_count() -> None:
    """Reject requests for a negative number of customers."""
    generator = MasterDataGenerator(seed=42)

    with pytest.raises(ValueError, match="Customer count must be non-negative"):
        generator.generate_customers(-1)


def test_generate_customers_accepts_zero_count() -> None:
    """Return an empty dataset when zero customers are requested."""
    generator = MasterDataGenerator(seed=42)

    assert generator.generate_customers(0) == []


def test_generate_dataset_returns_master_dataset() -> None:
    """Return the aggregate master-data container."""
    generator = MasterDataGenerator(seed=42)

    dataset = generator.generate_dataset(
        supplier_count=5,
        store_count=4,
        product_count=10,
        customer_count=25,
    )

    assert isinstance(dataset, MasterDataset)


def test_generate_dataset_returns_requested_entity_counts() -> None:
    """Generate the requested number of records for every master entity."""
    generator = MasterDataGenerator(seed=42)

    dataset = generator.generate_dataset(
        supplier_count=5,
        store_count=4,
        product_count=10,
        customer_count=25,
    )

    assert len(dataset.suppliers) == 5
    assert len(dataset.stores) == 4
    assert len(dataset.products) == 10
    assert len(dataset.customers) == 25


def test_generate_dataset_is_deterministic_for_same_seed() -> None:
    """Produce identical complete datasets from the same seed and counts."""
    first_generator = MasterDataGenerator(seed=42)
    second_generator = MasterDataGenerator(seed=42)

    first_dataset = first_generator.generate_dataset(
        supplier_count=5,
        store_count=4,
        product_count=10,
        customer_count=25,
    )
    second_dataset = second_generator.generate_dataset(
        supplier_count=5,
        store_count=4,
        product_count=10,
        customer_count=25,
    )

    assert first_dataset == second_dataset


def test_generate_dataset_changes_with_different_seed() -> None:
    """Produce different complete datasets when the seed changes."""
    first_generator = MasterDataGenerator(seed=42)
    second_generator = MasterDataGenerator(seed=43)

    first_dataset = first_generator.generate_dataset(
        supplier_count=5,
        store_count=4,
        product_count=10,
        customer_count=25,
    )
    second_dataset = second_generator.generate_dataset(
        supplier_count=5,
        store_count=4,
        product_count=10,
        customer_count=25,
    )

    assert first_dataset != second_dataset


def test_generate_dataset_preserves_product_supplier_integrity() -> None:
    """Keep every generated product linked to an existing supplier."""
    generator = MasterDataGenerator(seed=42)

    dataset = generator.generate_dataset(
        supplier_count=5,
        store_count=4,
        product_count=10,
        customer_count=25,
    )

    supplier_ids = {supplier.supplier_id for supplier in dataset.suppliers}

    assert all(product.supplier_id in supplier_ids for product in dataset.products)


def test_generate_dataset_accepts_zero_counts() -> None:
    """Allow generation of a completely empty master dataset."""
    generator = MasterDataGenerator(seed=42)

    dataset = generator.generate_dataset(
        supplier_count=0,
        store_count=0,
        product_count=0,
        customer_count=0,
    )

    assert dataset.suppliers == []
    assert dataset.stores == []
    assert dataset.products == []
    assert dataset.customers == []


def test_generate_dataset_requires_suppliers_when_products_requested() -> None:
    """Reject datasets containing products without supplier master data."""
    generator = MasterDataGenerator(seed=42)

    with pytest.raises(
        ValueError,
        match="Products cannot be generated without suppliers",
    ):
        generator.generate_dataset(
            supplier_count=0,
            store_count=4,
            product_count=1,
            customer_count=25,
        )
