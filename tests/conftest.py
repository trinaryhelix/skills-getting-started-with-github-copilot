"""Pytest configuration and shared fixtures for the test suite."""
import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Fixture providing a FastAPI test client for making HTTP requests."""
    return TestClient(app)
