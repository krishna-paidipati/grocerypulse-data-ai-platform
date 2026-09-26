# 004 — Deterministic Synthetic Master Data

## What I Built

In GP-004, I implemented deterministic synthetic master-data generation for
GroceryPulse.

The implementation generates validated synthetic records for:

- suppliers
- stores
- products
- customers

The generated records use the canonical Pydantic data contracts created in
GP-003.

The complete dataset can be generated through a command-line interface and
exported as JSON Lines files for downstream processing.

The generation flow is:

```text
Canonical Pydantic contracts
        ↓
MasterDataGenerator
        ↓
Supplier / Store / Product / Customer records
        ↓
MasterDataset
        ↓
JSONL serialization
        ↓
Synthetic master-data files
```

## Why Synthetic Data Is Useful

A data platform often needs realistic development and testing data before
production source systems are available.

Synthetic data allows GroceryPulse to develop and test pipelines without:

- depending on production systems
- exposing customer or commercially sensitive data
- waiting for upstream integrations
- manually maintaining large test datasets

Synthetic data also makes failure scenarios easier to reproduce.

## Deterministic Generation

Random data is useful, but uncontrolled randomness makes tests difficult to
reproduce.

GroceryPulse therefore uses a seeded pseudo-random number generator:

```python
random.Random(seed)
```

The generator owns its own random-number-generator instance rather than using
Python's global random state.

Given the same:

- seed
- generator code
- entity counts
- generation sequence

the generator produces the same dataset.

This means a failure associated with a particular seed can be reproduced.

For example:

```bash
uv run python -m grocerypulse.generators.generate --seed 42
```

## Why the PRNG Is Not Security-Sensitive

The standard Python pseudo-random generator is intentionally used for
synthetic test-data generation.

It must not be used for:

- passwords
- authentication tokens
- encryption keys
- security-sensitive identifiers

For GroceryPulse synthetic retail records, reproducibility is desirable and
cryptographic randomness is unnecessary.

## Dependency Ordering and Referential Integrity

Products reference suppliers through `supplier_id`.

Therefore suppliers must exist before products are generated.

The relevant dependency is:

```text
Suppliers ──────→ Products

Stores

Customers
```

The Product generator selects supplier identifiers only from the Supplier
records supplied to it.

Tests verify that every generated Product supplier reference exists in the
generated Supplier dataset.

This prevents orphaned foreign keys.

## Validation at the Generation Boundary

Synthetic data should not bypass the same contracts used by application data.

Every generated entity is constructed through its canonical Pydantic model.

Therefore invalid generated values fail during generation rather than
propagating into later pipeline stages.

The boundary is:

```text
Random value generation
        ↓
Canonical Pydantic validation
        ↓
Validated domain record
```

This is important because downstream pipelines should not have to compensate
for synthetic data that violates the platform's own contracts.

## Dataset Orchestration

Individual entity generators are coordinated by:

```python
MasterDataGenerator.generate_dataset(...)
```

The method returns a `MasterDataset` dataclass containing:

- suppliers
- stores
- products
- customers

`MasterDataset` is an application-level container rather than an external
business data contract, so a Python dataclass is sufficient.

The entity counts are keyword-only arguments.

For example:

```python
generator.generate_dataset(
    supplier_count=10,
    store_count=8,
    product_count=15,
    customer_count=100,
)
```

This is clearer and less error-prone than relying on positional arguments such
as:

```python
generator.generate_dataset(10, 8, 15, 100)
```

With positional arguments, it would be much easier for a caller to
accidentally swap two counts.

## Separation of Concerns

Generation and persistence are deliberately separated.

`MasterDataGenerator` is responsible for creating valid domain records.

`export_master_dataset()` is responsible for serializing those records to
physical storage.

The architecture is therefore:

```text
Generation
    ↓
MasterDataset
    ↓
Serialization
    ↓
Physical storage
```

This separation means future exporters can be added without rewriting the
synthetic-data generation logic.

