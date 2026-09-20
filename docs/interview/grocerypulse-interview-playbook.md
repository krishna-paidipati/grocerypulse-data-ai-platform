# GroceryPulse — Interview Engineering Playbook

> A living record of the architecture, engineering decisions, production controls,
> lessons learned, failure scenarios, and interview talking points developed while
> building GroceryPulse.

---

## 1. Purpose

GroceryPulse is a production-style grocery retail Data, ML and GenAI engineering
platform.

This document captures the engineering reasoning behind the platform so that the
project can be demonstrated confidently in:

- Data Engineering interviews
- AWS Data Engineering interviews
- System-design discussions
- Architecture walkthroughs
- GitHub portfolio demonstrations
- Behavioural and technical interviews

This is a **living document** and should evolve with the platform.

For every significant GroceryPulse milestone, this playbook should capture:

1. What was built.
2. Why it was designed that way.
3. Alternatives considered.
4. Production risks identified.
5. Controls implemented.
6. Problems encountered.
7. How those problems were diagnosed and resolved.
8. Important engineering terminology.
9. Interview questions that can be answered from the work.
10. Evidence available in the repository.

---

# 2. Engineering Philosophy

GroceryPulse is not intended to demonstrate that I can simply assemble a long
list of technologies.

The objective is to demonstrate that I understand:

```text
WHY a system is designed
        ↓
HOW it behaves
        ↓
HOW it fails
        ↓
HOW failures are detected
        ↓
HOW failures are recovered
        ↓
HOW correctness is demonstrated
        ↓
HOW the system operates at production scale
```

The portfolio should demonstrate **engineering judgement**, not simply technology
usage.

---

# 3. GroceryPulse Engineering Mind Map

```text
                              GROCERYPULSE
                 Production-Style Data / ML / GenAI
                                   │
        ┌──────────────────────────┼──────────────────────────┐
        │                          │                          │
  ENGINEERING                DATA CONTRACTS              GOVERNANCE
  FOUNDATION                       │                          │
        │                          │                          │
  Python 3.12                Pydantic v2                 CODEOWNERS
  src layout                 Domain Models               Dependabot
  pyproject.toml             Validation                  Git workflow
  uv                         Enums                       CI
  uv.lock                    Business Rules              Least Privilege
        │                    JSON Schema                     │
        │                          │                          │
        │                   SOURCE OF TRUTH                  │
        │                          │                          │
        └──────────────┬───────────┴────────────┬─────────────┘
                       │                        │
                 QUALITY GATES            DOCUMENTATION
                       │                        │
                 Ruff                       MkDocs
                 mypy --strict              Material
                 pytest                     mkdocstrings
                 coverage >= 85%            Google-style docstrings
                 pip-audit                  Strict documentation build
                 pre-commit                      │
                       │                        │
                       └────────────┬───────────┘
                                    │
                          REPRODUCIBLE BUILD
                                    │
                            GitHub Actions CI
                                    │
                           Clean Linux Runner
                                    │
                 ┌──────────────────┴──────────────────┐
                 │                                     │
          CURRENT FOUNDATION                     FUTURE PLATFORM
                 │                                     │
          Canonical contracts                         S3
          Automated tests                             PySpark
          Coverage gate                               Snowflake
          Security audit                              dbt
          Deterministic schemas                       Airflow
          Schema-drift control                        Kafka / MSK
          CI                                          Data Quality
                                                      Observability
                                                      Terraform
                                                      SageMaker
                                                      Bedrock
                                                      QuickSight
```

---

# PART I — ENGINEERING JOURNEY

# 4. GP-001 — Repository and Engineering Foundation

## What I Built

GroceryPulse was established as a structured Python engineering repository rather
than a collection of standalone scripts.

The engineering foundation includes:

- Python 3.12
- `src/` package layout
- `pyproject.toml`
- `uv`
- virtual-environment isolation
- Git
- GitHub
- pytest
- Ruff
- professional project documentation

## Engineering Principle

> A production data platform starts with reproducible engineering foundations,
> not with the first ETL script.

---

## Why Use a `src/` Layout?

Application code lives beneath:

```text
src/grocerypulse/
```

rather than directly in the repository root.

This creates a clear separation between:

```text
Application source
Tests
Documentation
Configuration
Generated artifacts
Infrastructure
```

It also reduces the possibility of accidentally importing source code directly
from the working directory rather than from the installed Python package.

### Important Technical Terms

- Package layout
- Source layout
- Import isolation
- Separation of concerns
- Project structure

---

# 5. Dependency Management and Reproducibility

GroceryPulse uses `uv` for Python dependency and environment management.

The resolved dependency graph is captured in:

```text
uv.lock
```

and the lockfile is committed to Git.

This supports:

- deterministic dependency resolution
- reproducible development environments
- reproducible CI environments
- controlled dependency upgrades
- reduced "works on my machine" behaviour

## Engineering Principle

> The environment required to execute the software should be reproducible from
> version-controlled configuration.

## Important Technical Terms

- Reproducibility
- Dependency resolution
- Lockfile
- Environment isolation
- Dependency graph
- Transitive dependency
- Build reproducibility

## Interview Talking Point

> I deliberately established reproducible dependency management before building
> the data platform. GroceryPulse uses uv with a committed lockfile so development
> and CI operate from a controlled dependency graph rather than independently
> resolving package versions.

---

# 6. GP-002 — Retail Domain Modelling

## Define the Grain Before Building the Pipeline

One of the first modelling decisions was to explicitly define the grain of each
dataset.

