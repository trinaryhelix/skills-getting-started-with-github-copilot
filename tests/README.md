# Backend API Tests

This directory contains pytest tests for the FastAPI backend of the Mergington High School Activities Management System.

## Running Tests

### Run all tests
```bash
pytest
```

### Run tests with verbose output
```bash
pytest -v
```

### Run specific test class
```bash
pytest tests/test_activities_endpoints.py::TestGetActivities
```

### Run specific test function
```bash
pytest tests/test_activities_endpoints.py::TestSignupForActivity::test_signup_duplicate_prevention
```

### Run tests matching a keyword
```bash
pytest -k "duplicate"
```

### Run with coverage report (requires pytest-cov)
```bash
pip install pytest-cov
pytest --cov=src --cov-report=html
```

## Test Structure

Tests are organized by endpoint and follow the **AAA (Arrange-Act-Assert) pattern**:

- **Arrange**: Set up test data and preconditions
- **Act**: Execute the code/endpoint being tested
- **Assert**: Verify the results match expectations

### Test Classes

- **TestGetActivities** — Tests for `GET /activities`
  - Verify all activities returned
  - Verify correct data structure
  - Verify participant data format

- **TestSignupForActivity** — Tests for `POST /activities/{activity_name}/signup`
  - Valid signup scenarios
  - Duplicate prevention
  - Activity not found errors
  - Edge cases with special characters and multiple signups

- **TestRemoveFromActivity** — Tests for `POST /activities/{activity_name}/remove`
  - Valid removal scenarios
  - Student not enrolled errors
  - Activity not found errors
  - Duplicate removal prevention

- **TestRootEndpoint** — Tests for `GET /`
  - Verify redirect behavior

## Test Coverage

Current test coverage:
- ✓ GET /activities (4 tests)
- ✓ POST /activities/{name}/signup (6 tests)
- ✓ POST /activities/{name}/remove (5 tests)
- ✓ GET / (1 test)
- **Total: 16 tests**

## Test Fixtures

### client (conftest.py)
Provides a FastAPI `TestClient` instance for making HTTP requests to the API during tests.

```python
@pytest.fixture
def client():
    """Fixture providing a FastAPI test client for making HTTP requests."""
    return TestClient(app)
```

## Adding New Tests

1. Add test methods to the appropriate test class
2. Use the `client` fixture for HTTP requests
3. Follow the AAA pattern with explicit comments:
   ```python
   def test_example(self, client):
       # Arrange
       data = {"example": "setup"}
       
       # Act
       response = client.post("/endpoint", json=data)
       
       # Assert
       assert response.status_code == 200
   ```
4. Include docstrings explaining the test purpose
5. Use descriptive test names: `test_<what_you_are_testing>`
6. Run `pytest -v` to verify new test is discovered and passes

## Notes

- Tests use the `TestClient` from `fastapi.testclient` for making HTTP requests
- In-memory data is reset between test runs (TestClient creates a fresh app instance)
- Each test is independent and can run in any order
- The in-memory activities dictionary is shared across tests but this doesn't affect test isolation since TestClient creates a fresh instance per client fixture

## Troubleshooting

### Tests not discovered
- Ensure files are named `test_*.py`
- Ensure test functions are named `test_*`
- Run `pytest --collect-only` to list all discovered tests

### Import errors
- Make sure pytest is installed: `pip install -r requirements.txt`
- Verify the `tests/` directory has an `__init__.py` file
- Check that `conftest.py` is in the `tests/` directory

### Tests failing due to shared state
- If tests are modifying shared in-memory activities, consider:
  - Using unique email addresses per test (recommended)
  - Adding a fixture to reset activities between tests (if needed)