For example:

```text
MasterDataset
   ├── JSONL
   ├── Parquet
   ├── Amazon S3
   └── other storage targets
```

This is an example of separation of concerns: generation logic does not need
to know how or where its output will eventually be stored.

## Why JSON Lines

The first physical format used by GroceryPulse is JSON Lines (`.jsonl`).

Each line contains one complete JSON object.

For example:

```text
{"supplier_id":"SUP_0001", ...}
{"supplier_id":"SUP_0002", ...}
```

JSONL is useful at this stage because:

- records can be processed independently
- files can be streamed line by line
- it is human-readable
- it works well with command-line tools
- it is convenient for data-pipeline ingestion
- it does not require pandas or PyArrow

Parquet will be introduced later when GroceryPulse reaches the analytical
data-lake processing stages where a columnar format becomes more valuable.

## Serialization with Pydantic

The exporter serializes validated Pydantic records using:

```python
record.model_dump_json()
```

This is preferable to manually converting values such as `Decimal`, `date`,
and `datetime` because the canonical model already knows how its fields should
be represented as JSON-compatible values.

Tests also compare exported Product records with:

```python
product.model_dump(mode="json")
```

This verifies that the physical JSON representation corresponds to the
validated domain object.

## Idempotent Export

The exporter opens output files in write mode rather than append mode.

Conceptually:

```text
"w" → replace existing contents
"a" → append to existing contents
```

For the current snapshot-style master-data export, rerunning the same export
must replace the existing dataset rather than duplicate it.

For example:

```text
First run:
15 products

Second run:
15 products
```

The second run must not produce 30 products.

Idempotency is important in production Data Engineering because pipelines are
frequently retried after failures.

A safe retry should not silently duplicate data.

## Testing Filesystem Code

Exporter tests use pytest's `tmp_path` fixture.

Each test receives an isolated temporary directory.

This avoids:

- polluting the repository
- tests depending on existing local files
- one test affecting another test
- manual test-file cleanup

The export tests verify:

- expected files are created
- expected record counts are written
- every line contains valid JSON
- exported records match generated records
- identical datasets produce byte-identical output
- repeated exports are idempotent
- empty datasets create valid empty files

This allows filesystem behaviour to be tested without writing test artifacts
into the real `data/` directory.

## Command-Line Interface

GroceryPulse exposes synthetic master-data generation through:

```bash
uv run python -m grocerypulse.generators.generate
```

The CLI supports configurable:

- seed
- supplier count
- store count
- product count
- customer count
- output directory

For example:

```bash
uv run python -m grocerypulse.generators.generate \
  --seed 42 \
  --suppliers 10 \
  --stores 8 \
  --products 15 \
  --customers 100 \
  --output-dir data/synthetic/master
```

The standard-library `argparse` module is sufficient for this small CLI, so an
additional command-line framework is not required.

The CLI boundary is also tested.

The tests temporarily replace `sys.argv` using `unittest.mock.patch`, allowing
the normal argument-parsing path to be exercised without spawning a separate
Python process.

## Reproducibility with SHA-256

After generating the dataset, I calculated SHA-256 checksums using:

```bash
shasum -a 256 data/synthetic/master/*.jsonl
```

The generator was then executed again using the same default configuration.

The SHA-256 hashes remained identical for:

- customers
- products
- stores
- suppliers

The observed hashes were:

```text
cce0ed27f3b07ba36df0ba509a5d27015970a70b92a64750e3dafeb04a12be0a  customers.jsonl
b30240d98278e0d81bc0a26118c51665f89ba138f9a86b99fcf5f4db01aea4bc  products.jsonl
6d830593cf92652776003d0a725150e0eb11016256988bff7bebfd6761888ac9  stores.jsonl
9f9fa719353bf36fdb672a444ff964d1e87d290ed75a4cd30bc030ae1b156397  suppliers.jsonl
```

For the current generator, configuration, and execution environment, this
demonstrates byte-level reproducibility.

