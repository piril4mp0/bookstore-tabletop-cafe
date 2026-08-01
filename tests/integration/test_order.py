from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient

from tests.constants import (
	MENU_ENDPOINT,
	ORDER_ENDPOINT,
)


@pytest.mark.core
def test_create_order_success(
	client: TestClient,
	admin_headers: dict[str, str],
	stp_trdwn_table,
	stp_trdwn_menu_item,
	stp_trdwn_meal_item,
):
	table_number = stp_trdwn_table.json()["number"]
	drink_id = stp_trdwn_menu_item.json()["id"]
	meal_id = stp_trdwn_meal_item.json()["id"]

	order_body = {
		"table_number": table_number,
		"notes": "Extra hot latte, please!",
		"items": [
			{"menu_item_id": drink_id, "quantity": 2},
			{"menu_item_id": meal_id, "quantity": 1},
		],
	}

	response = client.post(ORDER_ENDPOINT, json=order_body, headers=admin_headers)
	assert response.status_code == HTTPStatus.CREATED
	data = response.json()
	assert data["table_number"] == table_number
	assert data["notes"] == "Extra hot latte, please!"
	assert data["status"] == "pending"
	assert len(data["items"]) == 2
	# Total price: (4.50 * 2) + (8.00 * 1) = 17.00
	assert data["total_price"] == 17.00


@pytest.mark.core
def test_create_order_unauthorized(
	client: TestClient, stp_trdwn_table, stp_trdwn_menu_item
):
	table_number = stp_trdwn_table.json()["number"]
	drink_id = stp_trdwn_menu_item.json()["id"]

	order_body = {
		"table_number": table_number,
		"items": [{"menu_item_id": drink_id, "quantity": 1}],
	}

	response = client.post(ORDER_ENDPOINT, json=order_body)
	assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.core
def test_create_order_customer_forbidden(
	client: TestClient,
	customer_headers: dict[str, str],
	stp_trdwn_table,
	stp_trdwn_menu_item,
):
	table_number = stp_trdwn_table.json()["number"]
	drink_id = stp_trdwn_menu_item.json()["id"]

	order_body = {
		"table_number": table_number,
		"items": [{"menu_item_id": drink_id, "quantity": 1}],
	}

	response = client.post(ORDER_ENDPOINT, json=order_body, headers=customer_headers)
	assert response.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.core
def test_create_order_invalid_table(
	client: TestClient, admin_headers: dict[str, str], stp_trdwn_menu_item
):
	drink_id = stp_trdwn_menu_item.json()["id"]

	order_body = {
		"table_number": 9999,  # Non-existent table
		"items": [{"menu_item_id": drink_id, "quantity": 1}],
	}

	response = client.post(ORDER_ENDPOINT, json=order_body, headers=admin_headers)
	assert response.status_code == HTTPStatus.NOT_FOUND
	assert "Table with number 9999 does not exist" in response.json()["detail"]


@pytest.mark.core
def test_create_order_unavailable_item(
	client: TestClient,
	admin_headers: dict[str, str],
	stp_trdwn_table,
	stp_trdwn_menu_item,
):
	table_number = stp_trdwn_table.json()["number"]
	drink_id = stp_trdwn_menu_item.json()["id"]

	# Set drink availability to False
	client.patch(
		f"{MENU_ENDPOINT}/{drink_id}/availability",
		json={"is_available": False},
		headers=admin_headers,
	)

	try:
		order_body = {
			"table_number": table_number,
			"items": [{"menu_item_id": drink_id, "quantity": 1}],
		}
		response = client.post(ORDER_ENDPOINT, json=order_body, headers=admin_headers)
		assert response.status_code == HTTPStatus.BAD_REQUEST
		assert "not currently available" in response.json()["detail"]
	finally:
		# Restore availability
		client.patch(
			f"{MENU_ENDPOINT}/{drink_id}/availability",
			json={"is_available": True},
			headers=admin_headers,
		)


@pytest.mark.core
def test_get_orders_customer_forbidden(
	client: TestClient,
	customer_headers: dict[str, str],
	admin_headers: dict[str, str],
	stp_trdwn_table,
	stp_trdwn_menu_item,
):
	table_number = stp_trdwn_table.json()["number"]
	drink_id = stp_trdwn_menu_item.json()["id"]

	order_body = {
		"table_number": table_number,
		"items": [{"menu_item_id": drink_id, "quantity": 1}],
	}

	res = client.post(ORDER_ENDPOINT, json=order_body, headers=admin_headers)
	assert res.status_code == HTTPStatus.CREATED

	# Customer attempts to list orders -> 403 Forbidden
	cust_orders_res = client.get(ORDER_ENDPOINT, headers=customer_headers)
	assert cust_orders_res.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.core
