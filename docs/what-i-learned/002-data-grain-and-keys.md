# Data Grain and Keys

Understanding data grain and keys is fundamental to building reliable Data Engineering pipelines and analytical models.

## What is data grain?

The **grain** of a dataset defines exactly what one row represents.

Before designing a table, pipeline, transformation, or analytical model, I should be able to complete this sentence:

> One row represents...

For example, in GroceryPulse:

```text
transactions
One row = one customer checkout transaction

transaction_items
One row = one product line within a transaction
```

These tables represent different grains.

A transaction may contain several items.

Example:

```text
transactions

transaction_id    total_amount
TXN_001           6.76
```

The corresponding transaction items could be:

```text
transaction_id    line_number    product       line_amount
TXN_001           1              Milk          2.00
TXN_001           2              Bread         1.50
TXN_001           3              Coffee        3.26
```

The transaction table contains one row.

The item table contains three rows.

Understanding that difference is essential before joining or aggregating the datasets.

## What is a primary key?

A **primary key** uniquely identifies a row within a dataset.

For example:

```text
STORE_0001
STORE_0002
STORE_0003
```

could be values of:

```text
store_id
```

in the Store dataset.

Each value must uniquely identify one store.

Similarly:

```text
supplier_id
product_id
customer_id
transaction_id
```

can act as primary keys for their respective entities.

A good primary key helps provide:

- uniqueness,
- stable identification,
- reliable joins,
- referential integrity,
- and predictable downstream processing.

## What is a foreign key?

A **foreign key** connects one dataset to another.

For example, a Product may contain:

```text
supplier_id
```

That value references the supplier represented in the Supplier dataset.

Conceptually:

```text
Supplier
--------
supplier_id  PK
     ^
     |
     |
Product
-------
product_id   PK
supplier_id  FK
```

This relationship allows GroceryPulse to determine which supplier is associated with a product.

Foreign-key integrity means a referenced value should actually exist in the parent dataset.

For example, this would be invalid:

```text
Product.supplier_id = SUP_9999
```

if `SUP_9999` does not exist in the Supplier dataset.

## What is a composite key?

Sometimes one field is not enough to uniquely identify a row.

Consider transaction items:

```text
transaction_id    line_number
TXN_001           1
TXN_001           2
TXN_001           3
TXN_002           1
```

`transaction_id` alone is not unique because a transaction contains multiple lines.

`line_number` alone is also not unique because every transaction may have line 1.

Together:

```text
(transaction_id, line_number)
```

uniquely identify a transaction item.

That combination is a **composite key**.

## Why can joining datasets at different grains cause double counting?

This is one of the most important analytical risks when joining datasets.

Suppose the transaction header contains:

```text
transaction_id    total_amount
TXN_001           6.76
```

and the transaction contains three item rows.

If the header is joined directly to the item table:

```text
transaction_id    line_number    total_amount
TXN_001           1              6.76
TXN_001           2              6.76
TXN_001           3              6.76
```

then:

```text
SUM(total_amount)
```

would produce:

```text
20.28
```

instead of:

```text
6.76
```

The original transaction value has been repeated once for every matching item.

This is sometimes called **fan-out**.

The join itself may be technically valid while the resulting aggregation is analytically wrong.

## Grain before joins

Before joining two datasets, I should ask:

```text
What does one row represent on the left?
What does one row represent on the right?
What is the relationship between them?
What will happen to row counts after the join?
Which measures are safe to aggregate afterward?
```

For example:

```text
Transaction       1
                   \
                    ---- many TransactionItems
```

This is a one-to-many relationship.

Measures stored at transaction grain should not automatically be summed after expanding the transaction into item grain.

## OLTP versus analytical modelling

Operational systems often store normalized entities optimized for transactional consistency.

Analytical systems commonly reorganize data into structures optimized for reporting and aggregation.

A future GroceryPulse analytical model may resemble:

```text
             dim_customer
                  |
                  |
dim_store ---- fct_sales ---- dim_product
                  |
                  |
             dim_date
```

The grain of `fct_sales` must be explicitly defined.

For example:

```text
One row = one product line sold in one transaction.
```

Once that grain is defined, measures and dimensions can be designed around it.

## GroceryPulse examples

Current canonical master entities have clear grains:

```text
Store
One row/model instance = one retail or fulfilment location

Supplier
One row/model instance = one supplier

Product
One row/model instance = one sellable SKU

Customer
One row/model instance = one customer
```

Future transactional datasets will have their own grains.

Examples could include:

```text
SalesTransaction
One row = one completed transaction

SalesLine
One row = one product line within a transaction

InventoryMovement
One row = one inventory movement event

StockSnapshot
One row = inventory state for a product/location/time combination

WasteRecord
One row = one recorded waste event
```

The exact grain should be documented before implementing each dataset.

## Initial mistake / learning point

A common beginner mistake is to focus first on columns:

```text
What fields should this table contain?
```

The better first question is:

```text
What exactly does one row represent?
```

Once the grain is clear, decisions about:

- keys,
- relationships,
- measures,
- joins,
- deduplication,
- and aggregation

become much easier.

## Production consideration

Grain errors can propagate silently through a data platform.

A pipeline may:

```text
ingest successfully
        |
        v
validate successfully
        |
        v
join successfully
        |
        v
load successfully
        |
        v
produce the wrong business metric
```

This is why technical success does not automatically imply analytical correctness.

Production systems should therefore test important assumptions such as:

- uniqueness at the declared grain,
- primary-key integrity,
- foreign-key integrity,
- expected row-count changes,
- duplicate detection,
- and aggregation reconciliation.

These checks will become increasingly important when GroceryPulse introduces dbt tests and data-quality monitoring.

## Interview questions

### What is data grain?

Data grain defines what one row in a dataset represents.

### Why should grain be defined before designing a table?

Because keys, joins, measures, deduplication rules, and aggregation behaviour all depend on the row-level meaning of the dataset.

### What is the difference between a primary key and a foreign key?

A primary key uniquely identifies a row in its own dataset. A foreign key references a key in another dataset and establishes a relationship between them.

### What is a composite key?

A composite key uses multiple columns together to uniquely identify a row.

### Why can a one-to-many join cause double counting?

Values from the one-side may be repeated for every matching row on the many-side. Aggregating those repeated values without accounting for the grain can overstate metrics.

### How would you protect against grain-related errors?

I would explicitly document dataset grain, enforce key uniqueness, test referential integrity, validate expected join cardinality, monitor row counts, and reconcile important business measures.

## Key takeaway

Before creating or joining any dataset, define:

```text
GRAIN
  ↓
KEYS
  ↓
RELATIONSHIPS
  ↓
MEASURES
  ↓
JOINS
  ↓
AGGREGATIONS
```

If the grain is wrong or unclear, everything built on top of it is at risk.
