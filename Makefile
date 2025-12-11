.PHONY: install upgrade check fix format lint type-check spell-check test clean run

# Install all dependencies
install:
	uv sync --all-groups

# Upgrade all dependencies to their latest versions
upgrade:
	uv sync --all-groups --upgrade

# Run all checks
check: format lint type-check spell-check

# Auto-fix formatting and linting issues
fix:
	uv run ruff format .
	uv run ruff check --fix .

# Format code
format:
	uv run ruff format .

# Run linter
lint:
	uv run ruff check .

# Run type checker
type-check:
	uv run pyright

# Run spell checker
spell-check:
	uv run typos

# Run unit tests
test:
	uv run pytest tests/

# Run tests with coverage
test-coverage:
	uv run pytest --cov=. --cov-report=term-missing --cov-report=html tests/

# Clean build artifacts and caches
clean:
	rm -rf .venv
	rm -rf .ruff_cache
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Run the Streamlit app
run:
	uv run streamlit run app.py
