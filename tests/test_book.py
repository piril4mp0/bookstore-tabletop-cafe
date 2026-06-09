from http import HTTPStatus
from httpx import Response
import pytest
import uuid
from fastapi.testclient import TestClient
from app.main import app

endpoint = "/books"
test_isbn = "9780261103283"


@pytest.fixture
def client() -> TestClient:
    return TestClient(app=app)


@pytest.fixture
def seed_db_with_book(client: TestClient) -> Response:
    book = {"isbn": test_isbn, "stock": 0}
    return client.post(endpoint, json=book)


@pytest.fixture
def clear_db(client: TestClient):
    client.delete(f"{endpoint}/remove/{test_isbn}")
    client.get(f"{endpoint}/{test_isbn}")