For example:

```text
TRANSACTION
Grain:
One row per customer checkout

TRANSACTION_ITEM
Grain:
One row per product line within a checkout
```

These represent different business grains.

## Why Grain Matters

Suppose a transaction has a total value of:

```text
£6.76
```

and contains three product lines.

If the transaction header is joined incorrectly to the transaction-item table, the
header value could appear three times:

```text
£6.76
£6.76
£6.76
```

A careless aggregation could therefore produce:

```text
£20.28
```

instead of:

```text
£6.76
```

This is an example of **join fan-out**.

## Engineering Principle

> Define the business grain before designing keys, joins, pipelines or analytical
> measures.

## Important Technical Terms

- Data grain
- Business grain
- Primary key
- Composite key
- Foreign key
- Referential integrity
- Join fan-out
- Double counting
- OLTP
- OLAP
- Dimensional modelling
- Fact table
- Dimension table

## Interview Talking Point

> Before implementing pipelines, I explicitly modelled dataset grain and key
> relationships. This reduces the risk of join fan-out and incorrect analytical
> aggregation later in the warehouse.

---

# 7. Keys and Referential Integrity

Different types of keys serve different purposes.

## Primary Key

Uniquely identifies a record within a dataset.

Example:

```text
transaction_id
```

## Composite Key

Uses multiple columns together to uniquely identify a record.

For example:

```text
transaction_id + line_number
```

could uniquely identify a transaction item.

## Foreign Key

Represents a relationship with another entity.

For example:

```text
Product.supplier_id
```

references a supplier.

## Engineering Principle

> Keys are not simply database implementation details. They express business
> identity and relationships.

## Important Technical Terms

- Entity identity
- Referential integrity
- Natural key
- Surrogate key
- Composite key
- Foreign key
- Cardinality

---

# 8. Canonical Retail Entities

Initial GroceryPulse master entities include:

```text
Store
Product
Customer
Supplier
```

These represent important master-data concepts within the retail domain.

Future transactional entities will build upon these contracts, including:

```text
Transaction
TransactionItem
Inventory
Promotion
Delivery
OnlineOrder
```

This establishes a controlled domain model before introducing large-scale data
generation and ingestion.

---

# 9. GP-003 — Canonical Data Contracts

## Why Introduce Data Contracts?

Data pipelines should not assume that incoming records are valid.

Without explicit contracts, malformed data can propagate through the platform:

```text
Source
  ↓
Kafka
  ↓
S3
  ↓
PySpark
  ↓
Snowflake
  ↓
dbt
  ↓
BI / ML / AI
```

The further invalid data travels, the more expensive it becomes to diagnose and
repair.

GroceryPulse therefore validates data close to the system boundary.

## Engineering Principle

> Fail fast at the ingestion boundary rather than creating downstream
> data-quality debt.

## Important Technical Terms

- Data contract
- Contract enforcement
- Boundary validation
- Fail-fast validation
- Data-quality debt
- Domain model
- Canonical model

---

# 10. Pydantic as the Canonical Model

GroceryPulse uses Pydantic v2 models for canonical domain contracts.

Current contracts include:

```text
Store
Product
Customer
Supplier
```

These contracts define:

- identifiers
- types
- required fields
- optional fields
- enumerations
- numeric ranges
- string constraints
- date constraints
- cross-field business rules

The Pydantic models act as the:

**canonical source of truth**.

## Interview Talking Point

> I use Pydantic models as canonical domain contracts rather than allowing
> validation logic to become scattered across individual pipelines.

---

# 11. Defensive Contract Configuration

The shared GroceryPulse model configuration includes concepts such as:

```python
extra = "forbid"
str_strip_whitespace = True
validate_assignment = True
```

## `extra="forbid"`

Unexpected fields are rejected rather than silently accepted.

This helps expose unexpected producer-side changes.

## `str_strip_whitespace=True`

Boundary whitespace is normalised automatically.

## `validate_assignment=True`

Validation continues when model values are modified after object creation.

## Engineering Concepts

- Defensive validation
- Contract enforcement
- Boundary validation
- Mutation safety
- Schema strictness
- Fail-fast behaviour

## Interview Talking Point

> I deliberately chose strict contract behaviour because silently accepting
> unexpected fields can hide upstream schema changes and create downstream
> ambiguity.

---

# 12. Business Invariants

Validation is not limited to primitive data types.

GroceryPulse also enforces domain-specific business rules.

Examples include:

```text
Store latitude must be valid.

Store longitude must be valid.

Supplier reliability must be between 0 and 1.

Customer signup date cannot be in the future.

Perishable products require shelf-life information.

Product cost price should not exceed the canonical unit price.
```

These are examples of **business invariants**.

## Structural Validation vs Semantic Validation

A record can be syntactically valid while still being semantically invalid.

For example:

```text
reliability_score = 5.0
```

is a valid floating-point number.

However, it violates the GroceryPulse domain contract if the permitted range is:

```text
0.0 → 1.0
```

## Interview Talking Point

> I distinguish structural validation from business-rule validation. A record can
> be syntactically valid while still violating a domain invariant, so both need
> to be enforced.

---

# 13. Enumerations and Controlled Domains

Important categorical values are represented using explicit enumerations rather
than arbitrary strings.

Examples include:

```text
StoreFormat
CustomerSegment
SalesChannel
SupplierType
UnitMeasure
ProductCategory
```

This reduces:

- spelling inconsistencies
- uncontrolled categorical values
- downstream grouping errors
- contract ambiguity