The reproducibility chain is:

```text
same seed
+ same counts
+ same code
+ same generation sequence
        ↓
same validated records
        ↓
same serialization
        ↓
same bytes
        ↓
same SHA-256
```

A checksum is useful as a compact fingerprint of a file.

If the physical contents unexpectedly change, the checksum will normally
change as well.

Checksums can therefore be useful for:

- artifact verification
- reproducibility checks
- detecting unexpected output changes
- validating transferred files
- pipeline integrity controls

## Generated-Data Repository Policy

Generated synthetic datasets are not committed to Git.

The repository ignores:

```text
data/synthetic/
```

The policy is to version-control:

- generator source code
- tests
- data contracts
- documentation
- deliberately maintained small fixtures when required

but not normal reproducible generated datasets.

The ignore rule can be verified using:

```bash
git check-ignore -v data/synthetic/master/products.jsonl
```

This shows not only that the file is ignored, but also which `.gitignore` rule
is responsible.

Because the normal synthetic dataset can be regenerated deterministically,
there is no need to continuously store its generated output in Git history.

This becomes increasingly important when GroceryPulse later generates much
larger transactional datasets.

## India-First Synthetic Scenario

The canonical GroceryPulse domain remains intended to be reusable rather than
hard-coded to one country.

GP-004, however, uses an India-first synthetic scenario.

The generated Store records use synthetic Bengaluru/Karnataka locations.

Supplier generation includes domestic suppliers and a smaller international
supplier scenario.

This is scenario data rather than a restriction imposed on the canonical
domain model.

That distinction is important:

```text
Canonical domain contract
        ↓
Country-neutral business structure

Synthetic scenario/configuration
        ↓
India-first generated data
```

Geography should generally be represented through data or configuration rather
than hard-coded into the reusable domain model.

## Product and Supplier Relationship

The current Product contract contains one optional `supplier_id`.

That is sufficient for GP-004 because it allows us to demonstrate
cross-entity referential integrity.

A production retail platform will normally need a richer relationship because
one Product may be available from multiple Suppliers and one Supplier may
provide multiple Products.

A future relationship such as `SupplierProduct` could contain attributes such
as:

- supplier-specific SKU
- purchase price
- minimum order quantity
- lead time
- availability
- effective dates

This is intentionally deferred rather than being hidden inside GP-004.

## Future Product-Modelling Evolution

The current Product category enum is intentionally limited.

A future product-agnostic Store Intelligence platform may need a more flexible
category hierarchy rather than requiring a source-code enum change whenever a
new retail assortment is introduced.

GP-004 therefore uses the existing canonical Product contract rather than
silently redesigning the model to fit synthetic generation.

This preserves an important engineering principle:

> Generators should conform to the domain contract. They should not quietly
> redefine the domain contract merely because generating data would otherwise
> be inconvenient.

## Future Tax-Modelling Evolution

The current canonical Product contract contains `vat_rate`.

For the India-first GP-004 scenario, the generator does not attempt to invent
a complete Indian GST model.

Generated products currently use a zero value rather than introducing
inaccurate tax assumptions into the synthetic dataset.

Tax modelling should be evolved explicitly when GroceryPulse reaches the
relevant commerce and pricing stages.

## Important Production Consideration: Random-Stream Coupling

The current implementation uses one seeded PRNG instance across the entity
generators.

This means random-number consumption depends on generation order.

For GP-004, the reproducibility contract is:

> Same seed + same counts + same generation sequence produces the same
> dataset.

It does not currently guarantee that changing the number of Suppliers will
leave every subsequently generated Store, Product, or Customer unchanged.

If independent domain reproducibility becomes a requirement, a future version
could derive separate deterministic random streams for each entity domain.

For example:

```text
Master seed
   ├── Supplier RNG
   ├── Store RNG
   ├── Product RNG
   └── Customer RNG
```

That additional complexity is not currently required.

