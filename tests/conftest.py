"""Shared fixtures for the FastAPI backend tests."""

import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture
def client():
    """A TestClient for the FastAPI app."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def restore_activities():
    """Snapshot the in-memory activities database and restore it after each test.

    Signup/unregister endpoints mutate the global `activities` dict, so each
    test must start from a clean, known state.
    """
    snapshot = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(snapshot)
