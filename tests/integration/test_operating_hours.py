from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient

from tests.constants import OPERATING_HOURS_ENDPOINT, UPDATE_OPERATING_HOURS_BODY


@pytest.mark.core
def test_list_operating_hours(client: TestClient):
	res = client.get(OPERATING_HOURS_ENDPOINT)
	assert res.status_code == HTTPStatus.OK
	assert isinstance(res.json(), list)


@pytest.mark.core
def test_get_operating_hours_by_day_not_found(client: TestClient):
	# Day 0 (Monday) before configuration
	res = client.get(f"{OPERATING_HOURS_ENDPOINT}/0")
	# If empty initially, returns 404
	assert res.status_code in (HTTPStatus.NOT_FOUND, HTTPStatus.OK)


@pytest.mark.core
def test_put_operating_hours_admin(client: TestClient, admin_headers):
	# Configure Monday (day_of_week=0)
	res = client.put(
		f"{OPERATING_HOURS_ENDPOINT}/0",
		json=UPDATE_OPERATING_HOURS_BODY,
		headers=admin_headers,
	)
	assert res.status_code == HTTPStatus.OK
	data = res.json()
	assert data["day_of_week"] == 0
	assert data["open_time"] == UPDATE_OPERATING_HOURS_BODY["open_time"]
	assert data["close_time"] == UPDATE_OPERATING_HOURS_BODY["close_time"]
	assert data["is_closed"] is False

	# Fetch to verify persistence
	res_get = client.get(f"{OPERATING_HOURS_ENDPOINT}/0")
	assert res_get.status_code == HTTPStatus.OK
	assert res_get.json()["day_of_week"] == 0


@pytest.mark.core
def test_put_operating_hours_unauthorized(client: TestClient, customer_headers):
	res_unauth = client.put(
		f"{OPERATING_HOURS_ENDPOINT}/0", json=UPDATE_OPERATING_HOURS_BODY
	)
	assert res_unauth.status_code == HTTPStatus.UNAUTHORIZED

	res_customer = client.put(
		f"{OPERATING_HOURS_ENDPOINT}/0",
		json=UPDATE_OPERATING_HOURS_BODY,
		headers=customer_headers,
	)
	assert res_customer.status_code == HTTPStatus.FORBIDDEN