## Engineering Principle

> Where the business domain has a known finite set of valid values, the contract
> should express that domain explicitly.

## Important Technical Terms

- Enumeration
- Controlled vocabulary
- Domain constraint
- Categorical consistency
- Contract semantics

---

# 14. JSON Schema Generation

The canonical Pydantic models generate machine-readable JSON Schema contracts.

```text
Pydantic Models
      │
      │ model_json_schema()
      ▼
JSON Schema
      │
      ▼
schemas/json/
```

Generated contracts currently include:

```text
customer.json
product.json
store.json
supplier.json
```

## Why This Matters

The Python implementation remains authoritative while JSON Schema provides a
language-independent contract representation.

This creates a foundation for future integration with:

- event producers
- Kafka
- APIs
- validation services
- ingestion pipelines
- contract testing

## Important Technical Terms

- Canonical schema
- Machine-readable contract
- Schema interoperability
- Contract generation
- Source of truth
- Generated artifact

## Interview Talking Point

> Rather than manually maintaining Python models and JSON schemas independently,
> I generate the machine-readable contracts from the canonical Pydantic models.
> This reduces duplicated schema definitions and the risk of divergence.

---

# 15. Deterministic Schema Generation

Schema generation was explicitly tested by generating the contracts twice and
calculating hashes for each generated artifact.

Both generations produced identical hashes.

Conceptually:

```text
same source
    ↓
same transformation
    ↓
same generated artifact
```

This demonstrates **deterministic generation**.

## Engineering Principle

> Generated artifacts should be reproducible from their authoritative source.

## Interview Talking Point

> I didn't simply assume generated contracts were deterministic. I verified
> determinism by regenerating the artifacts and comparing their hashes.

---

# 16. Idempotency

The schema exporter can be safely executed repeatedly without continually changing
the resulting state.

This demonstrates the principle of **idempotency**.

This concept will become increasingly important later in GroceryPulse for:

- Airflow retries
- Spark reruns
- S3 ingestion
- dbt incremental processing
- Kafka consumers
- infrastructure deployment

## Determinism vs Idempotency

### Determinism

Same input produces the same output.

### Idempotency

Repeating an operation does not continue changing the final state.

These concepts are related but not identical.

## Interview Question

**What is the difference between deterministic and idempotent processing?**

Suggested answer:

> Determinism means identical inputs produce identical outputs. Idempotency means
> repeating the same operation does not continue changing the resulting state.
> GroceryPulse's schema-generation process demonstrates both concepts.

---

# 17. Automated Schema-Drift Detection

CI regenerates the JSON Schema contracts and checks Git for differences.

Conceptually:

```bash
uv run python -m grocerypulse.schemas.export
git diff --exit-code -- schemas/json/
```

The control behaves approximately like this:

```text
Developer modifies Product model
             ↓
forgets to regenerate product.json
             ↓
CI regenerates contracts
             ↓
Git detects difference
             ↓
CI FAILS
```

## Engineering Principle

> Generated artifacts should not silently diverge from their authoritative source.

## Important Technical Terms

- Schema drift
- Contract drift
- Drift detection
- Generated artifact
- Source of truth
- CI enforcement

## Interview Talking Point

> The Pydantic model is authoritative. CI regenerates the JSON contracts and fails
> if the committed artifacts diverge from their source, giving me automated
> schema-drift detection.

---

# PART II — SOFTWARE ENGINEERING QUALITY

# 18. Testing Strategy

The current verified GroceryPulse baseline includes:

```text
13 automated tests
90.13% total test coverage
85% minimum coverage gate
```

Testing covers important contract behaviour including:

- valid models
- invalid identifiers
- invalid coordinates
- invalid supplier reliability
- negative prices
- perishable shelf-life requirements
- future customer signup dates
- unknown fields
- schema generation

## Engineering Principle

> Coverage is a guardrail, not the objective.

The project deliberately avoids meaningless tests written purely to increase the
coverage percentage.

The objective is to test:

- business invariants
- contract behaviour
- failure conditions
- boundary conditions
- regression-sensitive logic

## Important Technical Terms

- Regression testing
- Test coverage
- Negative testing
- Boundary testing
- Business-rule testing
- Quality threshold

## Interview Talking Point

> I maintain an automated coverage threshold, but I don't optimise for 100%
> coverage as a vanity metric. I prioritise tests around business invariants,
> failure paths and regression-sensitive behaviour.

---

# 19. Static Analysis and Type Safety

GroceryPulse uses:

```text
Ruff
mypy --strict
```

## Ruff

Ruff provides:

- linting
- formatting
- import ordering
- code-quality checks
- security-related rules
- docstring rules

## mypy

Strict static type checking moves a class of defects from runtime into the
development feedback loop.

## Engineering Principle

> Detect defects as early and as cheaply as practical.

## Important Technical Terms

- Static analysis
- Type safety
- Static type checking
- Linting
- Code quality
- Developer feedback loop

## Interview Talking Point

> I use static analysis and strict typing to move a class of defects from runtime
> into the development feedback loop.

---

# 20. Layered Quality Gates

GroceryPulse uses multiple quality-control layers.

```text
Developer
    │
    ▼
PRE-COMMIT
Fast local feedback
    │
    ▼
LOCAL QUALITY GATE
make quality
    │
    ▼
REMOTE CI
Independent Linux execution
    │
    ▼
MERGE / RELEASE
```

This demonstrates **defence in depth**.

It also demonstrates **shift-left quality engineering**.

