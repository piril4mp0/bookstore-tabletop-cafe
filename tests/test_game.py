from http import HTTPStatus
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client() -> TestClient:
    return TestClient(app=app)

# review later
def test_create_game(client: TestClient):
    game_data = {
        "title": "Old Dragon 2",
        "genre": ["RPG", "Fantasy"],
        "description": "An epic fantasy role-playing game",
        "release_date": "2023-01-01",
        "players": 4
    }
    response = client.post("/games/create", json=game_data)
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == game_data

# review later
def test_get_all_games(client: TestClient):
    response = client.get("/games/")
    assert response.status_code == HTTPStatus.OK
    assert isinstance(response.json(), list)