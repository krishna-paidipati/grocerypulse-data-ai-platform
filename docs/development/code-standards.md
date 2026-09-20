# GroceryPulse Engineering Standards

## Source ownership

Repository ownership is enforced through `.github/CODEOWNERS`.

Important source modules additionally identify the responsible code owner and
component in their module documentation.

## Documentation

Every public Python module, class, method, and function must have an
appropriate docstring.

Google-style docstrings are the project standard.

Documentation must explain intent, contracts, business assumptions, parameters,
return values, and meaningful exceptions.

Inline comments should explain non-obvious reasoning rather than restating code.

## Type safety

All production Python functions must have complete type annotations.

Static typing is validated with mypy strict mode.

## Formatting and linting

Ruff is the canonical formatter and linter.

Developers must not manually maintain alternative formatting conventions.

## Testing

Business rules require tests.

Bug fixes should include a regression test whenever practical.

Tests must remain deterministic and independent of execution order.

## Security

Secrets, credentials, tokens, passwords, and private keys must never be
committed.

Dependencies are audited for known vulnerabilities.

## Dependency management

`pyproject.toml` defines dependency requirements.

`uv.lock` records the reproducible dependency resolution.

Both must remain synchronized.

## Generated artifacts

Generated files must identify their source of truth and should never be edited
manually unless explicitly documented.
