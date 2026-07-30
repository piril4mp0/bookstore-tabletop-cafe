from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient

from tests.constants import CREATE_TAG_BODY, TAG_ENDPOINT


@pytest.mark.core
def test_create_tag(client: TestClient, stp_trdwn_tag):
	res = stp_trdwn_tag
	assert res.status_code == HTTPStatus.CREATED
	assert res.json()["name"] == CREATE_TAG_BODY["name"]
	assert "id" in res.json()


@pytest.mark.core
def test_create_tag_unauthorized(client: TestClient):
	response = client.post(TAG_ENDPOINT, json=CREATE_TAG_BODY)
	assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.core
def test_get_all_tags(client: TestClient, stp_trdwn_tag):
	response = client.get(TAG_ENDPOINT)
	assert response.status_code == HTTPStatus.OK
	assert isinstance(response.json(), list)


@pytest.mark.core
def test_get_tag_by_id(client: TestClient, stp_trdwn_tag):
	tag_data = stp_trdwn_tag.json()
	tag_id = tag_data["id"]
	response = client.get(f"{TAG_ENDPOINT}/{tag_id}")
	assert response.status_code == HTTPStatus.OK
	assert response.json()["id"] == tag_id
	assert response.json()["name"] == CREATE_TAG_BODY["name"]


@pytest.mark.core
def test_delete_tag(client: TestClient, stp_trdwn_tag, admin_headers: dict[str, str]):
	tag_id = stp_trdwn_tag.json()["id"]
	delete_res = client.delete(f"{TAG_ENDPOINT}/{tag_id}", headers=admin_headers)
	assert delete_res.status_code == HTTPStatus.NO_CONTENT
	assert client.get(f"{TAG_ENDPOINT}/{tag_id}").status_code == HTTPStatus.NOT_FOUND
