from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient

from tests.constants import *


@pytest.mark.core
def test_import_book(client: TestClient, imported_book):
	res = imported_book
	assert res.status_code == HTTPStatus.CREATED
	data = res.json()
	assert data["isbn"] == BOOK_DATA["isbn"]
	assert data["title"] == BOOK_DATA["title"]
	assert data["stock"] == 10


@pytest.mark.core
def test_get_book_by_isbn(client: TestClient, imported_book):
	res = client.get(f"{BOOK_ENDPOINT}/{BOOK_DATA['isbn']}")
	assert res.status_code == HTTPStatus.OK
	assert res.json()["isbn"] == BOOK_DATA["isbn"]


@pytest.mark.core
def test_get_all_books(client: TestClient, imported_book):
	res = client.get(f"{BOOK_ENDPOINT}/")
	assert res.status_code == HTTPStatus.OK
	assert isinstance(res.json(), list)


@pytest.mark.core
def test_add_book_stock(client: TestClient, admin_headers, imported_book):
	value = 10
	total_stock = BOOK_IMPORT_BODY["stock"] + value
	res = client.patch(
		f"{BOOK_ENDPOINT}/add-stock/{BOOK_DATA['isbn']}",
		json={"stock": value},
		headers=admin_headers,
	)
	assert res.status_code == HTTPStatus.OK
	assert res.json()["stock"] == total_stock


@pytest.mark.core
def test_edit_book(client: TestClient, get_admin_token, imported_book):
	new_title = "Harry Potter - Updated Title"
	res = client.put(
		f"{BOOK_ENDPOINT}/{BOOK_DATA['isbn']}",
		json={"title": new_title},
		headers={"Authorization": get_admin_token},
	)
	assert res.status_code == HTTPStatus.OK
	assert res.json()["title"] == new_title


@pytest.mark.core
def test_remove_book(client: TestClient, get_admin_token, imported_book):
	res = client.delete(
		f"{BOOK_ENDPOINT}/{BOOK_DATA['isbn']}",
		headers={"Authorization": get_admin_token},
	)
	assert res.status_code == HTTPStatus.OK
	get_res = client.get(f"{BOOK_ENDPOINT}/{BOOK_DATA['isbn']}")
	assert get_res.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.core
def test_unauthorized_import(client: TestClient):
	res = client.post(f"{BOOK_ENDPOINT}/import", json={"isbn": BOOK_DATA["isbn"]})
	assert res.status_code == HTTPStatus.UNAUTHORIZED
