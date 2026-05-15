from http import HTTPStatus
import pytest
import uuid
from fastapi.testclient import TestClient
from app.main import app

endpoint = "/games"


@pytest.fixture
def client() -> TestClient:
    return TestClient(app=app)


@pytest.fixture
def seed_db_with_game(client: TestClient):
    game_data = {
        "title": f"Old Dragon 2 - {uuid.uuid4()}",
        "genre": ["RPG", "Fantasy"],
        "description": "An epic fantasy role-playing game",
        "release_date": "2023-01-01",
        "players": 4,
    }
    response = client.post(endpoint, json=game_data)
    return response


# review later
def test_create_game(client: TestClient):
    game_data = {
        "title": f"Old Dragon 2 - {uuid.uuid4()}",
        "genre": ["RPG", "Fantasy"],
        "description": "An epic fantasy role-playing game",
        "release_date": "2023-01-01",
        "players": 4,
    }
    response = client.post(endpoint, json=game_data)
    json = response.json()
    assert response.status_code == HTTPStatus.CREATED
    for key, value in game_data.items():
        assert json[key] == value


# review later
def test_get_all_games(client: TestClient):
    response = client.get(endpoint)
    assert response.status_code == HTTPStatus.OK
    assert isinstance(response.json(), list)


def test_get_game_by_id(client: TestClient, seed_db_with_game):
    game_id = seed_db_with_game.json()["id"]
    response = client.get(f"{endpoint}/{game_id}")
    assert response.status_code == HTTPStatus.OK
    assert response.json()["id"] == game_id


def test_put_game(client: TestClient, seed_db_with_game):
    game_id = seed_db_with_game.json()["id"]
    new_data = {
        "title": f"edit - {uuid.uuid4()}",
        "genre": ["edit", "edit2"],
        "description": "editted description",
        "release_date": "2000-01-01",
        "players": 1,
    }
    response = client.put(f"{endpoint}/{game_id}", json=new_data)
    assert response.status_code == HTTPStatus.OK
    assert response.json()["title"] == new_data["title"]
    assert response.json()["genre"] == new_data["genre"]
    assert response.json()["description"] == new_data["description"]
    assert response.json()["release_date"] == new_data["release_date"]
    assert response.json()["players"] == new_data["players"]


def test_delete_game(client: TestClient, seed_db_with_game):
    game_id = seed_db_with_game.json()["id"]
    print(game_id)
    response = client.delete(f"{endpoint}/{game_id}")
    assert response.status_code == HTTPStatus.NO_CONTENT
    assert client.get(f"{endpoint}/{game_id}").status_code == HTTPStatus.NOT_FOUND
