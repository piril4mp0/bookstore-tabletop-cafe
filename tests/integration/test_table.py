from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient

from tests.constants import CREATE_TABLE_BODY, TABLE_ENDPOINT


@pytest.mark.core
def test_create_table_admin(client: TestClient, stp_trdwn_table):
	res = stp_trdwn_table
	data = res.json()
	assert res.status_code == HTTPStatus.CREATED
	assert data["number"] == CREATE_TABLE_BODY["number"]
	assert data["chairs"] == CREATE_TABLE_BODY["chairs"]
	assert data["size"] == CREATE_TABLE_BODY["size"]
	assert "id" in data


@pytest.mark.core
def test_create_table_unauthorized(client: TestClient, customer_headers):
	# Unauthenticated
	res = client.post(TABLE_ENDPOINT, json=CREATE_TABLE_BODY)
	assert res.status_code == HTTPStatus.UNAUTHORIZED

	# Non-admin user
	res_customer = client.post(
		TABLE_ENDPOINT, json=CREATE_TABLE_BODY, headers=customer_headers
	)
	assert res_customer.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.core
def test_create_table_duplicate_number(
	client: TestClient, stp_trdwn_table, admin_headers
):
	# Attempt to create another table with table number 1
	res = client.post(TABLE_ENDPOINT, json=CREATE_TABLE_BODY, headers=admin_headers)
	assert res.status_code == HTTPStatus.CONFLICT
	assert "already exists" in res.json()["detail"]


@pytest.mark.core
def test_list_tables(client: TestClient, stp_trdwn_table):
	res = client.get(TABLE_ENDPOINT)
	assert res.status_code == HTTPStatus.OK
	assert isinstance(res.json(), list)
	assert len(res.json()) >= 1


@pytest.mark.core
def test_get_table_by_id(client: TestClient, stp_trdwn_table):
	table_id = stp_trdwn_table.json()["id"]
	res = client.get(f"{TABLE_ENDPOINT}/{table_id}")
	assert res.status_code == HTTPStatus.OK
	assert res.json()["id"] == table_id
	assert res.json()["number"] == CREATE_TABLE_BODY["number"]


@pytest.mark.core
def test_get_table_not_found(client: TestClient):
	res = client.get(f"{TABLE_ENDPOINT}/99999")
	assert res.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.core
def test_update_table_admin(client: TestClient, stp_trdwn_table, admin_headers):
	table_id = stp_trdwn_table.json()["id"]
	update_payload = {"chairs": 8, "size": "large"}
	res = client.put(
		f"{TABLE_ENDPOINT}/{table_id}", json=update_payload, headers=admin_headers
	)
	assert res.status_code == HTTPStatus.OK
	assert res.json()["chairs"] == 8
	assert res.json()["size"] == "large"
	assert res.json()["number"] == CREATE_TABLE_BODY["number"]


@pytest.mark.core
def test_update_table_duplicate_number(
	client: TestClient, stp_trdwn_table, admin_headers
):
	# Create a second table
	res2 = client.post(
		TABLE_ENDPOINT,
		json={"number": 2, "chairs": 2, "size": "small"},
		headers=admin_headers,
	)
	assert res2.status_code == HTTPStatus.CREATED
	table2_id = res2.json()["id"]

	try:
		# Update table 2 to use table 1's number
		res_dup = client.put(
			f"{TABLE_ENDPOINT}/{table2_id}",
			json={"number": CREATE_TABLE_BODY["number"]},
			headers=admin_headers,
		)
		assert res_dup.status_code == HTTPStatus.CONFLICT
	finally:
		client.delete(f"{TABLE_ENDPOINT}/{table2_id}", headers=admin_headers)


@pytest.mark.core
def test_delete_table_admin(client: TestClient, admin_headers):
	res = client.post(
		TABLE_ENDPOINT,
		json={"number": 99, "chairs": 4, "size": "medium"},
		headers=admin_headers,
	)
	table_id = res.json()["id"]

	res_delete = client.delete(f"{TABLE_ENDPOINT}/{table_id}", headers=admin_headers)
	assert res_delete.status_code == HTTPStatus.NO_CONTENT

	res_get = client.get(f"{TABLE_ENDPOINT}/{table_id}")
	assert res_get.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.core
def test_delete_table_not_found(client: TestClient, admin_headers):
	res = client.delete(f"{TABLE_ENDPOINT}/99999", headers=admin_headers)
	assert res.status_code == HTTPStatus.NOT_FOUND
