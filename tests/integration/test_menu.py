from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient

from tests.constants import (
	CREATE_MENU_DRINK_BODY,
	CREATE_MENU_MEAL_BODY,
	MENU_ENDPOINT,
)


@pytest.mark.core
def test_create_menu_item(client: TestClient, stp_trdwn_menu_item, stp_trdwn_tag):
	res = stp_trdwn_menu_item
	assert res.status_code == HTTPStatus.CREATED
	data = res.json()
	assert data["name"] == CREATE_MENU_DRINK_BODY["name"]
	assert data["category"] == CREATE_MENU_DRINK_BODY["category"]
	assert data["price"] == CREATE_MENU_DRINK_BODY["price"]
	assert "id" in data


@pytest.mark.core
def test_create_menu_item_unauthorized(client: TestClient):
	response = client.post(MENU_ENDPOINT, json=CREATE_MENU_DRINK_BODY)
	assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.core
def test_get_all_menu_items(client: TestClient, stp_trdwn_menu_item):
	response = client.get(MENU_ENDPOINT)
	assert response.status_code == HTTPStatus.OK
	assert isinstance(response.json(), list)


@pytest.mark.core
def test_filter_menu_items_by_category(
	client: TestClient, stp_trdwn_menu_item, admin_headers: dict[str, str]
):
	# Meal item setup
	meal_res = client.post(
		MENU_ENDPOINT, json=CREATE_MENU_MEAL_BODY, headers=admin_headers
	)
	assert meal_res.status_code == HTTPStatus.CREATED
	meal_id = meal_res.json()["id"]

	try:
		drinks_res = client.get(f"{MENU_ENDPOINT}?category=drink")
		assert drinks_res.status_code == HTTPStatus.OK
		assert all(d["category"] == "drink" for d in drinks_res.json())

		meals_res = client.get(f"{MENU_ENDPOINT}?category=meal")
		assert meals_res.status_code == HTTPStatus.OK
		assert all(m["category"] == "meal" for m in meals_res.json())
	finally:
		client.delete(f"{MENU_ENDPOINT}/{meal_id}", headers=admin_headers)


@pytest.mark.core
def test_filter_menu_items_by_availability(
	client: TestClient, stp_trdwn_menu_item, admin_headers: dict[str, str]
):
	unavail_body = {
		**CREATE_MENU_DRINK_BODY,
		"name": "Unavailable Coffee",
		"is_available": False,
	}
	unavail_res = client.post(MENU_ENDPOINT, json=unavail_body, headers=admin_headers)
	assert unavail_res.status_code == HTTPStatus.CREATED
	unavail_id = unavail_res.json()["id"]

	try:
		avail_res = client.get(f"{MENU_ENDPOINT}?is_available=true")
		assert avail_res.status_code == HTTPStatus.OK
		assert all(item["is_available"] is True for item in avail_res.json())

		unavail_check = client.get(f"{MENU_ENDPOINT}?is_available=false")
		assert unavail_check.status_code == HTTPStatus.OK
		assert all(item["is_available"] is False for item in unavail_check.json())
	finally:
		client.delete(f"{MENU_ENDPOINT}/{unavail_id}", headers=admin_headers)


@pytest.mark.core
def test_filter_menu_items_by_tag(
	client: TestClient, stp_trdwn_tag, admin_headers: dict[str, str]
):
	tag_id = stp_trdwn_tag.json()["id"]
	tagged_item_body = {
		**CREATE_MENU_MEAL_BODY,
		"name": "Tagged Meal",
		"tag_ids": [tag_id],
	}
	create_res = client.post(
		MENU_ENDPOINT, json=tagged_item_body, headers=admin_headers
	)
	assert create_res.status_code == HTTPStatus.CREATED
	item_id = create_res.json()["id"]

	try:
		tagged_res = client.get(f"{MENU_ENDPOINT}?tag_id={tag_id}")
		assert tagged_res.status_code == HTTPStatus.OK
		items = tagged_res.json()
		assert len(items) >= 1
		assert any(tag["id"] == tag_id for item in items for tag in item["tags"])
	finally:
		client.delete(f"{MENU_ENDPOINT}/{item_id}", headers=admin_headers)


@pytest.mark.core
def test_get_menu_item_by_id(client: TestClient, stp_trdwn_menu_item):
	item_data = stp_trdwn_menu_item.json()
	item_id = item_data["id"]

	get_res = client.get(f"{MENU_ENDPOINT}/{item_id}")
	assert get_res.status_code == HTTPStatus.OK
	assert get_res.json()["id"] == item_id


@pytest.mark.core
def test_update_menu_item(
	client: TestClient, stp_trdwn_menu_item, admin_headers: dict[str, str]
):
	item_id = stp_trdwn_menu_item.json()["id"]
	update_body = {"price": 6.99, "stock": 50, "description": "Updated description"}
	put_res = client.put(
		f"{MENU_ENDPOINT}/{item_id}", json=update_body, headers=admin_headers
	)
	assert put_res.status_code == HTTPStatus.OK
	updated = put_res.json()
	assert updated["price"] == 6.99
	assert updated["stock"] == 50
	assert updated["description"] == "Updated description"


@pytest.mark.core
def test_patch_menu_item_availability(
	client: TestClient, stp_trdwn_menu_item, admin_headers: dict[str, str]
):
	item_id = stp_trdwn_menu_item.json()["id"]
	patch_res = client.patch(
		f"{MENU_ENDPOINT}/{item_id}/availability",
		json={"is_available": False},
		headers=admin_headers,
	)
	assert patch_res.status_code == HTTPStatus.OK
	assert patch_res.json()["is_available"] is False


@pytest.mark.core
def test_delete_menu_item(
	client: TestClient, stp_trdwn_menu_item, admin_headers: dict[str, str]
):
	item_id = stp_trdwn_menu_item.json()["id"]
	delete_res = client.delete(f"{MENU_ENDPOINT}/{item_id}", headers=admin_headers)
	assert delete_res.status_code == HTTPStatus.NO_CONTENT
	assert client.get(f"{MENU_ENDPOINT}/{item_id}").status_code == HTTPStatus.NOT_FOUND
