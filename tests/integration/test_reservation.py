from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient

from tests.constants import (
	OPERATING_HOURS_ENDPOINT,
	RESERVATION_ENDPOINT,
)


@pytest.fixture
def setup_operating_hours(client: TestClient, admin_headers):
	"""Sets operating hours for Monday (09:00 - 22:00) and Sunday (closed)."""
	# Monday open
	client.put(
		f"{OPERATING_HOURS_ENDPOINT}/0",
		json={"open_time": "09:00:00", "close_time": "22:00:00", "is_closed": False},
		headers=admin_headers,
	)
	# Sunday closed
	client.put(
		f"{OPERATING_HOURS_ENDPOINT}/6",
		json={"open_time": "10:00:00", "close_time": "18:00:00", "is_closed": True},
		headers=admin_headers,
	)


@pytest.mark.core
def test_create_reservation_success(
	client: TestClient,
	customer_headers,
	stp_trdwn_table,
	stp_trdwn_game,
	setup_operating_hours,
):
	table_id = stp_trdwn_table.json()["id"]
	game_id = stp_trdwn_game.json()["id"]

	# 2026-08-03 is a Monday (day_of_week=0)
	reservation_payload = {
		"game_id": game_id,
		"table_id": table_id,
		"starts_at": "2026-08-03T14:00:00",
		"ends_at": "2026-08-03T16:00:00",
	}

	res = client.post(
		RESERVATION_ENDPOINT, json=reservation_payload, headers=customer_headers
	)
	assert res.status_code == HTTPStatus.CREATED
	data = res.json()
	assert data["game_id"] == game_id
	assert data["table_id"] == table_id
	assert data["status"] == "active"
	assert "id" in data

	# Check game stock is decremented (was 1, now 0)
	game_res = client.get(f"/games/{game_id}")
	assert game_res.status_code == HTTPStatus.OK
	assert game_res.json()["current_stock"] == 0


@pytest.mark.core
def test_create_reservation_duration_too_short(
	client: TestClient,
	customer_headers,
	stp_trdwn_table,
	stp_trdwn_game,
	setup_operating_hours,
):
	table_id = stp_trdwn_table.json()["id"]
	game_id = stp_trdwn_game.json()["id"]

	# 20 minutes duration (< 30m)
	reservation_payload = {
		"game_id": game_id,
		"table_id": table_id,
		"starts_at": "2026-08-03T14:00:00",
		"ends_at": "2026-08-03T14:20:00",
	}

	res = client.post(
		RESERVATION_ENDPOINT, json=reservation_payload, headers=customer_headers
	)
	assert res.status_code == HTTPStatus.BAD_REQUEST
	assert "at least 30 minutes" in res.json()["detail"]


@pytest.mark.core
def test_create_reservation_different_calendar_days(
	client: TestClient,
	customer_headers,
	stp_trdwn_table,
	stp_trdwn_game,
	setup_operating_hours,
):
	table_id = stp_trdwn_table.json()["id"]
	game_id = stp_trdwn_game.json()["id"]

	reservation_payload = {
		"game_id": game_id,
		"table_id": table_id,
		"starts_at": "2026-08-03T23:00:00",
		"ends_at": "2026-08-04T01:00:00",
	}

	res = client.post(
		RESERVATION_ENDPOINT, json=reservation_payload, headers=customer_headers
	)
	assert res.status_code == HTTPStatus.BAD_REQUEST
	assert "same calendar day" in res.json()["detail"]


@pytest.mark.core
def test_create_reservation_starts_before_opening_hours(
	client: TestClient,
	customer_headers,
	stp_trdwn_table,
	stp_trdwn_game,
	setup_operating_hours,
):
	table_id = stp_trdwn_table.json()["id"]
	game_id = stp_trdwn_game.json()["id"]

	# Starts before open (08:00 vs 09:00 open)
	res = client.post(
		RESERVATION_ENDPOINT,
		json={
			"game_id": game_id,
			"table_id": table_id,
			"starts_at": "2026-08-03T08:00:00",
			"ends_at": "2026-08-03T10:00:00",
		},
		headers=customer_headers,
	)
	assert res.status_code == HTTPStatus.BAD_REQUEST
	assert "starts before" in res.json()["detail"]


@pytest.mark.core
def test_create_reservation_starts_less_than_30m_before_closing(
	client: TestClient,
	customer_headers,
	stp_trdwn_table,
	stp_trdwn_game,
	setup_operating_hours,
):
	table_id = stp_trdwn_table.json()["id"]
	game_id = stp_trdwn_game.json()["id"]

	# Less than 30 mins before closing (21:40 vs 22:00 close)
	res = client.post(
		RESERVATION_ENDPOINT,
		json={
			"game_id": game_id,
			"table_id": table_id,
			"starts_at": "2026-08-03T21:40:00",
			"ends_at": "2026-08-03T22:10:00",
		},
		headers=customer_headers,
	)
	assert res.status_code == HTTPStatus.BAD_REQUEST
	assert "less than 30 minutes from closing" in res.json()["detail"]


