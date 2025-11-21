"""
test_item_logic.py
This module tests the business logic related to `Item` operations under `item_logic`.

Features tested:
    • Adding items to a Todo
    • Updating item status
    • Deleting items
    • Retrieving items (single and multiple)
    • Bulk item updates (status change, deletion)
    • Error handling for invalid or missing records

Fixtures used:
    - db_session: Provides a temporary test database session.
    - fake_user: Provides a mock user for ownership validation.
    - fake_todo: Creates a Todo entry for item association.
    - fake_item: Creates an Item entry linked to the fake Todo.
"""

import pytest
from unittest.mock import patch
from app.business_logic import item_logic


#               TESTS: add_item_to_todo

@pytest.mark.parametrize(
    "todo_id,content,expected_error",
    [
        (None, "New Task", None),                 # valid Todo (fixture overrides todo_id)
        (999, "Orphan Task", "Todo not found"),   # non-existent Todo
    ],
)
def test_add_item_to_todo(db_session, fake_user, fake_todo, todo_id, content, expected_error):
    """
    Test: Adding a new item to an existing or invalid Todo.
    """
    if todo_id is None:
        todo_id = fake_todo.id

    item, error = item_logic.add_item_to_todo(todo_id=todo_id, user_id=fake_user.id, content=content)

    if expected_error:
        assert item is None
        assert expected_error in error
    else:
        assert error is None
        assert item.content == content
        assert item.todo_id == fake_todo.id


#              TESTS: update_item_status

@pytest.mark.parametrize(
    "new_status,expected_error",
    [
        ("Completed", None),          # valid update
        ("Invalid", "Invalid status"),
        ("Done", "Invalid status"),
        ("", "Invalid status"),
    ],
)
def test_update_item_status(db_session, fake_user, fake_item, new_status, expected_error):
    """
    Test: Updating the status of an existing Item.
    """
    updated_item, error = item_logic.update_item_status(
        item_id=fake_item.id, user_id=fake_user.id, new_status=new_status
    )

    if expected_error:
        assert updated_item is None
        assert expected_error in error
    else:
        assert error is None
        assert updated_item.status == new_status


def test_update_item_status_item_not_found(db_session, fake_user):
    """
    Test: Attempting to update status of a non-existent Item.
    """
    item, error = item_logic.update_item_status(item_id=999, user_id=fake_user.id, new_status="Completed")
    assert item is None
    assert "Item not found" in error


#                  TESTS: delete_item

@pytest.mark.parametrize(
    "item_id,expected_success,expected_error",
    [
        (None, True, None),                 # valid item (fixture overrides)
        (999, False, "Item not found"),     # invalid item
    ],
)
def test_delete_item(db_session, fake_user, fake_item, item_id, expected_success, expected_error):
    """
    Test: Deleting an Item from a Todo.
    """
    if item_id is None:
        item_id = fake_item.id

    success, error = item_logic.delete_item(item_id=item_id, user_id=fake_user.id)

    assert success is expected_success
    if expected_error:
        assert expected_error in error
    else:
        assert error is None


#               TESTS: get_items_for_todo

@pytest.mark.parametrize(
    "todo_id,expected_error",
    [
        (None, None),                # valid Todo (fixture overrides)
        (999, "Todo not found"),     # invalid Todo
    ],
)
def test_get_items_for_todo(db_session, fake_user, fake_todo, fake_item, todo_id, expected_error):
    """
    Test: Retrieving all items for a given Todo.
    """
    if todo_id is None:
        todo_id = fake_todo.id

    result, error = item_logic.get_items_for_todo(todo_id=todo_id, user_id=fake_user.id, page=1, per_page=5)

    if expected_error:
        assert result is None
        assert expected_error in error
    else:
        assert error is None
        assert "items" in result
        assert len(result["items"]) >= 1


#               TESTS: get_item_by_id

@pytest.mark.parametrize(
    "item_id,should_exist",
    [
        (None, True),     # valid Item (fixture overrides)
        (999, False),     # invalid Item
    ],
)
def test_get_item_by_id(db_session, fake_user, fake_item, item_id, should_exist):
    """
    Test: Fetching a specific Item by its ID.
    """
    if item_id is None:
        item_id = fake_item.id

    found = item_logic.get_item_by_id(item_id=item_id, user_id=fake_user.id)

    if should_exist:
        assert found is not None
        assert found.id == fake_item.id
    else:
        assert found is None


#             TESTS: bulk_update_items

@pytest.mark.parametrize(
    "action,expected_success,expected_error",
    [
        ("Completed", True, None),          # valid bulk status update
        ("delete", True, None),             # valid bulk delete
        ("InvalidAction", False, "Invalid action"),  # invalid operation
    ],
)
def test_bulk_update_items(db_session, fake_user, fake_item, action, expected_success, expected_error):
    """
    Test: Performing bulk actions on multiple items.
    """
    success, error = item_logic.bulk_update_items(
        user_id=fake_user.id, item_ids=[fake_item.id], action=action
    )

    assert success is expected_success
    if expected_error:
        assert expected_error in error
    else:
        assert error is None


def test_bulk_update_items_not_found(db_session, fake_user):
    """
    Test: Bulk updating non-existent item IDs.
    """
    success, error = item_logic.bulk_update_items(user_id=fake_user.id, item_ids=[999], action="Completed")
    assert success is False
    assert "Item not found" in error


#                 TESTS WITH MOCKING

def test_add_item_with_mocked_todo(fake_user):
    """
    Test: Mock Todo query to simulate 'Todo not found' behavior.
    """
    with patch("app.business_logic.item_logic.Todo.query.filter_by") as mock_filter:
        mock_filter.return_value.first.return_value = None
        item, error = item_logic.add_item_to_todo(todo_id=1, user_id=fake_user.id, content="Fake Task")
        assert item is None
        assert "Todo not found" in error