## Why Multiple Layers?

Each layer solves a different problem.

### Pre-Commit

Detect inexpensive issues immediately.

### Local Quality Gate

Perform comprehensive validation before code leaves the developer environment.

### Remote CI

Independently verify the repository in a clean environment.

## Interview Talking Point

> I use layered quality controls rather than relying on a single CI pipeline.
> Pre-commit provides fast feedback, the local quality gate performs comprehensive
> validation, and CI independently reproduces those guarantees in a clean
> environment.

---

# 21. Pre-Commit Controls

Before a commit is accepted, automated hooks perform checks including:

```text
large-file detection
JSON validation
TOML validation
YAML validation
private-key detection
end-of-file consistency
line-ending consistency
trailing-whitespace detection
Ruff linting
Ruff formatting
```

## Engineering Principle

> Cheap defects should be detected as early as possible.

Finding a formatting or configuration problem before commit is cheaper than
finding it after CI, deployment or production.

## Important Technical Terms

- Shift-left testing
- Pre-commit hook
- Fast feedback
- Automated enforcement
- Developer guardrail

---

# 22. Local Quality Gate

GroceryPulse exposes a common quality command:

```bash
make quality
```

The quality gate performs:

```text
Formatting validation
        ↓
Linting
        ↓
Static type checking
        ↓
Tests
        ↓
Coverage
        ↓
Dependency vulnerability audit
        ↓
Documentation build
```

A failure in any stage fails the quality gate.

## Important Technical Terms

- Quality gate
- Automated verification
- Developer feedback loop
- Build failure
- Regression prevention

---

# PART III — SECURITY AND GOVERNANCE

# 23. Dependency Security

GroceryPulse uses:

```text
pip-audit
Dependabot
uv.lock
```

## pip-audit

Checks installed third-party Python dependencies against known vulnerability
information.

## Dependabot

Automatically creates dependency-update proposals.

## uv.lock

Provides controlled and reproducible dependency resolution.

Together these contribute to **software supply-chain hygiene**.

## Important Technical Terms

- Dependency vulnerability scanning
- Software supply chain
- Dependency provenance
- Dependency lifecycle
- Lockfile
- Transitive dependency

## Interview Talking Point

> I treat dependency management as part of the software supply chain. The lockfile
> provides reproducibility, pip-audit checks known vulnerabilities, and Dependabot
> manages dependency-update proposals.

---

# 24. Documentation as Code

GroceryPulse uses:

```text
Google-style Python docstrings
        ↓
mkdocstrings
        ↓
MkDocs
        ↓
Generated developer documentation
```

Documentation is validated using:

```bash
uv run mkdocs build --strict
```

This makes documentation part of the engineering lifecycle.

## Engineering Principle

> Documentation should evolve with the implementation rather than being maintained
> as an unrelated artifact.

## Important Technical Terms

- Documentation as code
- API reference generation
- Docstrings
- Strict documentation build
- Developer documentation

## Interview Talking Point

> Documentation is part of the quality gate. I use source-level docstrings,
> mkdocstrings and MkDocs so documentation evolves alongside the implementation
> and is validated in CI.

---

# 25. Code Ownership

GroceryPulse uses:

```text
.github/CODEOWNERS
```

This explicitly defines ownership boundaries for important repository areas.

This establishes a foundation for future pull-request review governance.

## Important Technical Terms

- Code ownership
- Repository governance
- Review responsibility
- Ownership boundary

---

# PART IV — CONTINUOUS INTEGRATION

# 26. GitHub Actions CI

GitHub Actions provides independent CI execution.

The workflow executes on a clean Linux runner.

The CI process includes:

```text
Checkout repository
        ↓
Install uv
        ↓
Install Python
        ↓
Synchronise locked dependencies
        ↓
Formatting
        ↓
Linting
        ↓
Strict type checking
        ↓
Tests + coverage
        ↓
Dependency audit
        ↓
Schema-drift detection
        ↓
Strict documentation build
```

## Engineering Principle

> Local success is not sufficient evidence of reproducibility.

A project that works on one developer laptop may still depend on hidden local
state.

CI verifies GroceryPulse independently in an ephemeral environment.

## Important Technical Terms

- Continuous Integration
- Ephemeral runner
- Reproducible build
- Independent verification
- Build pipeline
- Quality gate

## Interview Talking Point

> Local success wasn't sufficient evidence for me. I reproduced the quality gates
> on a clean GitHub-hosted Linux runner to eliminate developer-machine
> assumptions.

---

# 27. Least-Privilege CI

The GitHub Actions workflow explicitly uses:

```yaml
permissions:
  contents: read
```

The CI process therefore receives only the repository permissions required for its
job.

This demonstrates the **principle of least privilege**.

## Interview Talking Point

> I explicitly restricted CI permissions rather than relying on unnecessarily
> broad defaults. The quality workflow only requires read access to repository
> contents.

---

# 28. CI Concurrency Control

The workflow uses concurrency control so superseded executions can be cancelled.

This avoids wasting CI resources on obsolete runs when newer changes are
available.

## Important Technical Terms

- CI concurrency
- Superseded build
- Resource efficiency
- Build cancellation

---

# 29. Repository Governance

The current engineering governance layer includes:

```text
Git
GitHub
CODEOWNERS
Pre-commit
Dependabot
GitHub Actions
Quality gates
Documentation standards
```

The repository is therefore treated as an **engineering product**, not merely as
source-code storage.

---

# PART V — PRODUCTION THINKING