def test_get_orders_admin_sees_all_orders(
	client: TestClient,
	admin_headers: dict[str, str],
	stp_trdwn_table,
	stp_trdwn_menu_item,
):
	table_number = stp_trdwn_table.json()["number"]
	drink_id = stp_trdwn_menu_item.json()["id"]

	order_body = {
		"table_number": table_number,
		"items": [{"menu_item_id": drink_id, "quantity": 1}],
	}

	# Admin places order
	res = client.post(ORDER_ENDPOINT, json=order_body, headers=admin_headers)
	assert res.status_code == HTTPStatus.CREATED
	order_id = res.json()["id"]

	# Admin lists orders -> sees order
	admin_orders_res = client.get(ORDER_ENDPOINT, headers=admin_headers)
	assert admin_orders_res.status_code == HTTPStatus.OK
	admin_orders = admin_orders_res.json()
	assert any(o["id"] == order_id for o in admin_orders)


@pytest.mark.core
def test_filter_orders_by_status_and_table(
	client: TestClient,
	admin_headers: dict[str, str],
	stp_trdwn_table,
	stp_trdwn_menu_item,
):
	table_number = stp_trdwn_table.json()["number"]
	drink_id = stp_trdwn_menu_item.json()["id"]

	order_body = {
		"table_number": table_number,
		"items": [{"menu_item_id": drink_id, "quantity": 1}],
	}
	res = client.post(ORDER_ENDPOINT, json=order_body, headers=admin_headers)
	assert res.status_code == HTTPStatus.CREATED

	# Filter by pending status and table
	filter_res = client.get(
		f"{ORDER_ENDPOINT}?status=pending&table_number={table_number}",
		headers=admin_headers,
	)
	assert filter_res.status_code == HTTPStatus.OK
	assert all(
		o["status"] == "pending" and o["table_number"] == table_number
		for o in filter_res.json()
	)


@pytest.mark.core
def test_get_order_by_id(
	client: TestClient,
	customer_headers: dict[str, str],
	admin_headers: dict[str, str],
	stp_trdwn_table,
	stp_trdwn_menu_item,
):
	table_number = stp_trdwn_table.json()["number"]
	drink_id = stp_trdwn_menu_item.json()["id"]

	order_body = {
		"table_number": table_number,
		"items": [{"menu_item_id": drink_id, "quantity": 1}],
	}
	res = client.post(ORDER_ENDPOINT, json=order_body, headers=admin_headers)
	assert res.status_code == HTTPStatus.CREATED
	order_id = res.json()["id"]

	# Customer attempts to view order detail -> 403 Forbidden
	cust_res = client.get(f"{ORDER_ENDPOINT}/{order_id}", headers=customer_headers)
	assert cust_res.status_code == HTTPStatus.FORBIDDEN

	# Admin can view order detail -> 200 OK
	admin_res = client.get(f"{ORDER_ENDPOINT}/{order_id}", headers=admin_headers)
	assert admin_res.status_code == HTTPStatus.OK
	assert admin_res.json()["id"] == order_id


@pytest.mark.core
def test_update_order_status_workflow(
	client: TestClient,
	customer_headers: dict[str, str],
	admin_headers: dict[str, str],
	stp_trdwn_table,
	stp_trdwn_menu_item,
):
	table_number = stp_trdwn_table.json()["number"]
	drink_id = stp_trdwn_menu_item.json()["id"]

	res = client.post(
		ORDER_ENDPOINT,
		json={
			"table_number": table_number,
			"items": [{"menu_item_id": drink_id, "quantity": 1}],
		},
		headers=admin_headers,
	)
	assert res.status_code == HTTPStatus.CREATED
	order_id = res.json()["id"]

	# Customer attempts to update status -> 403 Forbidden
	forbidden_patch = client.patch(
		f"{ORDER_ENDPOINT}/{order_id}/status",
		json={"status": "preparing"},
		headers=customer_headers,
	)
	assert forbidden_patch.status_code == HTTPStatus.FORBIDDEN

	# Admin advances status: pending -> preparing
	p1 = client.patch(
		f"{ORDER_ENDPOINT}/{order_id}/status",
		json={"status": "preparing"},
		headers=admin_headers,
	)
	assert p1.status_code == HTTPStatus.OK
	assert p1.json()["status"] == "preparing"

	# Admin advances status: preparing -> ready
	p2 = client.patch(
		f"{ORDER_ENDPOINT}/{order_id}/status",
		json={"status": "ready"},
		headers=admin_headers,
	)
	assert p2.status_code == HTTPStatus.OK
	assert p2.json()["status"] == "ready"

	# Admin advances status: ready -> served
	p3 = client.patch(
		f"{ORDER_ENDPOINT}/{order_id}/status",
		json={"status": "served"},
		headers=admin_headers,
	)
	assert p3.status_code == HTTPStatus.OK
	assert p3.json()["status"] == "served"
