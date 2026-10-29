import os
import tempfile

# Use a throwaway SQLite database for tests (must be set before the app is imported).
_tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp.name}"
os.environ["ADMIN_USER"] = "tester"
os.environ["ADMIN_PASSWORD"] = "test-pass"

import pytest
from fastapi.testclient import TestClient

from app.main import app, contact_limiter, subscribe_limiter
from app.seed import seed


@pytest.fixture(scope="session", autouse=True)
def _seed():
    seed()


@pytest.fixture()
def client():
    contact_limiter.hits.clear()
    subscribe_limiter.hits.clear()
    with TestClient(app) as c:
        yield c