# 30. Production Failure Scenarios

| Failure Scenario | Engineering Risk | GroceryPulse Control |
|---|---|---|
| Invalid source record | Downstream data corruption | Pydantic validation |
| Unexpected field | Silent contract change | `extra="forbid"` |
| Invalid business value | Semantically incorrect data | Business invariants |
| Schema changes without regenerated contract | Contract drift | CI schema-drift detection |
| Different dependency versions | Non-reproducible build | `uv.lock` |
| Formatting inconsistency | Codebase inconsistency | Ruff |
| Type defect | Runtime failure | strict mypy |
| Regression | Existing behaviour breaks | pytest |
| Insufficient testing | Undetected defects | Coverage threshold |
| Vulnerable dependency | Security exposure | pip-audit |
| Outdated dependency | Maintenance/security risk | Dependabot |
| Developer forgets checks | Defect committed | pre-commit |
| Works only locally | Deployment/CI failure | GitHub Actions |
| Documentation breaks | Developer confusion | MkDocs strict build |
| Unclear ownership | Review ambiguity | CODEOWNERS |

---

# 31. Engineering Vocabulary

| Term | Meaning | GroceryPulse Evidence |
|---|---|---|
| Data Grain | What one row represents | Transaction vs TransactionItem |
| Join Fan-Out | Row multiplication caused by joins | Transaction/header modelling |
| Canonical Model | Authoritative domain representation | Pydantic entities |
| Data Contract | Explicit agreement about data structure and rules | Pydantic + JSON Schema |
| Business Invariant | Rule that must remain true for valid domain data | Cross-field validators |
| Fail Fast | Reject invalid state early | Pydantic boundary validation |
| Schema Governance | Controlled management of schemas | Canonical models + generated contracts |
| Schema Drift | Unexpected divergence in contracts | CI regeneration check |
| Determinism | Same input produces same output | Identical schema hashes |
| Idempotency | Repetition preserves final state | Schema exporter |
| Reproducibility | Environment/build can be recreated | uv + lockfile + CI |
| Static Analysis | Analyse code without executing it | Ruff + mypy |
| Type Safety | Detect incompatible types early | mypy strict |
| Regression Testing | Verify existing behaviour remains valid | pytest |
| Quality Gate | Required checks before accepting change | `make quality` |
| Shift Left | Detect problems earlier in lifecycle | pre-commit |
| Defence in Depth | Multiple independent controls | pre-commit → local gate → CI |
| Supply-Chain Security | Protect dependency/build chain | pip-audit + Dependabot |
| Documentation as Code | Documentation managed with software lifecycle | MkDocs |
| Code Ownership | Explicit responsibility for code areas | CODEOWNERS |
| Least Privilege | Grant minimum required permissions | CI `contents: read` |
| Ephemeral Environment | Temporary clean execution environment | GitHub Actions runner |
| Generated Artifact | File produced from authoritative source | JSON schemas |

---

# PART VI — PROBLEMS ENCOUNTERED AND LESSONS LEARNED

# 32. Generated Python Cache Accidentally Tracked

A generated Python bytecode artifact under `__pycache__` was found in Git.

Generated runtime artifacts should not form part of the source repository.

The file was removed from version control and the ignore configuration was
verified.

## Lesson

> Version control should contain authoritative source and intentionally generated
> artifacts, not machine-specific runtime residue.

## Interview Concepts

- Repository hygiene
- Generated artifacts
- `.gitignore`
- Source control discipline

---

# 33. Generic YAML Validation vs MkDocs Configuration

MkDocs configuration can contain application-specific YAML constructs that a
generic safe YAML validator does not understand.

Rather than disabling YAML validation globally, the generic YAML hook excludes
only:

```text
mkdocs.yml
```

while MkDocs itself validates that file through:

```bash
uv run mkdocs build --strict
```

Other YAML files continue to receive generic validation.

## Engineering Lesson

> Use the validator that understands the semantics of the artifact being
> validated.

## Why This Is Important

The solution was not:

```text
Disable YAML validation everywhere
```

Instead it was:

```text
Generic YAML validator
        ↓
all normal YAML files

MkDocs validator
        ↓
mkdocs.yml
```

This preserves validation coverage while avoiding an inappropriate validator for
an application-specific configuration file.

## Interview Concepts

- Tooling compatibility
- Targeted exception
- Validation semantics
- Least-broad exception
- Quality-control design

---

# 34. Pre-Commit Auto-Fixes

Some pre-commit hooks can modify files automatically.

When this happens, the correct workflow is:

```text
Run pre-commit
      ↓
Hook modifies file
      ↓
Review modification
      ↓
Restage file
      ↓
Run checks again
      ↓
Commit
```

The correct response is **not** to bypass the hook.

## Engineering Principle

> Quality controls should be resolved, not circumvented.

---

# 35. Schema Reproducibility Verification

Generated JSON schemas were not simply assumed to be stable.

The generation process was executed repeatedly and resulting hashes were compared.

The generated files remained identical.

## Lesson

> Important engineering properties should be demonstrated through evidence where
> practical rather than merely assumed.

---

# PART VII — INTERVIEW QUESTIONS

# 36. Tell Me About GroceryPulse

GroceryPulse is a production-style grocery retail Data, ML and GenAI engineering
platform that I am building to demonstrate the complete lifecycle of a modern data
platform.

Rather than starting directly with ETL pipelines, I first established explicit
domain modelling, canonical data contracts, reproducible dependency management,
automated testing, static analysis, security scanning, documentation and CI.