The important engineering decision is to document the current reproducibility
guarantee accurately rather than claiming stronger isolation than the
implementation provides.

## What Initially Went Wrong

During GP-004, Product generator tests were expected to exist, but they had
not actually been added to the test file.

Running:

```bash
uv run pytest --collect-only -q
```

showed that the expected Product tests were missing.

This reinforced an important lesson:

> Never assume that a test exists merely because it was planned. Verify that
> pytest actually discovers it.

After the missing Product tests were added, the test count increased as
expected.

Another useful lesson was that coverage displayed during:

```bash
uv run pytest --collect-only -q
```

is not equivalent to normal executed-test coverage.

Collection discovers tests but does not execute them.

The authoritative coverage result therefore comes from:

```bash
uv run pytest
```

## Ruff Annotation Lesson

The strict Ruff configuration detected:

```text
ANN202 Missing return type annotation for private function
```

for a private test helper.

The helper was changed from:

```python
def _generate_test_dataset():
```

to:

```python
def _generate_test_dataset() -> MasterDataset:
```

The warning was fixed rather than suppressed because the return type is known
and useful.

This improves both readability and static type checking.

## Quality Results

At the completion of the tested GP-004 implementation, the repository test
suite reported:

```text
74 tests passed
Required coverage: 85%
Total coverage: 95.03%
```

The implementation also passed:

```bash
uv run ruff check
uv run mypy src tests
```

The final repository-wide quality gate will still be run before the GP-004
commit.

## Commands I Learned

### Generate the Dataset

```bash
uv run python -m grocerypulse.generators.generate
```

### View CLI Help

```bash
uv run python -m grocerypulse.generators.generate --help
```

### Generate with Explicit Configuration

```bash
uv run python -m grocerypulse.generators.generate \
  --seed 42 \
  --suppliers 10 \
  --stores 8 \
  --products 15 \
  --customers 100 \
  --output-dir data/synthetic/master
```

### List Generated Files

```bash
find data/synthetic/master -type f -maxdepth 1 -print
```

### Count JSONL Records

```bash
wc -l data/synthetic/master/*.jsonl
```

Because JSONL stores one record per line, `wc -l` provides a quick record-count
check.

### Inspect the First Record

```bash
head -n 1 data/synthetic/master/products.jsonl
```

### Inspect File Sizes

```bash
du -h data/synthetic/master/*.jsonl
```

### Calculate SHA-256 Checksums

```bash
shasum -a 256 data/synthetic/master/*.jsonl
```

### Verify a Git Ignore Rule

```bash
git check-ignore -v data/synthetic/master/products.jsonl
```

### Format Python

```bash
uv run ruff format src tests
```

### Lint Python

```bash
uv run ruff check src tests
```

### Run Static Type Checking

```bash
uv run mypy src tests
```

For this src-layout project, the canonical mypy invocation is:

```bash
uv run mypy src tests
```

### Run the Full Test Suite

```bash
uv run pytest
```

### Inspect Test Discovery

```bash
uv run pytest --collect-only -q
```

This is useful for verifying that expected tests are actually being discovered,
but it should not be treated as the authoritative coverage run.

## Key Concepts Learned

The main Data Engineering and software-engineering concepts reinforced in
GP-004 were:

- deterministic synthetic-data generation
- seeded pseudo-random number generation
- reproducibility
- referential integrity
- dependency ordering
- validation boundaries
- application-level dataset orchestration
- separation of concerns
- serialization
- JSON Lines
- idempotent pipeline behaviour
- filesystem testing
- pytest fixtures
- command-line interfaces
- SHA-256 checksums
- generated-artifact repository policy
- static typing
- test discovery
- layered testing

## Interview Questions

### Why did you make the synthetic-data generator deterministic?

Determinism makes data-pipeline failures reproducible. Given the same seed,
counts, code and generation sequence, I can recreate the same dataset and
investigate the same failure conditions.

### Why use a dedicated `random.Random` instance?

