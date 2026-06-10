from http import HTTPStatus
from httpx import Response
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.dependencies import get_db
from sqlalchemy.orm import Session
from app.models.user import User as UserModel
from app.models.book import Book

endpoint = "/books"
# Harry Potter e a Pedra Filosofal
test_isbn = "9788532511010"
user_data = {
    "username": "admin_test",
    "full_name": "Admin User",
    "email": "admin_test@gmail.com",
    "password": "password123",
}
body = {"isbn": test_isbn, "stock": 10}


@pytest.fixture
def client() -> TestClient:
    return TestClient(app=app)


@pytest.fixture
def get_admin_token(client: TestClient) -> str:
    """Registers a user, makes them admin in the DB, and returns the Bearer token."""
    client.post("/auth/signup", json=user_data)
    from app.db.database import SessionLocal

    db: Session = SessionLocal()
    user = db.query(UserModel).filter(UserModel.email == user_data["email"]).first()
    if user:
        user.is_admin = True
        db.commit()
    db.close()

    # Login - OAuth2PasswordRequestForm uses 'username' field for the identifier (email)
    res: Response = client.post(
        "/auth/login",
        data={"username": user_data["email"], "password": user_data["password"]},
    )

    if res.status_code != HTTPStatus.OK:
        raise Exception(f"Login failed with status {res.status_code}: {res.text}")

    return f"Bearer {res.json()['access_token']}"


@pytest.fixture
def setup_book(client: TestClient, get_admin_token) -> Response:
    res = client.post(
        f"{endpoint}/import",
        json=body,
        headers={"Authorization": get_admin_token},
    )
    return res


@pytest.fixture
def clear_book(client: TestClient, get_admin_token):
    """Teardown fixture to ensure the test book is removed."""
    client.delete(f"{endpoint}/{test_isbn}", headers={"Authorization": get_admin_token})
    yield
    client.delete(f"{endpoint}/{test_isbn}", headers={"Authorization": get_admin_token})


@pytest.fixture
def clear_book_after(client: TestClient, get_admin_token):
    yield
    client.delete(f"{endpoint}/{test_isbn}", headers={"Authorization": get_admin_token})


def test_import_book(client: TestClient, get_admin_token, clear_book, setup_book):
    res = setup_book
    assert res.status_code == HTTPStatus.CREATED
    data = res.json()
    assert data["isbn"] == test_isbn
    assert data["title"] == "Harry Potter e a Pedra Filosofal"
    assert data["stock"] == 10


def test_get_book_by_isbn(client: TestClient, clear_book, setup_book):
    res = client.get(f"{endpoint}/{test_isbn}")
    assert res.status_code == HTTPStatus.OK
    assert res.json()["isbn"] == test_isbn


def test_get_all_books(client: TestClient, get_admin_token, clear_book):
    # Ensure at least one book exists
    client.post(
        f"{endpoint}/import",
        json={"isbn": test_isbn, "stock": 1},
        headers={"Authorization": get_admin_token},
    )

    res = client.get(f"{endpoint}/")
    assert res.status_code == HTTPStatus.OK
    assert isinstance(res.json(), list)
    assert len(res.json()) >= 1


def test_add_book_stock(client: TestClient, get_admin_token, clear_book, setup_book):
    # Add stock
    value = 10
    total_stock = body["stock"] + value
    res = client.patch(
        f"{endpoint}/add-stock/{test_isbn}",
        json={"stock": value},
        headers={"Authorization": get_admin_token},
    )
    assert res.status_code == HTTPStatus.OK
    assert res.json()["stock"] == total_stock


def test_edit_book(client: TestClient, get_admin_token, clear_book, setup_book):

    # Edit
    new_title = "Harry Potter - Updated Title"
    res = client.put(
        f"{endpoint}/{test_isbn}",
        json={"title": new_title},
        headers={"Authorization": get_admin_token},
    )
    assert res.status_code == HTTPStatus.OK
    assert res.json()["title"] == new_title


def test_remove_book(client: TestClient, get_admin_token):
    # Import
    client.post(
        f"{endpoint}/import",
        json={"isbn": test_isbn, "stock": 5},
        headers={"Authorization": get_admin_token},
    )

    # Remove
    res = client.delete(
        f"{endpoint}/{test_isbn}",
        headers={"Authorization": get_admin_token},
    )
    assert res.status_code == HTTPStatus.OK

    # Verify it's gone
    get_res = client.get(f"{endpoint}/{test_isbn}")
    assert get_res.status_code == HTTPStatus.NOT_FOUND


def test_unauthorized_import(client: TestClient):
    res = client.post(f"{endpoint}/import", json={"isbn": test_isbn})
    assert res.status_code == HTTPStatus.UNAUTHORIZED