The platform will progressively introduce AWS, S3, PySpark, Snowflake, dbt,
Airflow, Kafka, ML and GenAI capabilities while maintaining those engineering
controls.

---

# 37. Why Did You Define Data Grain First?

Because grain determines what each row represents.

If grain is ambiguous, joins and aggregations can produce incorrect results such as
double counting.

For example, joining transaction-header measures to transaction-item records can
create join fan-out.

I therefore define grain before keys, joins and analytical measures.

---

# 38. Why Did You Use Pydantic?

Pydantic allows the domain contract to express both structural constraints and
business invariants.

It also provides machine-readable JSON Schema generation, allowing the Python model
to remain authoritative while exposing an interoperable contract.

---

# 39. What Is a Data Contract?

A data contract is an explicit agreement describing the expected structure,
types, constraints and semantics of data exchanged between systems.

In GroceryPulse, Pydantic models define the canonical contracts and JSON Schema
provides a machine-readable representation.

---

# 40. How Do You Prevent Schema Drift?

Pydantic models are the canonical source.

JSON schemas are generated from those models.

CI regenerates the schemas and performs a Git diff. If a developer changes the
model without updating the committed generated contract, CI fails.

---

# 41. What Is the Difference Between Determinism and Idempotency?

Determinism means the same input produces the same output.

Idempotency means repeating an operation does not continue changing the final
state.

The GroceryPulse schema-generation process demonstrates both principles.

---

# 42. How Do You Maintain Code Quality?

I use layered controls.

Pre-commit provides fast local checks.

`make quality` performs formatting, linting, strict type checking, tests, coverage,
security auditing and documentation validation.

GitHub Actions independently reproduces the controls on a clean Linux runner.

This provides defence in depth.

---

# 43. Why Not Rely Only on CI?

CI detects problems after code has already left the immediate developer feedback
loop.

Pre-commit catches inexpensive problems earlier.

The local quality gate provides comprehensive validation before pushing.

CI provides independent verification.

Each layer therefore serves a different purpose.

---

# 44. Why Isn't 100% Coverage the Target?

Coverage is useful as a guardrail but does not prove test quality.

A meaningless test can increase coverage without protecting behaviour.

I prefer meaningful tests around business invariants, failure conditions and
regression-sensitive logic.

---

# 45. How Do You Ensure Reproducibility?

I use a committed dependency lockfile and install dependencies from that controlled
dependency graph.

The same project is then validated in a clean Linux CI environment.

This reduces dependence on developer-specific machine state.

---

# 46. How Do You Handle Dependency Security?

I combine deterministic dependency management with vulnerability scanning and
automated dependency-update proposals.

`pip-audit` checks known vulnerabilities, Dependabot proposes updates and `uv.lock`
controls dependency resolution.

---

# 47. Why Generate JSON Schema Instead of Maintaining It Manually?

Maintaining the Python models and JSON schemas independently would create two
sources of truth.

Instead, the Pydantic domain models are authoritative and JSON schemas are derived
from them.

This reduces duplication and provides automated drift detection.

---

# 48. What Does Fail Fast Mean in GroceryPulse?

Fail fast means detecting invalid data close to the point where it enters a system
rather than allowing it to travel through multiple downstream layers.

In GroceryPulse, canonical Pydantic contracts provide early structural and
business-rule validation.

The objective is to prevent bad data from contaminating downstream storage,
transformations, analytics and ML workloads.

---

# 49. What Is Defence in Depth?

Defence in depth means using multiple independent controls rather than relying on
one mechanism.

In GroceryPulse:

```text
Pre-commit
     ↓
Local quality gate
     ↓
GitHub Actions CI
```

provide separate layers of verification.

---

# 50. What Does Shift Left Mean?

Shift left means moving quality, security and validation activities earlier in the
development lifecycle.

For example, a formatting or configuration error caught by pre-commit is cheaper
to resolve than the same problem discovered after deployment.

---

# PART VIII — INTERVIEW ANSWERS BY LENGTH

# 51. 30-Second Version

I am building GroceryPulse as a production-style retail Data, ML and GenAI
platform. I started by defining business grain and canonical Pydantic data
contracts rather than jumping directly into ETL. Those contracts generate
deterministic JSON schemas, and CI detects schema drift automatically. I also
implemented layered quality controls using Ruff, strict mypy, pytest, coverage,
pip-audit, pre-commit and GitHub Actions with reproducible dependencies managed by
uv.

---

# 52. 60-Second Version

I am building GroceryPulse as a production-style retail Data, ML and GenAI
platform rather than simply a collection of ETL scripts.

I started by defining explicit business grain and canonical domain contracts using
Pydantic, including strict validation and business invariants. Those models are the
source of truth and deterministically generate JSON Schema contracts. CI
regenerates those schemas and detects contract drift automatically.

I then established layered engineering controls: Ruff for formatting and linting,
strict mypy for static typing, pytest with an 85% coverage gate, pip-audit for
dependency vulnerability scanning, pre-commit for shift-left validation, and
MkDocs with mkdocstrings for documentation as code.

Dependencies are reproducible using uv and a committed lockfile. GitHub Actions
then independently reproduces the quality gate on a clean Linux runner, while
CODEOWNERS and Dependabot provide repository governance and dependency lifecycle
management.

---

# 53. Two-Minute Architecture Discussion

GroceryPulse is being built as a production-style retail data platform rather than
as a single pipeline.

