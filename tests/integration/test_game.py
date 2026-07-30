import uuid
from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient

from tests.constants import *


@pytest.mark.core
def test_create_game(client: TestClient, stp_trdwn_game):
	res = stp_trdwn_game
	data = res.json()
	assert res.status_code == HTTPStatus.CREATED
	for key, value in CREATE_GAME_BODY.items():
		assert data[key] == value


@pytest.mark.core
def test_get_all_games(client: TestClient, stp_trdwn_game):
	response = client.get(GAME_ENDPOINT)
	assert response.status_code == HTTPStatus.OK
	assert isinstance(response.json(), list)


@pytest.mark.core
def test_get_game_by_id(client: TestClient, stp_trdwn_game):
	data = stp_trdwn_game.json()
	id = data["id"]
	response = client.get(f"{GAME_ENDPOINT}/{id}")
	assert response.status_code == HTTPStatus.OK
	for key, value in CREATE_GAME_BODY.items():
		assert data[key] == value


@pytest.mark.core
def test_put_game(client: TestClient, stp_trdwn_game, admin_headers):
	game_id = stp_trdwn_game.json()["id"]
	new_data = {
		"title": f"edit - {uuid.uuid4()}",
		"genre": ["edit", "edit2"],
		"description": "editted description",
		"release_date": "2000-01-01",
		"players": 1,
	}
	response = client.put(
		f"{GAME_ENDPOINT}/{game_id}", json=new_data, headers=admin_headers
	)
	assert response.status_code == HTTPStatus.OK
	assert response.json()["title"] == new_data["title"]
	assert response.json()["genre"] == new_data["genre"]
	assert response.json()["description"] == new_data["description"]
	assert response.json()["release_date"] == new_data["release_date"]
	assert response.json()["players"] == new_data["players"]


@pytest.mark.core
def test_delete_game(client: TestClient, stp_trdwn_game, admin_headers):
	game_id = stp_trdwn_game.json()["id"]
	response = client.delete(f"{GAME_ENDPOINT}/{game_id}", headers=admin_headers)
	assert response.status_code == HTTPStatus.NO_CONTENT
	assert client.get(f"{GAME_ENDPOINT}/{game_id}").status_code == HTTPStatus.NOT_FOUND