@pytest.mark.core
def test_create_reservation_ends_after_closing_hours(
	client: TestClient,
	customer_headers,
	stp_trdwn_table,
	stp_trdwn_game,
	setup_operating_hours,
):
	table_id = stp_trdwn_table.json()["id"]
	game_id = stp_trdwn_game.json()["id"]

	# Ends after closing hours (21:00 to 22:30 vs 22:00 close)
	res = client.post(
		RESERVATION_ENDPOINT,
		json={
			"game_id": game_id,
			"table_id": table_id,
			"starts_at": "2026-08-03T21:00:00",
			"ends_at": "2026-08-03T22:30:00",
		},
		headers=customer_headers,
	)
	assert res.status_code == HTTPStatus.BAD_REQUEST
	assert "ends after cafe closing hours" in res.json()["detail"]


@pytest.mark.core
def test_create_reservation_on_closed_day(
	client: TestClient,
	customer_headers,
	stp_trdwn_table,
	stp_trdwn_game,
	setup_operating_hours,
):
	table_id = stp_trdwn_table.json()["id"]
	game_id = stp_trdwn_game.json()["id"]

	# Cafe closed on Sunday (2026-08-09 is Sunday)
	res = client.post(
		RESERVATION_ENDPOINT,
		json={
			"game_id": game_id,
			"table_id": table_id,
			"starts_at": "2026-08-09T14:00:00",
			"ends_at": "2026-08-09T16:00:00",
		},
		headers=customer_headers,
	)
	assert res.status_code == HTTPStatus.BAD_REQUEST
	assert "closed" in res.json()["detail"]


@pytest.mark.core
def test_create_reservation_not_found_entities(
	client: TestClient, customer_headers, stp_trdwn_table, stp_trdwn_game
):
	table_id = stp_trdwn_table.json()["id"]
	game_id = stp_trdwn_game.json()["id"]

	# Table not found
	res_table = client.post(
		RESERVATION_ENDPOINT,
		json={
			"game_id": game_id,
			"table_id": 99999,
			"starts_at": "2026-08-03T14:00:00",
			"ends_at": "2026-08-03T16:00:00",
		},
		headers=customer_headers,
	)
	assert res_table.status_code == HTTPStatus.NOT_FOUND

	# Game not found
	res_game = client.post(
		RESERVATION_ENDPOINT,
		json={
			"game_id": 99999,
			"table_id": table_id,
			"starts_at": "2026-08-03T14:00:00",
			"ends_at": "2026-08-03T16:00:00",
		},
		headers=customer_headers,
	)
	assert res_game.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.core
def test_create_reservation_table_overlap(
	client: TestClient,
	customer_headers,
	stp_trdwn_table,
	stp_trdwn_game,
	setup_operating_hours,
):
	table_id = stp_trdwn_table.json()["id"]
	game_id = stp_trdwn_game.json()["id"]

	# First reservation: 14:00 to 16:00
	res1 = client.post(
		RESERVATION_ENDPOINT,
		json={
			"game_id": game_id,
			"table_id": table_id,
			"starts_at": "2026-08-03T14:00:00",
			"ends_at": "2026-08-03T16:00:00",
		},
		headers=customer_headers,
	)
	assert res1.status_code == HTTPStatus.CREATED

	# Second reservation overlapping: 15:00 to 17:00
	res2 = client.post(
		RESERVATION_ENDPOINT,
		json={
			"game_id": game_id,
			"table_id": table_id,
			"starts_at": "2026-08-03T15:00:00",
			"ends_at": "2026-08-03T17:00:00",
		},
		headers=customer_headers,
	)
	assert res2.status_code == HTTPStatus.BAD_REQUEST
	assert "already reserved" in res2.json()["detail"]


@pytest.mark.core
def test_create_reservation_game_out_of_stock(
	client: TestClient,
	customer_headers,
	admin_headers,
	stp_trdwn_table,
	stp_trdwn_game,
	setup_operating_hours,
):
	table_id = stp_trdwn_table.json()["id"]
	game_id = stp_trdwn_game.json()["id"]

	# Create table 2
	t2_res = client.post(
		"/tables",
		json={"number": 2, "chairs": 4, "size": "large"},
		headers=admin_headers,
	)
	table2_id = t2_res.json()["id"]

	try:
		# Customer 1 reserves game (stock 1 -> current_stock 0)
		res1 = client.post(
			RESERVATION_ENDPOINT,
			json={
				"game_id": game_id,
				"table_id": table_id,
				"starts_at": "2026-08-03T14:00:00",
				"ends_at": "2026-08-03T16:00:00",
			},
			headers=customer_headers,
		)
		assert res1.status_code == HTTPStatus.CREATED

		# Customer 1 tries to reserve same game for table 2 at different time slot
		res2 = client.post(
			RESERVATION_ENDPOINT,
			json={
				"game_id": game_id,
				"table_id": table2_id,
				"starts_at": "2026-08-03T17:00:00",
				"ends_at": "2026-08-03T19:00:00",
			},
			headers=customer_headers,
		)
		assert res2.status_code == HTTPStatus.BAD_REQUEST
		assert "out of stock" in res2.json()["detail"]
	finally:
		client.delete(f"/tables/{table2_id}", headers=admin_headers)


