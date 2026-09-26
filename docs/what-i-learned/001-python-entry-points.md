# Python Entry Points

## What I learned

A Python module can be used in two main ways:

1. It can be imported by another Python module.
2. It can be executed directly as a program.

Python provides the special variable `__name__` so a module can determine which of these situations is occurring.

A common entry-point pattern is:

```python
def main() -> None:
    """Run the application."""
    print("Starting GroceryPulse")


if __name__ == "__main__":
    main()
```

When the file is executed directly, Python assigns:

```python
__name__ == "__main__"
```

and therefore calls `main()`.

When the module is imported, `__name__` contains the module's import name instead, so the entry-point block is not executed automatically.

## Why does this matter?

Separating reusable application logic from program startup behaviour makes Python code easier to:

- import,
- test,
- reuse,
- maintain,
- package,
- and execute safely.

Without an entry-point guard, code placed at module level may execute unexpectedly whenever the module is imported.

For example, this is undesirable:

```python
print("Generating GroceryPulse data")
generate_data()
```

Importing that module from a test could unexpectedly generate data.

A safer structure is:

```python
def main() -> None:
    """Run the GroceryPulse data generation process."""
    generate_data()


if __name__ == "__main__":
    main()
```

Tests can now import functions from the module without triggering the application automatically.

## Running a module with `python -m`

Instead of executing a Python file by filesystem path, GroceryPulse generally runs package modules using:

```bash
uv run python -m grocerypulse.some_module
```

For example:

```bash
uv run python -m grocerypulse.schemas.export
```

This tells Python to locate and execute the module using the package import system.

This is particularly useful with a `src/` project layout because it keeps execution consistent with normal Python package imports.

## Why use a `main()` function?

Using a dedicated `main()` function provides a clear boundary between:

- program startup,
- reusable business logic,
- and testable functions.

For example:

```python
def main() -> None:
    """Run the command-line workflow."""
    ...


if __name__ == "__main__":
    main()
```

The function can also be called explicitly by a test if required.

This structure becomes increasingly valuable as GroceryPulse develops command-line utilities for tasks such as:

- schema generation,
- synthetic data generation,
- dataset export,
- data-quality checks,
- ingestion,
- and operational jobs.

## GroceryPulse example

GroceryPulse uses Python modules as executable utilities where appropriate.

The general flow is:

```text
Terminal
   |
   v
python -m grocerypulse.<module>
   |
   v
module loaded
   |
   v
__name__ == "__main__"
   |
   v
main()
   |
   v
application logic
```

The entry point should remain thin.

Complex business logic should normally live in reusable functions or classes rather than directly inside:

```python
if __name__ == "__main__":
```

That makes the implementation easier to test and reuse.

## Initial mistake / learning point

It is easy when learning Python to treat a `.py` file as if it were simply a script.

Production applications usually benefit from thinking in terms of **modules, packages, APIs, and explicit entry points** instead.

The important distinction is:

```text
script-oriented thinking
    file executes everything

package-oriented thinking
    module exposes reusable behaviour
    entry point explicitly starts the application
```

GroceryPulse follows the second approach.

## Production consideration

As GroceryPulse grows, some executable modules may eventually become formal command-line interfaces or scheduled jobs.

For example:

```text
developer CLI
      |
      +--> generate synthetic data
      +--> export schemas
      +--> run validation
      +--> bootstrap development data
```

Later cloud workloads may invoke the same underlying application logic from:

- AWS Lambda,
- Airflow,
- AWS Glue,
- containers,
- CI/CD pipelines,
- or scheduled services.

The entry mechanism can change while the core business logic remains reusable.

## Interview questions

### What does `if __name__ == "__main__":` do?

It ensures that a block of code executes only when the Python module is run directly, rather than when it is imported by another module.

### Why put application startup logic inside `main()`?

It creates a clean boundary between executable behaviour and reusable code, which improves testability and maintainability.

### Why use `python -m`?

It executes a module using Python's package/import system and is generally safer for package-based projects than relying on filesystem-relative execution.

### Why is this relevant to Data Engineering?

Data Engineering repositories commonly contain executable modules for ingestion, transformation, validation, schema management, dataset generation, orchestration utilities, and operational jobs. Clear entry points make those components easier to test and automate.

## Key takeaway

A Python entry point is not merely syntax.

It establishes a clean boundary between:

```text
reusable code
     and
executable application behaviour
```

That boundary becomes increasingly important as a small Python project evolves into a production data platform.
