# GroceryPulse Retail Domain Model

## Purpose

This document defines the initial business entities and data grain used by the GroceryPulse synthetic retail platform.

The domain model will evolve as the project introduces transactional sales, inventory, promotions, supplier deliveries, streaming events, analytics, and ML workloads.

## Store

**Grain:** One row per physical or fulfilment store/location.

### Primary key

`store_id`

### Core attributes

* `store_id`
* `store_name`
* `store_format`
* `region`
* `city`
* `postcode`
* `latitude`
* `longitude`
* `open_date`
* `floor_area_sqm`
* `is_active`
* `created_at`

## Product

**Grain:** One row per sellable SKU.

### Primary key

`product_id`

### Business identifier

`sku`

### Core attributes

* `product_id`
* `sku`
* `product_name`
* `brand`
* `category`
* `subcategory`
* `unit_size`
* `unit_measure`
* `unit_price`
* `cost_price`
* `vat_rate`
* `shelf_life_days`
* `is_perishable`
* `supplier_id`
* `is_active`
* `created_at`

## Customer

**Grain:** One row per registered customer.

### Primary key

`customer_id`

### Core attributes

* `customer_id`
* `loyalty_id`
* `customer_segment`
* `home_region`
* `signup_date`
* `preferred_channel`
* `marketing_opt_in`
* `is_active`
* `created_at`

Customer identity is optional on future sales transactions because anonymous and non-loyalty purchases must be supported.

## Supplier

**Grain:** One row per supplier organisation.

### Primary key

`supplier_id`

### Core attributes

* `supplier_id`
* `supplier_name`
* `supplier_type`
* `country`
* `lead_time_days`
* `minimum_order_qty`
* `reliability_score`
* `is_active`
* `created_at`

## Initial relationships

* One supplier may supply many products.
* One store may process many transactions.
* One customer may make many transactions.
* One transaction may contain many transaction items.
* One product may appear in many transaction items.
* Inventory will later relate stores and products.

## Design principles

The project defines the grain of every dataset explicitly before implementation.

Stable surrogate identifiers are used as primary keys rather than relying on names.

Personally identifiable customer information is deliberately minimised because GroceryPulse uses synthetic data and does not require realistic personal details to demonstrate the engineering architecture.

The initial product-to-supplier relationship assumes a default supplier for simplicity. This may later evolve into a many-to-many relationship as supply-chain modelling becomes more sophisticated.
