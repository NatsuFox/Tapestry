# Tapestry Tests

Unit tests for the Tapestry skill pack.

## Running Tests

```bash
# Run the local CI command that mirrors .github/workflows/tests.yml
./tools/run_local_ci.sh

# Install the pre-commit hook so every commit runs the same check
./tools/install_git_hooks.sh

# Run a specific test file
python3 -m pytest tests/test_parse.py

# Run with coverage
python3 -m pytest tests/ --cov=skills/tapestry/_src --cov-report=html

# Run with verbose output
python3 -m pytest -v tests/
```

## Test Structure

- `test_parse.py`: Tests for HTML parsing and content extraction
- `test_ingest.py`: Tests for ingestion workflow
- `test_router.py`: Tests for crawler routing and matching
- `conftest.py`: Shared pytest fixtures
- `fixtures/`: Test data and mock HTML files

## Writing Tests

Tests use pytest and should follow these conventions:

```python
def test_feature_name():
    # Arrange
    input_data = ...

    # Act
    result = function_under_test(input_data)

    # Assert
    assert result == expected_value
```

## Test Coverage

Run tests with coverage to ensure code quality:

```bash
python3 -m pytest tests/ --cov=skills/tapestry/_src --cov-report=html
open htmlcov/index.html
```
