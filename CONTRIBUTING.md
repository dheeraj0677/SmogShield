# Contributing to SmogShield

Thank you for contributing to **SmogShield**! Please follow these engineering standards so every pull request keeps our quality, security, and accessibility bars high.

## Code Standards
- **Module size:** Keep every source module at or below **200 lines**. Split cohesive helpers into dedicated modules when approaching this limit.
- **Python (`backend/`):**
  - Type-annotate all functions, methods, and parameters.
  - Include concise Google-style docstrings on all modules, classes, and functions.
  - Format & lint with Ruff (`python -m ruff check backend`).
- **JavaScript / React (`frontend/src/`):**
  - Document exported hooks, services, and helpers with JSDoc comments.
  - Keep `0` ESLint & `eslint-plugin-jsx-a11y` errors (`npx eslint src`).
  - Maintain WCAG 2.1 AA compliance (`0` `@axe-core/playwright` violations).

## Running Tests
```bash
# Backend unit & integration tests with coverage
python -m pytest backend/tests --cov=backend --cov-report=term-missing

# Frontend unit tests with coverage
cd frontend && npx vitest run --coverage
```

## Security & Secrets
- Never commit `.env` files, API keys, or credentials.
- Verify `git diff --cached --name-only` before pushing.
