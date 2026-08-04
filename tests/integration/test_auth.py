from datetime import datetime, timedelta
from http import HTTPStatus
from zoneinfo import ZoneInfo

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.refresh_token import RefreshToken
from tests.constants import CUSTOMER_DATA


def test_login_returns_access_and_refresh_tokens(client: TestClient):
	client.post("/auth/signup", json=CUSTOMER_DATA)
	res = client.post(
		"/auth/login",
		data={
			"username": CUSTOMER_DATA["email"],
			"password": CUSTOMER_DATA["password"],
		},
	)
	assert res.status_code == HTTPStatus.OK
	data = res.json()
	assert "access_token" in data
	assert "refresh_token" in data
	assert data["token_type"] == "bearer"
	assert len(data["refresh_token"]) > 0


def test_refresh_token_success(client: TestClient):
	client.post("/auth/signup", json=CUSTOMER_DATA)
	login_res = client.post(
		"/auth/login",
		data={
			"username": CUSTOMER_DATA["email"],
			"password": CUSTOMER_DATA["password"],
		},
	)
	old_refresh_token = login_res.json()["refresh_token"]

	refresh_res = client.post(
		"/auth/refresh",
		json={"refresh_token": old_refresh_token},
	)
	assert refresh_res.status_code == HTTPStatus.OK
	new_data = refresh_res.json()
	assert "access_token" in new_data
	assert "refresh_token" in new_data
	assert new_data["refresh_token"] != old_refresh_token


def test_refresh_token_rotation_invalidates_old_token(client: TestClient):
	client.post("/auth/signup", json=CUSTOMER_DATA)
	login_res = client.post(
		"/auth/login",
		data={
			"username": CUSTOMER_DATA["email"],
			"password": CUSTOMER_DATA["password"],
		},
	)
	old_refresh_token = login_res.json()["refresh_token"]

	# First refresh call succeeds
	refresh_res = client.post(
		"/auth/refresh",
		json={"refresh_token": old_refresh_token},
	)
	assert refresh_res.status_code == HTTPStatus.OK

	# Second refresh call with old token fails
	reuse_res = client.post(
		"/auth/refresh",
		json={"refresh_token": old_refresh_token},
	)
	assert reuse_res.status_code == HTTPStatus.UNAUTHORIZED
	assert reuse_res.json()["detail"] == "Invalid or expired refresh token"


def test_refresh_token_expired(client: TestClient, session: Session):
	client.post("/auth/signup", json=CUSTOMER_DATA)
	login_res = client.post(
		"/auth/login",
		data={
			"username": CUSTOMER_DATA["email"],
			"password": CUSTOMER_DATA["password"],
		},
	)
	refresh_token_str = login_res.json()["refresh_token"]

	# Manually expire the token in the DB
	token_record = (
		session.query(RefreshToken)
		.filter(RefreshToken.token == refresh_token_str)
		.first()
	)
	assert token_record is not None
	token_record.expires_at = datetime.now(tz=ZoneInfo("UTC")) - timedelta(days=1)
	session.commit()

	refresh_res = client.post(
		"/auth/refresh",
		json={"refresh_token": refresh_token_str},
	)
	assert refresh_res.status_code == HTTPStatus.UNAUTHORIZED
	assert refresh_res.json()["detail"] == "Invalid or expired refresh token"


def test_revoke_token_success(client: TestClient):
	client.post("/auth/signup", json=CUSTOMER_DATA)
	login_res = client.post(
		"/auth/login",
		data={
			"username": CUSTOMER_DATA["email"],
			"password": CUSTOMER_DATA["password"],
		},
	)
	refresh_token_str = login_res.json()["refresh_token"]

	revoke_res = client.post(
		"/auth/revoke",
		json={"refresh_token": refresh_token_str},
	)
	assert revoke_res.status_code == HTTPStatus.NO_CONTENT

	# Attempt to refresh using revoked token should fail
	refresh_res = client.post(
		"/auth/refresh",
		json={"refresh_token": refresh_token_str},
	)
	assert refresh_res.status_code == HTTPStatus.UNAUTHORIZED


def test_refresh_token_invalid_str(client: TestClient):
	refresh_res = client.post(
		"/auth/refresh",
		json={"refresh_token": "non_existent_token_123"},
	)
	assert refresh_res.status_code == HTTPStatus.UNAUTHORIZED
