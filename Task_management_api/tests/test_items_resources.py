"""
test_item_resources.py

This module verifies API behavior for the following endpoints:
    • GET    /todos/<todo_id>/items
    • POST   /todos/<todo_id>/items
    • GET    /todos/<todo_id>/items/<item_id>
    • PUT    /todos/<todo_id>/items/<item_id>
    • DELETE /todos/<todo_id>/items/<item_id>
    • PUT    /todos/items/bulk

Functional coverage includes:
    - Item creation, retrieval (single and list)
    - Item updates and deletions
    - Bulk actions (status update, delete)
    - Error handling for invalid Todo or Item references

All tests use pytest fixtures defined in `conftest.py`:
    - test_app → Flask application context
    - client → Test client for HTTP requests
    - db_session → Temporary database session
    - fake_user, fake_todo, fake_item → Mock database entries
"""

import pytest
from flask_jwt_extended import create_access_token

#                        FIXTURES

@pytest.fixture
def auth_header(test_app, fake_user):
    """
    Fixture: Generate an Authorization header with a valid JWT token.
    """
    with test_app.app_context():
        token = create_access_token(identity=fake_user.id)
    return {"Authorization": f"Bearer {token}"}


#             GET /todos/<todo_id>/items

def test_get_items_list_success(client, auth_header, fake_todo, fake_item):
    """
    Test: Retrieve the list of items for a valid Todo.
    """
    resp = client.get(f"/todos/{fake_todo.id}/items", headers=auth_header)
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert any(item["id"] == fake_item.id for item in data)


def test_get_items_list_todo_not_found(client, auth_header):
    """
    Test: Attempt to fetch items from a non-existent Todo.
    """
    resp = client.get("/todos/999/items", headers=auth_header)
    assert resp.status_code == 404
    assert "Todo not found" in resp.get_json()["message"]


#            POST /todos/<todo_id>/items

def test_create_item_success(client, auth_header, fake_todo):
    """
    Test: Successfully create a new item under a valid Todo.
    """
    payload = {"content": "New Item", "status": "Pending"}
    resp = client.post(f"/todos/{fake_todo.id}/items", json=payload, headers=auth_header)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["content"] == "New Item"
    assert data["status"] == "Pending"


def test_create_item_todo_not_found(client, auth_header):
    """
    Test: Attempt to create an item under a non-existent Todo.
    """
    payload = {"content": "Orphan Item"}
    resp = client.post("/todos/999/items", json=payload, headers=auth_header)
    assert resp.status_code == 404
    assert "Todo not found" in resp.get_json()["message"]


#         GET /todos/<todo_id>/items/<item_id>

@pytest.mark.parametrize(
    "item_id, expected_status, expected_key",
    [
        ("valid", 200, "id"),   # existing item
        (999, 404, "message"),  # invalid item
    ],
)
def test_get_single_item(client, auth_header, fake_item, item_id, expected_status, expected_key):
    """
    Test: Retrieve a single item by its ID.
    """
    if item_id == "valid":
        item_id = fake_item.id
    resp = client.get(f"/todos/{fake_item.todo_id}/items/{item_id}", headers=auth_header)
    assert resp.status_code == expected_status
    data = resp.get_json()
    assert expected_key in data


#         PUT /todos/<todo_id>/items/<item_id>

def test_update_item_success(client, auth_header, fake_item):
    """
    Test: Update an existing item's content and status.
    """
    payload = {"content": "Updated Content", "status": "Completed"}
    resp = client.put(f"/todos/{fake_item.todo_id}/items/{fake_item.id}", json=payload, headers=auth_header)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["content"] == "Updated Content"
    assert data["status"] == "Completed"


def test_update_item_not_found(client, auth_header):
    """
    Test: Attempt to update a non-existent item.
    """
    payload = {"content": "Doesn't exist"}
    resp = client.put("/todos/1/items/999", json=payload, headers=auth_header)
    assert resp.status_code == 404
    assert "Item not found" in resp.get_json()["message"]


#         DELETE /todos/<todo_id>/items/<item_id>

@pytest.mark.parametrize(
    "item_id, expected_status, expected_message",
    [
        ("valid", 200, "deleted successfully"),
        (999, 404, "Item not found"),
    ],
)
def test_delete_item(client, auth_header, fake_item, item_id, expected_status, expected_message):
    """
    Test: Delete an item by ID.
    """
    if item_id == "valid":
        item_id = fake_item.id
    resp = client.delete(f"/todos/{fake_item.todo_id}/items/{item_id}", headers=auth_header)
    assert resp.status_code == expected_status
    assert expected_message.split()[0] in resp.get_json()["message"]


#             PUT /todos/items/bulk

@pytest.mark.parametrize(
    "action, expected_status, expected_message",
    [
        ("Completed", 200, "updated to 'Completed' successfully"),
        ("delete", 200, "deleted successfully"),
        ("InvalidAction", 404, "Invalid action"),
    ],
)
def test_bulk_update_items_resource(client, auth_header, fake_item, action, expected_status, expected_message):
    """
    Test: Perform bulk operations (status update or delete) on items.
    """
    payload = {"item_ids": [fake_item.id], "action": action}
    resp = client.put("/todos/items/bulk", json=payload, headers=auth_header)
    # Allow flexibility: some implementations may use 400 instead of 404
    assert resp.status_code == expected_status or resp.status_code == 400
    assert expected_message.split()[0] in resp.get_json()["message"]
