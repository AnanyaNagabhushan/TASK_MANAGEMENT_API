"""
test_todo_logic.py

This suite ensures correctness of all core functions within todo_logic:
    • get_todo_by_id
    • get_todos
    • create_todo
    • update_todo
    • delete_todo
    • bulk_update_todos

The tests verify CRUD behavior, input validation, and cascade updates/deletes.
Uses in-memory SQLite DB for isolation. Reuses fixtures from conftest.py.
"""

import pytest
from app.business_logic import todo_logic

#                     TESTS: get_todo_by_id

@pytest.mark.parametrize(
    "todo_id,should_exist",
    [
        (None, True),   # valid existing todo
        (999, False),   # non-existent todo
    ]
)
def test_get_todo_by_id(fake_todo, fake_user, todo_id, should_exist):
    """
    Test: Retrieve a todo by its ID.

    Expected:
        - Returns a valid Todo for an existing ID.
        - Returns None for non-existent IDs.
    """
    if todo_id is None:
        todo_id = fake_todo.id

    todo = todo_logic.get_todo_by_id(todo_id, fake_user.id)

    if should_exist:
        assert todo is not None
        assert todo.title == "Test Todo"
        assert todo.user_id == fake_user.id
    else:
        assert todo is None


#                       TESTS: get_todos

@pytest.mark.parametrize(
    "create_count,expected_count",
    [
        (0, 0),
        (2, 2),
    ]
)
def test_get_todos(fake_user, create_count, expected_count):
    """
    Test: Retrieve all todos for a user.

    Expected:
        - Returns correct number of todos created for a user.
    """
    for i in range(create_count):
        todo_logic.create_todo(f"Todo {i+1}", fake_user.id)
    todos = todo_logic.get_todos(fake_user.id)

    assert isinstance(todos, list)
    assert len(todos) == expected_count


#                      TESTS: create_todo

def test_create_todo(fake_user):
    """
    Test: Create a new todo for a given user.

    Expected:
        - Todo should persist with title, description, and user ID.
    """
    todo = todo_logic.create_todo("New Todo", fake_user.id, description="Desc")
    assert todo.id is not None
    assert todo.title == "New Todo"
    assert todo.description == "Desc"
    assert todo.user_id == fake_user.id


#                      TESTS: update_todo

@pytest.mark.parametrize(
    "todo_id,data,expected_error",
    [
        (None, {"title": "Updated Todo", "status": "Completed", "completed": True}, None),
        (999, {"title": "Updated"}, "Todo not found"),
    ]
)
def test_update_todo(fake_todo, fake_user, todo_id, data, expected_error):
    """
    Test: Update an existing todo or handle non-existent IDs.

    Expected:
        - Valid update should modify title, status, and completed flag.
        - Invalid todo_id should return 'Todo not found'.
    """
    if todo_id is None:
        todo_id = fake_todo.id

    todo, error = todo_logic.update_todo(todo_id, fake_user.id, data)

    if expected_error:
        assert todo is None
        assert error == expected_error
    else:
        assert error is None
        assert todo.title == "Updated Todo"
        assert todo.status == "Completed"
        assert todo.completed is True


#                      TESTS: delete_todo

@pytest.mark.parametrize(
    "todo_id,expected_success,expected_error",
    [
        (None, True, None),          # valid delete
        (999, False, "Todo not found"),  # invalid delete
    ]
)
def test_delete_todo(fake_todo, fake_user, todo_id, expected_success, expected_error):
    """
    Test: Delete an existing or non-existent todo.

    Expected:
        - Successful deletion returns True with no error.
        - Missing todo returns False with error message.
    """
    if todo_id is None:
        todo_id = fake_todo.id

    success, error = todo_logic.delete_todo(todo_id, fake_user.id)

    assert success is expected_success
    if expected_error:
        assert error == expected_error
    else:
        assert error is None


#                  TESTS: bulk_update_todos

@pytest.mark.parametrize(
    "action,extra,status_required,expected_success,expected_error",
    [
        ("update_status", {"status": "Completed"}, True, True, None),
        ("delete", {}, False, True, None),
        ("invalid", {}, False, False, "Invalid action"),
        ("update_status", {}, True, False, "Missing status for bulk update"),
    ]
)
def test_bulk_update_todos(fake_todo, fake_user, action, extra, status_required, expected_success, expected_error):
    """
    Test: Perform bulk actions on multiple todos.

    Supported actions:
        - 'update_status': Bulk change status of todos.
        - 'delete': Remove all given todos.
        - Invalid or missing params should raise errors.

    Expected:
        - Proper bulk updates and deletions reflected in DB.
        - Invalid inputs handled gracefully.
    """
    t2 = todo_logic.create_todo("Another Todo", fake_user.id)
    kwargs = {"action": action}
    kwargs.update(extra)

    success, error = todo_logic.bulk_update_todos(fake_user.id, [fake_todo.id, t2.id], **kwargs)

    assert success is expected_success
    if expected_error:
        assert error == expected_error
    else:
        assert error is None
        if action == "update_status" and expected_success:
            updated_todos = todo_logic.get_todos(fake_user.id)
            assert all(t.status == "Completed" for t in updated_todos)
        if action == "delete" and expected_success:
            todos = todo_logic.get_todos(fake_user.id)
            assert len(todos) == 0