The first design step was domain modelling. I defined the grain and keys of core
retail entities before implementing ingestion because unclear grain eventually
causes analytical problems such as join fan-out and double counting.

I then created canonical Store, Product, Customer and Supplier contracts using
Pydantic. These models enforce structural validation and domain invariants and act
as the source of truth for generated JSON Schema contracts.

The schema-generation process is deterministic and idempotent. CI regenerates the
schemas and checks for Git differences, which means contract drift is detected
automatically.

Around the implementation I built layered engineering controls. Ruff handles
formatting and linting, mypy runs in strict mode, pytest verifies contract
behaviour with an 85% coverage threshold, and pip-audit scans dependencies.
Pre-commit shifts cheap quality checks left into the developer workflow.

The full quality gate is then reproduced by GitHub Actions on a clean Linux runner,
which verifies that the project does not depend on hidden state on my development
machine.

The next stages extend this controlled foundation into synthetic retail data,
AWS S3, PySpark, Snowflake, dbt, Airflow, Kafka, ML and GenAI.

---

# PART IX — VERIFIED PROJECT EVIDENCE

# 54. Current Engineering Evidence

Current verified baseline:

```text
Automated tests                     13 passing
Total test coverage                 90.13%
Minimum coverage gate               85%
Ruff                                Passing
mypy strict                         Passing
pip-audit                           No known dependency vulnerabilities
Pre-commit                          Passing
MkDocs strict build                 Passing
JSON Schema generation              Deterministic
Schema drift detection              CI enforced
CODEOWNERS                          Enabled
Dependabot                          Enabled
GitHub Actions                      Passing
Clean Linux CI                      Verified
```

These figures should be updated as the project evolves.

---

# 55. Important Git Milestones

The engineering baseline was deliberately separated into logical commits:

```text
feat: establish canonical retail data contracts

chore: establish production quality tooling

docs: establish professional developer documentation

ci: add repository governance and quality checks

ci: verify GitHub Actions trigger
```

This separates:

```text
Feature implementation
        ↓
Engineering tooling
        ↓
Documentation
        ↓
CI / governance
```

and creates an understandable and auditable Git history.

---

# PART X — FUTURE PLATFORM JOURNEY

# 56. Planned Architecture Sequence

```text
Canonical Data Contracts
          ↓
Synthetic Retail Sources
          ↓
Batch + Event Ingestion
          ↓
Kafka / MSK
          ↓
AWS S3 Bronze
          ↓
PySpark Transformation
          ↓
S3 Silver / Gold
          ↓
Snowflake
          ↓
dbt
          ↓
Airflow / MWAA
          ↓
Data Quality + Observability
          ↓
Feature Engineering
          ↓
SageMaker ML
          ↓
Bedrock GenAI
          ↓
QuickSight
```

The sequence may evolve as implementation decisions are made.

---

# 57. Future Data Lake / S3 Concepts

The following concepts should be added to the verified interview evidence only
after they are implemented and understood:

- Bronze / Silver / Gold architecture
- Partitioning
- Partition pruning
- Small-file problem
- Object-store semantics
- Data lifecycle
- Parquet
- Columnar storage
- Predicate pushdown

---

# 58. Future Kafka Concepts

Future concepts include:

- Event-driven architecture
- Producer
- Consumer
- Consumer group
- Partition
- Partition key
- Offset
- Ordering
- Delivery semantics
- Duplicate delivery
- Idempotent consumer
- Dead-letter queue
- Backpressure
- Schema evolution

---

# 59. Future PySpark Concepts

Future concepts include:

- Lazy evaluation
- DAG
- Shuffle
- Narrow transformation
- Wide transformation
- Partitioning
- Data skew
- Predicate pushdown
- Catalyst optimiser
- Adaptive Query Execution
- Broadcast joins

---

# 60. Future Snowflake Concepts

Future concepts include:

- Separation of storage and compute
- Virtual warehouse
- Micro-partition
- Pruning
- Clustering
- Time Travel
- Streams
- Tasks
- Zero-copy cloning
- Cost governance

---

# 61. Future dbt Concepts

Future concepts include:

- Staging layer
- Intermediate layer
- Marts
- Incremental model
- Tests
- Lineage
- Documentation
- SCD Type 2
- Semantic modelling

---

# 62. Future Airflow Concepts

Future concepts include:

- DAG
- Task dependency
- Idempotent task
- Retry
- Backfill
- Catchup
- Scheduling
- Orchestration
- Failure recovery

---

# 63. Future Data Quality and Observability Concepts

Future concepts include:

- Completeness
- Validity
- Uniqueness
- Referential integrity
- Freshness
- Reconciliation
- Quarantine
- Observability
- Data lineage
- SLA
- SLO

---

# 64. Future Infrastructure-as-Code Concepts

Future concepts include:

- Terraform
- Infrastructure as Code
- Declarative infrastructure
- State management
- Remote state
- Plan
- Apply
- Drift detection
- Reusable modules
- Environment isolation

---

# 65. Future ML / SageMaker Concepts

Future concepts include:

- Feature engineering
- Training pipeline
- Model registry
- Model deployment
- Model monitoring
- Data drift
- Model drift
- MLOps

The first planned GroceryPulse ML use case is:

```text
SKU × Store × Day
        ↓
Demand Forecast
```

A later use case will estimate:

```text
Probability of stock-out
within the next 24 hours
```

---

# 66. Future GenAI / Bedrock Concepts

Future concepts include:

- Retrieval-Augmented Generation
- RAG
- Embeddings
- Vector retrieval
- Tool calling
- Grounding
- Hallucination control
- Guardrails
- Governed access

