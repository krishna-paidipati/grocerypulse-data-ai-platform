# Data Contracts and Validation

GroceryPulse uses explicit data contracts to define what valid core retail data looks like before that data enters trusted parts of the platform.

The initial canonical master entities are:

```text
Store
Supplier
Product
Customer
```

These contracts are implemented using Pydantic models.

## What is a data contract?

A **data contract** defines the structure and rules that data must satisfy.

A contract can specify:

```text
field names
data types
required fields
optional fields
identifier formats
numeric ranges
allowed values
cross-field business rules
```

For example, a Product contract can require:

```text
product_id       -> valid GroceryPulse product ID
sku              -> valid SKU
unit_price       -> non-negative decimal
cost_price       -> non-negative decimal
supplier_id      -> valid supplier identifier format
is_perishable    -> boolean
shelf_life_days  -> required when product is perishable
```

This makes the expected structure explicit rather than relying on assumptions made independently by different producers and consumers.

## Why are data contracts important?

Without contracts, different parts of a platform may interpret the same data differently.

For example:

```text
Producer A
store_id = "123"

Producer B
store_id = "STORE-123"

Producer C
store_id = 123
```

All three may conceptually refer to a store, but they do not follow the same representation.

A canonical contract establishes one agreed representation.

Conceptually:

```text
Producer
   |
   v
Canonical Contract
   |
   +----> Storage
   +----> Transformation
   +----> API
   +----> Analytics
   +----> ML
```

This reduces ambiguity between systems.

## GroceryPulse base model

The GroceryPulse canonical models inherit shared behaviour from a common base model.

The base configuration includes behaviour such as:

```python
ConfigDict(
    extra="forbid",
    str_strip_whitespace=True,
    validate_assignment=True,
)
```

These settings establish common contract behaviour across entities.

## Why are enums useful?

Enums define a controlled set of valid values.

For example, GroceryPulse uses controlled values for concepts such as:

```text
StoreFormat
CustomerSegment
SalesChannel
SupplierType
UnitMeasure
ProductCategory
```

Without an enum, equivalent concepts might appear as:

```text
supermarket
SuperMarket
SUPERMARKET
super_market
Super Market
```

That creates unnecessary inconsistency.

With a controlled vocabulary:

```text
SUPERMARKET
```

becomes the agreed representation.

Enums improve:

- consistency,
- validation,
- discoverability,
- downstream transformations,
- analytical grouping,
- and interoperability.

## What is field-level validation?

Field-level validation checks an individual field independently.

Examples include:

```text
latitude must be between -90 and 90
longitude must be between -180 and 180
reliability_score must be between 0 and 1
price cannot be negative
identifier must match an expected pattern
```

Pydantic fields can express many of these constraints declaratively.

For example:

```python
latitude: Decimal = Field(
    ge=-90,
    le=90,
)
```

The contract itself documents and enforces the allowed range.

## Custom field validation

Some rules require application-specific validation.

For example, a store opening date should not be in the future.

Conceptually:

```python
@field_validator("open_date")
@classmethod
def open_date_cannot_be_future(cls, value: date) -> date:
    if value > datetime.now(UTC).date():
        raise ValueError("Open date cannot be in the future")
    return value
```

The same principle applies to customer signup dates.

The purpose is to reject logically invalid values at the contract boundary.

## What is cross-field validation?

Some business rules depend on multiple fields.

These cannot always be validated correctly by examining one field in isolation.

For example:

```text
is_perishable = True
```

has implications for:

```text
shelf_life_days
```

A GroceryPulse rule requires perishable products to define a shelf life.

Conceptually:

```python
if self.is_perishable and self.shelf_life_days is None:
    raise ValueError(...)
```

Another cross-field rule protects the canonical product price relationship:

```text
cost_price <= unit_price
```

The canonical Product model therefore rejects a standard product definition where cost exceeds its standard selling price.

Promotional pricing and intentional loss-leader behaviour can later be represented in separate promotional or transactional datasets rather than weakening the canonical standard-price rule.

## Why should unexpected fields sometimes be rejected?

GroceryPulse configures canonical contracts to reject unexpected fields.

Conceptually:

```python
extra = "forbid"
```

Suppose a producer sends:

```json
{
  "product_id": "PROD_000001",
  "sku": "SKU_000001",
  "unexpected_field": "something"
}
```

Silently accepting the additional field could hide:

- producer mistakes,
- misspelled field names,
- uncoordinated schema changes,
- incompatible versions,
- or misunderstood data.

Rejecting unexpected fields makes contract violations visible.

This follows a fail-fast principle:

```text
bad producer data
       |
       v
validation failure
       X
trusted dataset
```

rather than:

```text
bad producer data
       |
       v
silently accepted
       |
       v
trusted dataset
       |
       v
downstream failure or incorrect analytics
```

## Why should bad records be rejected before reaching trusted datasets?

The further invalid data travels through a platform, the more expensive it becomes to diagnose and correct.

A simplified platform might eventually look like:

```text
Source
  |
  v
Kafka / Batch ingestion
  |
  v
S3 Bronze
  |
  v
Validation
  |
  v
S3 Silver
  |
  v
Snowflake
  |
  v
dbt
  |
  v
BI / ML / GenAI
```

Data that violates an agreed contract should be identified as early as practical.

Otherwise bad data can contaminate:

- transformations,
- aggregates,
- dashboards,
- machine-learning features,
- forecasts,
- alerts,
- and AI-generated operational recommendations.

Validation is therefore not simply a Python concern.

It is a data-platform reliability concern.

## Validation at generation boundaries

Synthetic data should also obey the same contracts as production-style data.