@pytest.mark.core
def test_list_and_get_reservations_permissions(
	client: TestClient,
	customer_headers,
	admin_headers,
	stp_trdwn_table,
	stp_trdwn_game,
	setup_operating_hours,
):
	table_id = stp_trdwn_table.json()["id"]
	game_id = stp_trdwn_game.json()["id"]

	# Customer creates reservation
	res = client.post(
		RESERVATION_ENDPOINT,
		json={
			"game_id": game_id,
			"table_id": table_id,
			"starts_at": "2026-08-03T14:00:00",
			"ends_at": "2026-08-03T16:00:00",
		},
		headers=customer_headers,
	)
	reservation_id = res.json()["id"]

	# Customer lists reservations -> sees their reservation
	res_customer_list = client.get(RESERVATION_ENDPOINT, headers=customer_headers)
	assert res_customer_list.status_code == HTTPStatus.OK
	assert len(res_customer_list.json()) == 1
	assert res_customer_list.json()[0]["id"] == reservation_id

	# Admin lists reservations -> sees all reservations
	res_admin_list = client.get(RESERVATION_ENDPOINT, headers=admin_headers)
	assert res_admin_list.status_code == HTTPStatus.OK
	assert len(res_admin_list.json()) >= 1

	# Owner customer gets reservation details
	res_owner_get = client.get(
		f"{RESERVATION_ENDPOINT}/{reservation_id}", headers=customer_headers
	)
	assert res_owner_get.status_code == HTTPStatus.OK

	# Admin gets reservation details
	res_admin_get = client.get(
		f"{RESERVATION_ENDPOINT}/{reservation_id}", headers=admin_headers
	)
	assert res_admin_get.status_code == HTTPStatus.OK


@pytest.mark.core
def test_get_and_cancel_reservation_forbidden(
	client: TestClient,
	customer_headers,
	stp_trdwn_table,
	stp_trdwn_game,
	setup_operating_hours,
):
	table_id = stp_trdwn_table.json()["id"]
	game_id = stp_trdwn_game.json()["id"]

	# Reservation created by Customer 1
	res = client.post(
		RESERVATION_ENDPOINT,
		json={
			"game_id": game_id,
			"table_id": table_id,
			"starts_at": "2026-08-03T14:00:00",
			"ends_at": "2026-08-03T16:00:00",
		},
		headers=customer_headers,
	)
	reservation_id = res.json()["id"]

	# Create second customer user
	client.post(
		"/auth/signup",
		json={
			"username": "customer2",
			"full_name": "Customer Two",
			"email": "customer2@test.com",
			"password": "password123",
		},
	)
	login2 = client.post(
		"/auth/login",
		data={"username": "customer2@test.com", "password": "password123"},
	)
	token2 = f"Bearer {login2.json()['access_token']}"
	customer2_headers = {"Authorization": token2}

	# Customer 2 tries to view Customer 1's reservation
	res_view = client.get(
		f"{RESERVATION_ENDPOINT}/{reservation_id}", headers=customer2_headers
	)
	assert res_view.status_code == HTTPStatus.FORBIDDEN

	# Customer 2 tries to cancel Customer 1's reservation
	res_cancel = client.patch(
		f"{RESERVATION_ENDPOINT}/{reservation_id}/cancel", headers=customer2_headers
	)
	assert res_cancel.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.core
def test_cancel_reservation_replenishes_stock(
	client: TestClient,
	customer_headers,
	stp_trdwn_table,
	stp_trdwn_game,
	setup_operating_hours,
):
	table_id = stp_trdwn_table.json()["id"]
	game_id = stp_trdwn_game.json()["id"]

	# Customer creates reservation
	res = client.post(
		RESERVATION_ENDPOINT,
		json={
			"game_id": game_id,
			"table_id": table_id,
			"starts_at": "2026-08-03T14:00:00",
			"ends_at": "2026-08-03T16:00:00",
		},
		headers=customer_headers,
	)
	reservation_id = res.json()["id"]

	# Verify stock decremented to 0
	game_before = client.get(f"/games/{game_id}").json()
	assert game_before["current_stock"] == 0

	# Cancel reservation
	res_cancel = client.patch(
		f"{RESERVATION_ENDPOINT}/{reservation_id}/cancel", headers=customer_headers
	)
	assert res_cancel.status_code == HTTPStatus.OK
	assert res_cancel.json()["status"] == "cancelled"

	# Verify stock replenished to 1
	game_after = client.get(f"/games/{game_id}").json()
	assert game_after["current_stock"] == 1

	# Try cancelling again -> Bad Request
	res_cancel_again = client.patch(
		f"{RESERVATION_ENDPOINT}/{reservation_id}/cancel", headers=customer_headers
	)
	assert res_cancel_again.status_code == HTTPStatus.BAD_REQUEST
	assert "already cancelled" in res_cancel_again.json()["detail"]
