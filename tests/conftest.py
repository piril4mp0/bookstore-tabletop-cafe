from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient
from httpx import Response
from sqlalchemy.orm import Session

from app.db.database import table_registry
from app.dependencies import get_db
from app.main import app
from app.models.book import Book  # noqa: F401
from app.models.game import Game  # noqa: F401
from app.models.menu import MenuItem, menu_item_tags  # noqa: F401
from app.models.operating_hours import OperatingHours  # noqa: F401
from app.models.order import Order, OrderItem  # noqa: F401
from app.models.refresh_token import RefreshToken  # noqa: F401
from app.models.reservation import Reservation  # noqa: F401
from app.models.table import GameTable  # noqa: F401
from app.models.tag import Tag  # noqa: F401
from app.models.user import User as UserModel
from tests.constants import *
from tests.database import TestingSessionLocal, engine


@pytest.fixture
def session():
	"""Sets up a clean database for each test."""
	table_registry.metadata.create_all(bind=engine)
	db = TestingSessionLocal()
	try:
		yield db
	finally:
		db.close()
		table_registry.metadata.drop_all(bind=engine)


@pytest.fixture
def client(session):
	"""Overrides the database dependency and provides a TestClient."""

	def override_get_db():
		try:
			yield session
		finally:
			pass

	app.dependency_overrides[get_db] = override_get_db

	with TestClient(app) as client:
		yield client
	app.dependency_overrides.clear()


@pytest.fixture
def login(client: TestClient) -> Response:
	return client.post(
		"/auth/login",
		data={"username": ADMIN_DATA["email"], "password": ADMIN_DATA["password"]},
	)


@pytest.fixture
def get_admin_token(client: TestClient, session: Session) -> str:
	"""Registers a user, makes them admin in the DB, and returns the Bearer token."""
	client.post("/auth/signup", json=ADMIN_DATA)

	user = (
		session.query(UserModel).filter(UserModel.email == ADMIN_DATA["email"]).first()
	)
	if user:
		user.is_admin = True
		session.commit()

	res = client.post(
		"/auth/login",
		data={"username": ADMIN_DATA["email"], "password": ADMIN_DATA["password"]},
	)
	if res.status_code != HTTPStatus.OK:
		raise Exception(f"Login failed with status {res.status_code}: {res.text}")
	return f"Bearer {res.json()['access_token']}"


@pytest.fixture
def admin_headers(client: TestClient, get_admin_token) -> dict[str, str]:
	return {"Authorization": get_admin_token}


@pytest.fixture
def get_customer_token(client: TestClient) -> str:
	"""Registers a customer user and returns the Bearer token."""
	client.post("/auth/signup", json=CUSTOMER_DATA)
	res = client.post(
		"/auth/login",
		data={
			"username": CUSTOMER_DATA["email"],
			"password": CUSTOMER_DATA["password"],
		},
	)
	if res.status_code != HTTPStatus.OK:
		raise Exception(f"Login failed with status {res.status_code}: {res.text}")
	return f"Bearer {res.json()['access_token']}"


@pytest.fixture
def customer_headers(client: TestClient, get_customer_token) -> dict[str, str]:
	return {"Authorization": get_customer_token}


@pytest.fixture
def imported_book(client: TestClient, admin_headers):
	res = client.post(
		f"{BOOK_ENDPOINT}/import", json=BOOK_IMPORT_BODY, headers=admin_headers
	)

	yield res

	client.delete(
		f"{BOOK_ENDPOINT}/{BOOK_DATA['isbn']}",
		headers=admin_headers,
	)


@pytest.fixture
def stp_trdwn_game(client: TestClient, admin_headers):
	res = client.post(f"{GAME_ENDPOINT}", json=CREATE_GAME_BODY, headers=admin_headers)

	yield res

	if res.status_code == HTTPStatus.CREATED:
		game_id = res.json()["id"]
		client.delete(
			f"{GAME_ENDPOINT}/{game_id}",
			headers=admin_headers,
		)


@pytest.fixture
def stp_trdwn_tag(client: TestClient, admin_headers):
	res = client.post(TAG_ENDPOINT, json=CREATE_TAG_BODY, headers=admin_headers)

	yield res

	if res.status_code == HTTPStatus.CREATED:
		tag_id = res.json()["id"]
		client.delete(f"{TAG_ENDPOINT}/{tag_id}", headers=admin_headers)


@pytest.fixture
def stp_trdwn_menu_item(client: TestClient, admin_headers):
	res = client.post(MENU_ENDPOINT, json=CREATE_MENU_DRINK_BODY, headers=admin_headers)

	yield res

	if res.status_code == HTTPStatus.CREATED:
		item_id = res.json()["id"]
		client.delete(f"{MENU_ENDPOINT}/{item_id}", headers=admin_headers)


@pytest.fixture
def stp_trdwn_table(client: TestClient, admin_headers):
	res = client.post(TABLE_ENDPOINT, json=CREATE_TABLE_BODY, headers=admin_headers)

	yield res

	if res.status_code == HTTPStatus.CREATED:
		table_id = res.json()["id"]
		client.delete(f"{TABLE_ENDPOINT}/{table_id}", headers=admin_headers)


@pytest.fixture
def stp_trdwn_meal_item(client: TestClient, admin_headers):
	res = client.post(MENU_ENDPOINT, json=CREATE_MENU_MEAL_BODY, headers=admin_headers)

	yield res

	if res.status_code == HTTPStatus.CREATED:
		item_id = res.json()["id"]
		client.delete(f"{MENU_ENDPOINT}/{item_id}", headers=admin_headers)