The planned application is a:

**GroceryPulse AI Operations Copilot**

The objective is to provide governed access to trusted operational and analytical
information rather than allowing an LLM unrestricted access to raw enterprise
data.

---

# PART XI — ENGINEERING DECISION FRAMEWORK

# 67. How Future Decisions Should Be Recorded

For every significant architectural decision:

```text
Business Requirement
        ↓
Engineering Constraints
        ↓
Options Considered
        ↓
Trade-Off Analysis
        ↓
Selected Design
        ↓
Implementation
        ↓
Failure Modes
        ↓
Controls
        ↓
Testing
        ↓
Observability
        ↓
Interview Explanation
```

This prevents GroceryPulse from becoming a technology checklist.

The objective is to demonstrate **engineering judgement**.

---

# PART XII — DEFINITION OF DONE

# 68. Definition of Done for Future GroceryPulse Milestones

A major GroceryPulse work item should not be considered complete merely because
the code works.

Where applicable, the Definition of Done includes:

```text
Implementation                         ✓
Business rules                         ✓
Automated tests                        ✓
Negative/failure tests                 ✓
Static analysis                        ✓
Type checking                          ✓
Security considerations                ✓
Documentation                          ✓
What-I-Learned entry                   ✓
Interview Playbook update              ✓
Architecture update                    ✓
Quality gate                           ✓
Git commit                             ✓
CI verification                        ✓
```

---

# PART XIII — INTERVIEW STORY CAPTURE TEMPLATE

# 69. Template for Every Important Future Milestone

## Problem

What business or engineering problem were we solving?

## Constraints

What limitations or requirements affected the solution?

## Options Considered

What alternative approaches were available?

## Decision

What approach was selected?

## Why

Why was it selected?

## Implementation

How was it implemented?

## Failure Modes

What could go wrong?

## Controls

How were those risks controlled?

## Testing

How was correctness verified?

## Observability

How would we know the component is healthy in production?

## Production Considerations

What would matter at production scale?

## Lessons Learned

What did I learn?

## Interview Explanation

How would I explain this in 30–60 seconds?

---

# PART XIV — KNOWLEDGE DISCIPLINE

# 70. Rule for Technical Terminology

Advanced terminology should only become part of my interview vocabulary when it
has either:

1. been implemented in GroceryPulse, or
2. been explicitly studied and understood as part of an upcoming design decision.

Do not use terminology simply because it sounds impressive.

An interviewer may probe any technical term several levels deeper.

Every important technical term should eventually connect to:

```text
Concept
   ↓
Why it exists
   ↓
Where GroceryPulse uses it
   ↓
Implementation evidence
   ↓
Failure scenario
   ↓
Trade-off
   ↓
Interview explanation
```

---

# 71. Interviewer's "Why?" Rule

For every major technology or design decision, I should be prepared to answer at
least these questions:

```text
Why did you use it?

Why not the alternative?

What problem does it solve?

What are its limitations?

How can it fail?

How do you detect failure?

How do you recover?

How does it behave at scale?

What does it cost?

How do you secure it?

How did you test it?
```

Being able to answer these questions is more important than memorising product
features.

---

# 72. Architecture Trade-Off Discipline

Architecture decisions should not be presented as universally correct choices.

Instead, explain:

```text
Requirement
    +
Constraints
    ↓
Trade-offs
    ↓
Decision
```

For example, rather than saying:

> "Kafka is the best messaging technology."

the eventual interview explanation should be:

> "For this workload I selected Kafka because the requirements included durable
> event streams, partitioned throughput and independent consumers. I then had to
> design around ordering scope, duplicate delivery, partition-key selection,
> consumer lag and operational complexity."

This demonstrates engineering judgement rather than technology preference.

---

# 73. Production Mindset

For each future component, think beyond the happy path.

Ask:

```text
What happens when input is malformed?

What happens when a dependency is unavailable?

What happens when processing is repeated?

What happens when processing is late?

What happens when data arrives out of order?

What happens when the schema changes?

What happens when volume increases 10×?

What happens when only part of the pipeline succeeds?

Can the operation be safely retried?

How is bad data isolated?

How do we know something has failed?

How do we recover without corrupting data?
```

These questions will become increasingly important when GroceryPulse introduces
Kafka, Spark, Airflow, Snowflake and AWS services.

---

# 74. Evidence-Based Interviewing

Where possible, interview answers should point to actual GroceryPulse evidence.

For example:

```text
Claim:
"I implemented automated schema-drift detection."

Evidence:
.github/workflows/ci.yml
schemas/json/
src/grocerypulse/schemas/export.py
```

Or:

```text
Claim:
"I use strict static typing."

Evidence:
pyproject.toml
[tool.mypy]
strict = true
```

Or:

```text
Claim:
"I enforce business invariants."

Evidence:
src/grocerypulse/models/entities.py
tests/test_entities.py
```

This makes interview explanations concrete and defensible.

---

# 75. Final Guiding Principle

The weakest GroceryPulse interview answer would be:

> "I used AWS, Kafka, Snowflake, dbt, Airflow and PySpark."

A stronger engineering answer demonstrates:

> "I understand why the architecture was designed this way, the trade-offs
> involved, how data correctness is protected, how the system can fail, how those
> failures are detected and recovered from, and how I can demonstrate that the
> platform behaves correctly."

The goal of this playbook is to preserve that engineering story throughout the
entire GroceryPulse project.
