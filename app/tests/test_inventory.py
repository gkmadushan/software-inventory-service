import importlib
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from utils.database import Base
from dependencies import get_db, get_token_header


def override_get_token_header():
    return True


app.dependency_overrides[get_token_header] = override_get_token_header

client = TestClient(app)


def test_get_inventory_items():
    response = client.get("/v1/inventory")
    assert response.status_code == 200


def test_get_inventory_items_404():
    response = client.get("/v1/inventory?name=xxxxxxxx")
    assert response.json()['meta']['total_records'] == 0


def test_get_inventory_item_404():
    response = client.get("/v1/inventory/4f07cf23-cd0f-42b5-99c4-efa9022adccf")
    assert response.status_code == 404


def test_create_inventory_item_201():
    response = client.post("/v1/inventory", json={
        "name": "Test item",
        "id": "4f07cf23-cd0f-42b5-99c4-efa9022adccf",
        "code": "C1",
        "vendor": "vendor 1",
        "contact": "test@test.com",
        "description": "test description"
    })
    assert response.json() == {'success': True}
    assert response.status_code == 200


def test_get_inventory_item_200():
    response = client.get("/v1/inventory/4f07cf23-cd0f-42b5-99c4-efa9022adccf")
    assert response.status_code == 200


def test_update_inventory_item_200():
    response = client.put("/v1/inventory/4f07cf23-cd0f-42b5-99c4-efa9022adccf", json={
        "name": "Test item 2",
        "code": "C2",
        "vendor": "vendor 2",
        "contact": "test2@test.com",
        "description": "test description 2"
    })
    assert response.status_code == 200


def test_delete_inventory_item_204():
    response = client.delete("/v1/inventory/4f07cf23-cd0f-42b5-99c4-efa9022adccf")
    assert response.status_code == 204
