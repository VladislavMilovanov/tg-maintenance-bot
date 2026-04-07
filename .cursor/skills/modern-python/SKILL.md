---
name: modern-python
description: Apply modern Python 3.12+ practices with uv, ruff, strong typing, async-first design, and production-grade project conventions.
---

# Modern Python

Use this skill for Python application code, utilities, services, and refactors that should follow current Python conventions instead of legacy patterns.

## Standards

- Target Python 3.12+ idioms by default.
- Prefer `uv` for dependency and task execution when the project supports it.
- Use `ruff` for linting and formatting.
- Write explicit type hints for public functions, service boundaries, and domain models.
- Prefer `pathlib`, `datetime`, `enum`, `dataclasses`, and other stdlib tools before adding dependencies.
- Keep functions small, side effects explicit, and error handling intentional.

## Code Style

- Use `X | None` instead of `Optional[X]` unless compatibility requires otherwise.
- Use built-in generics like `list[str]`, `dict[str, Any]`.
- Prefer `match` when it materially improves clarity.
- Use f-strings over older interpolation styles.
- Replace ad-hoc dictionaries with typed models where the shape matters.
- Avoid boolean flag arguments when an enum or separate function makes intent clearer.

## Architecture Guidance

- Keep I/O at the edges and business rules in plain Python functions or services.
- Prefer dependency injection over hidden globals.
- Separate schemas, domain logic, persistence, and transport concerns.
- For async code, stay async end-to-end and avoid blocking libraries in request paths.
- Use explicit config objects or settings models instead of scattered environment reads.

## Tooling Baseline

```toml
[tool.ruff]
target-version = "py312"
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]
```

```toml
[tool.pyright]
pythonVersion = "3.12"
typeCheckingMode = "standard"
```

## Review Checklist

1. Remove outdated typing syntax and pre-3.10 compatibility noise when unnecessary.
2. Replace mutable default arguments and hidden state.
3. Make exceptions domain-specific where error handling matters.
4. Check async boundaries for blocking calls.
5. Reduce overly clever abstractions and duplicate utility layers.
6. Prefer tested, composable functions over framework-coupled logic.

## Expected Output

When using this skill:

- Suggest concrete refactors, not generic style advice.
- Prefer small, safe improvements that fit the existing codebase.
- Highlight correctness, readability, typing, and operability issues.
- If the code is already strong, say so and only recommend meaningful upgrades.
