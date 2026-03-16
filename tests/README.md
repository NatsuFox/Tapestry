# Tapestry Tests

Unit tests for the Tapestry skill pack.

## Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_parse.py

# Run with coverage
pytest --cov=skills/tapestry tests/

# Run with verbose output
pytest -v tests/
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
pytest --cov=skills/tapestry --cov-report=html tests/
open htmlcov/index.html
```