It isolates GroceryPulse generation from Python's global random state and
makes the generator easier to reason about and reproduce.

It also prevents unrelated code using the global random generator from
unexpectedly changing GroceryPulse's generated sequence.

### How do you maintain referential integrity?

Entities are generated in dependency order.

Suppliers are generated before Products, and Products choose supplier
identifiers only from the generated Supplier records.

Automated tests verify that every generated Product supplier reference exists
in the Supplier dataset.

### Why validate synthetic data with Pydantic?

Synthetic data should obey the same contracts as application data.

Creating records through the canonical Pydantic models prevents invalid test
data from silently entering downstream pipelines.

It also means the synthetic generator exercises the same validation boundary
that other application code uses.

### Why separate generation from export?

Generation and persistence are different responsibilities.

Keeping them separate allows the same validated `MasterDataset` to be written
to JSONL today and potentially Parquet, Amazon S3, or another destination
later without changing the generation logic.

### What is idempotency?

An idempotent operation can be safely repeated without unintentionally
changing the final result beyond the intended state.

For the current snapshot exporter, rerunning the export replaces existing
files rather than appending duplicate records.

### Why is idempotency important in Data Engineering?

Production pipelines fail and are retried.

If a retry blindly appends the same records again, it can create duplicates
and corrupt downstream metrics.

Designing operations to be idempotent makes recovery and reruns safer.

### Why JSONL rather than CSV?

JSONL maps naturally to structured records and can represent values without
forcing everything into a flat comma-separated representation.

Each record is independently parseable, and JSONL is easy to stream and
inspect.

### Why JSONL rather than Parquet at this stage?

At this stage I wanted a lightweight, inspectable, streamable interchange
format without introducing pandas or PyArrow.

Parquet becomes more appropriate when GroceryPulse moves into analytical
data-lake processing with PySpark because it is a columnar format designed for
efficient analytical workloads.

### How did you prove reproducibility?

I generated the files and calculated SHA-256 hashes.

I then regenerated the dataset using the same configuration and calculated
the hashes again.

The hashes were identical, demonstrating byte-level reproducibility for the
current generator, configuration, and execution environment.

### Does using the same seed always guarantee every entity remains unchanged?

Not under every possible change to the current implementation.

The generator currently uses one seeded PRNG stream.

Therefore changing an earlier entity count can change how many random values
are consumed before later entities are generated.

The current guarantee is same seed, same counts, same code, and same generation
sequence produce the same dataset.

If independent entity reproducibility becomes necessary, separate deterministic
random streams can be introduced.

### Why not commit the generated JSONL files to Git?

They are reproducible generated artifacts rather than source code.

Committing generated datasets would increase repository size and create noisy
Git history, especially as data volumes grow.

The source code, tests, contracts and documentation are version-controlled,
and the data can be regenerated when required.

### What is the purpose of `tmp_path` in the exporter tests?

`tmp_path` is a pytest fixture that gives each test an isolated temporary
filesystem location.

It lets filesystem behaviour be tested without polluting the repository or
allowing tests to interfere with one another.

### Why use `argparse` instead of Click or Typer?

The current CLI is small and its requirements are fully handled by Python's
standard-library `argparse` module.

Adding another dependency would increase project complexity without providing
enough value at this stage.

### What would you improve for a production-scale generator?

I would consider:

- independent deterministic random streams by domain
- configuration-driven reference data
- significantly larger datasets
- richer cross-entity relationships
- transaction and transaction-line generation
- inventory movements
- supplier deliveries
- promotions
- subscriptions and pre-orders
- batch and lot-level inventory
- controlled late-arriving and malformed records
- duplicate and out-of-order events
- schema-versioned events
- configurable data-quality defects
- scalable Parquet output
- partitioning strategies
- direct Amazon S3 integration
- generation-performance testing

These additions should be introduced incrementally as GroceryPulse progresses
through later Data Engineering stages rather than being prematurely added to
the master-data milestone.
