"""
test_todo_resources.py

This suite validates all RESTful operations:
    • Create Todo (POST /todos)
    • Retrieve Todos (GET /todos, GET /todos/<id>)
    • Update Todo (PUT /todos/<id>)
    • Bulk Update Todos (PUT /todos)
    • Delete Todo (DELETE /todos/<id>)

Uses pytest fixtures from conftest.py for isolated setup:
    - test_app: Flask app configured for testing
    - db_session: SQLAlchemy session
    - client: Flask test client
    - fake_user: Test user
    - fake_todo: Test todo
"""

import pytest
from flask_jwt_extended import create_access_token
from app.business_logic import todo_logic


#                        FIXTURES

@pytest.fixture
def auth_header(test_app, fake_user):
    """
    Fixture: Generate Authorization header with JWT token for API requests.
    """
    with test_app.app_context():
        token = create_access_token(identity=fake_user.id)
    return {"Authorization": f"Bearer {token}"}


#                   TESTS: POST /todos

def test_create_todo_success(client, auth_header):
    """
    Test: Successfully create a new Todo.
    """
    resp = client.post("/todos", json={"title": "New Todo"}, headers=auth_header)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["title"] == "New Todo"
    assert "id" in data


def test_create_todo_missing_title(client, auth_header):
    """
    Test: Handle missing 'title' field when creating a Todo.
    """
    resp = client.post("/todos", json={}, headers=auth_header)
    assert resp.status_code == 400
    assert "Missing field: title" in resp.get_json()["message"]


#                    TESTS: GET /todos

def test_get_todos_list(client, auth_header, fake_todo):
    """
    Test: Retrieve list of all Todos for the authenticated user.
    """
    resp = client.get("/todos", headers=auth_header)
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert len(data) >= 1


@pytest.mark.parametrize(
    "todo_id_getter, expected_status, expected_key",
    [
        (lambda fake_todo: fake_todo.id, 200, "id"),   # Existing todo
        (lambda _: 999, 403, "message"),               # Non-existent todo
    ]
)
def test_get_single_todo(client, auth_header, fake_todo, todo_id_getter, expected_status, expected_key):
    """
    Parametrized Test: Retrieve a specific Todo by ID.
    """
    todo_id = todo_id_getter(fake_todo)
    resp = client.get(f"/todos/{todo_id}", headers=auth_header)
    assert resp.status_code == expected_status
    data = resp.get_json()
    assert expected_key in data


#                   TESTS: PUT /todos/<id>

def test_update_todo_success(client, auth_header, fake_todo):
    """
    Test: Successfully update an existing Todo.
    """
    resp = client.put(
        f"/todos/{fake_todo.id}",
        json={"title": "Updated", "status": "Completed", "completed": True},
        headers=auth_header,
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["title"] == "Updated"
    assert data["status"] == "Completed"
    assert data["completed"] is True


def test_update_todo_not_found(client, auth_header):
    """
    Test: Handle update on non-existent Todo.
    """
    resp = client.put(
        "/todos/999",
        json={"title": "Doesn't exist"},
        headers=auth_header,
    )
    assert resp.status_code == 403
    assert "Todo not found" in resp.get_json()["message"]


#                   TESTS: PUT /todos (bulk update)

@pytest.mark.parametrize(
    "payload, expected_status, expected_message",
    [
        ({"action": "update_status", "status": "Completed"}, 200, "Bulk operation successful"),
        ({"action": "update_status"}, 400, "Missing status"),
        ({"action": "invalid"}, 400, "Invalid action"),
    ]
)
def test_bulk_update_status(client, auth_header, fake_todo, fake_user, payload, expected_status, expected_message):
    """
    Parametrized Test: Perform bulk operations on multiple Todos.
    """
    # Ensure another Todo exists for bulk operation
    t2 = todo_logic.create_todo("Another", fake_user.id)
    payload["todo_ids"] = [fake_todo.id, t2.id]

    resp = client.put("/todos", json=payload, headers=auth_header)
    assert resp.status_code == expected_status
    assert expected_message in resp.get_json()["message"]


#                   TESTS: DELETE /todos/<id>

@pytest.mark.parametrize(
    "todo_id_getter, expected_status, expected_message",
    [
        (lambda fake_todo: fake_todo.id, 200, "Todo deleted"),   # Success
        (lambda _: 999, 403, "Todo not found"),                  # Not found
    ]
)
def test_delete_todo(client, auth_header, fake_todo, todo_id_getter, expected_status, expected_message):
    """
    Parametrized Test: Delete a Todo by ID.
    """
    todo_id = todo_id_getter(fake_todo)
    resp = client.delete(f"/todos/{todo_id}", headers=auth_header)
    assert resp.status_code == expected_status
    assert expected_message in resp.get_json()["message"]