GroceryPulse generators construct canonical Pydantic entities rather than producing arbitrary dictionaries and assuming they are valid.

Conceptually:

```text
Synthetic Generator
        |
        v
Canonical Pydantic Model
        |
        v
Validated Entity
        |
        v
Export / downstream processing
```

This means the synthetic generator cannot casually bypass important domain constraints.

That principle becomes especially important as GroceryPulse introduces more complicated synthetic datasets.

## What is JSON Schema?

JSON Schema is a machine-readable representation of the expected structure and constraints of JSON-compatible data.

Pydantic models can generate JSON Schema from the canonical Python contracts.

GroceryPulse exports schemas for entities such as:

```text
Store
Product
Customer
Supplier
```

This is useful because the Python model can act as a source from which other representations are generated.

Conceptually:

```text
Pydantic canonical model
          |
          v
      JSON Schema
          |
    +-----+-----+
    |           |
    v           v
documentation  integration
```

## Why generate schemas instead of maintaining them manually?

If Python models and JSON Schema files are edited independently, they can drift apart.

For example:

```text
Python model says:
field required

JSON Schema says:
field optional
```

Now there are two conflicting definitions of the contract.

Generating JSON Schema from the canonical model reduces this risk.

GroceryPulse also verifies schema generation in the engineering workflow so unintended schema drift can be detected.

## How could the same canonical schema later help Kafka, APIs and Snowflake?

The canonical model provides a common semantic definition that can inform multiple platform components.

Conceptually:

```text
                    Canonical Model
                          |
          +---------------+---------------+
          |               |               |
          v               v               v
      JSON Schema       API models     Validation
          |
          +-------------------------------+
          |                               |
          v                               v
     event contracts                 ingestion rules
          |                               |
          v                               v
        Kafka                         data platform
                                          |
                                          v
                                      Snowflake
```

This does not mean every technology must use an identical physical schema.

Different systems have different storage and execution requirements.

Instead, the canonical contract provides a consistent business definition from which technology-specific representations can evolve.

## Contract versus physical storage model

A canonical data contract and a database table are related but are not necessarily the same thing.

For example:

```text
Canonical Product
       |
       +--> JSON representation
       +--> Kafka event representation
       +--> API representation
       +--> Snowflake table
       +--> dbt staging model
       +--> ML feature input
```

Each physical implementation may contain technical metadata or storage-specific fields.

The important objective is that the underlying business semantics remain consistent.

## Schema evolution

Changing a canonical contract can affect many consumers.

For example, changing:

```text
supplier_id
```

or changing the meaning of:

```text
unit_price
```

could affect:

- generated data,
- tests,
- JSON Schema,
- ingestion pipelines,
- Kafka producers and consumers,
- Snowflake tables,
- dbt models,
- APIs,
- ML features,
- and documentation.

Canonical model changes should therefore be treated as **schema evolution**, not casual refactoring.

## Initial mistake / learning point

It is tempting to think of a model as simply a Python class containing fields.

A production-style data contract has a broader responsibility.

It communicates:

```text
what the data means
what shape it has
which values are allowed
which business rules must hold
how downstream systems can depend on it
```

The important learning is that validation belongs close to the boundary where data enters a trusted domain.

## Production consideration

As GroceryPulse evolves, contract management will need to address:

- backward compatibility,
- schema versioning,
- nullable versus required fields,
- producer/consumer compatibility,
- controlled vocabulary evolution,
- event schema evolution,
- database migration,
- and data-quality monitoring.

For example, the current Product model associates a product with one supplier.

A more mature procurement model may introduce a relationship such as:

```text
Supplier
    |
    v
SupplierProduct
    |
    v
Product
```

That would allow supplier-specific properties such as:

```text
purchase price
lead time
minimum order quantity
supplier SKU
currency
```

without overloading the canonical Product entity.

Such a change should be introduced intentionally as domain evolution.

## Interview questions

### What is a data contract?

A data contract is an explicit agreement describing the structure, types, constraints, semantics, and validation rules expected for data exchanged between producers and consumers.

### Why use Pydantic for canonical models?

Pydantic provides typed models, runtime validation, declarative constraints, custom validators, serialization support, and JSON Schema generation. That makes it useful for defining enforceable Python data contracts.

### What is the difference between field-level and cross-field validation?

Field-level validation checks a value independently, such as ensuring latitude is within a valid range. Cross-field validation evaluates relationships between fields, such as requiring shelf life when a product is perishable.

### Why reject unknown fields?

Rejecting unknown fields helps detect producer mistakes and uncontrolled schema changes instead of silently allowing unexpected data into trusted datasets.

### Why generate JSON Schema?

JSON Schema provides a machine-readable representation of a contract that can support documentation, validation, integration, and downstream tooling.

### Why are enums useful in data platforms?

Enums create controlled vocabularies, preventing semantically equivalent values from being represented inconsistently across producers and consumers.

### What is schema drift?

Schema drift occurs when the actual or expected structure of data changes over time. Uncontrolled drift can break downstream consumers or, more dangerously, silently change data semantics.

### How would you manage schema evolution in production?

I would version important contracts, evaluate backward compatibility, test producers and consumers, automate schema-drift detection, document semantic changes, and deploy breaking changes through an explicit migration strategy.

## Key takeaway

A trustworthy data platform needs more than valid Python syntax.

The flow should be:

```text
Business meaning
       |
       v
Canonical contract
       |
       v
Validation
       |
       v
Machine-readable schema
       |
       v
Producers and consumers
       |
       v
Trusted data platform
```

The contract is the boundary that prevents inconsistent or invalid data from silently becoming trusted data.
