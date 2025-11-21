"""
test_models.py

This module ensures correct behavior of the following SQLAlchemy models:
    • User
    • Todo
    • Item
    • TokenBlocklist

Key aspects tested:
    - Model persistence (insert, query)
    - Relationship mapping and backref integrity
    - Cascade delete between Todo → Item
    - Token blocklist creation timestamp
"""

from datetime import datetime, date, timezone
import pytest
from app.models.user import User
from app.models.todo import Todo
from app.models.item import Item
from app.models.token_blocklist import TokenBlocklist

#                      USER MODEL TESTS

def test_user_model_persistence(db_session):
    user = User(username="ananya", email="ananya@example.com", password="securepass")
    db_session.add(user)
    db_session.commit()

    fetched = db_session.query(User).filter_by(username="ananya").first()
    assert fetched is not None
    assert fetched.username == "ananya"
    assert fetched.email == "ananya@example.com"
    assert fetched.password == "securepass"
    assert isinstance(fetched.todos, list)


#                      TODO MODEL TESTS

def test_todo_model_relationship(db_session, fake_user):
    todo = Todo(
        title="Learn Pytest",
        description="Write unit tests for models",
        status="In Progress",
        completed=False,
        user_id=fake_user.id,
    )
    db_session.add(todo)
    db_session.commit()

    fetched = db_session.query(Todo).filter_by(title="Learn Pytest").first()
    assert fetched is not None
    assert fetched.user_id == fake_user.id
    assert fetched.user.username == fake_user.username
    assert isinstance(fetched.items, list)


#                      ITEM MODEL TESTS

@pytest.mark.parametrize(
    "content,status,due_date",
    [
        ("Write test for Item model", "Pending", date(2025, 10, 5)),
        ("Another test item", "Completed", date(2025, 12, 31)),
        ("Third item", "Pending", None),
    ]
)
def test_item_model_relationship(db_session, fake_todo, content, status, due_date):
    """
    Parametrized Test: Confirm Item relationship to parent Todo with multiple variations.

    Args:
        content: Item content string
        status: Item status string
        due_date: Optional due_date for the item

    Expected:
        - Item persists with correct todo_id
        - Relationship back to Todo works
        - Fields match the input values
    """
    item = Item(
        content=content,
        status=status,
        due_date=due_date,
        todo_id=fake_todo.id,
    )
    db_session.add(item)
    db_session.commit()

    fetched = db_session.query(Item).filter_by(content=content).first()
    assert fetched is not None
    assert fetched.todo_id == fake_todo.id
    assert fetched.todo.title == fake_todo.title
    assert fetched.status == status
    assert fetched.due_date == due_date


#                TOKEN BLOCKLIST MODEL TESTS

def test_token_blocklist_model(db_session):
    token = TokenBlocklist(jti="1234-5678-uuid")
    db_session.add(token)
    db_session.commit()

    fetched = db_session.query(TokenBlocklist).filter_by(jti="1234-5678-uuid").first()
    assert fetched is not None
    assert fetched.jti == "1234-5678-uuid"
    assert isinstance(fetched.created_at, datetime)


#                   CASCADE DELETE TESTS

@pytest.mark.parametrize(
    "item_contents",
    [
        (["Task 1", "Task 2"]),
        (["Single Task"]),
        (["Task A", "Task B", "Task C"]),
    ]
)
def test_cascade_delete_todo_removes_items(db_session, fake_user, item_contents):
    """
    Parametrized Test: Ensure cascading delete from Todo to multiple Items works.

    Args:
        item_contents: List of content strings for items under the Todo

    Expected:
        - All Items related to the deleted Todo should also be removed
    """
    todo = Todo(title="Cascade Test", description="Check cascade delete", user_id=fake_user.id)
    db_session.add(todo)
    db_session.commit()

    items = [Item(content=content, todo_id=todo.id) for content in item_contents]
    db_session.add_all(items)
    db_session.commit()

    assert db_session.query(Item).filter_by(todo_id=todo.id).count() == len(item_contents)

    db_session.delete(todo)
    db_session.commit()

    remaining_items = db_session.query(Item).filter_by(todo_id=todo.id).count()
    assert remaining_items == 0


#               BACKREF RELATIONSHIP TESTS

def test_backref_user_todos_and_todo_items(db_session, fake_user):
    todo = Todo(title="Backref Test", description="Check relationships", user_id=fake_user.id)
    db_session.add(todo)
    db_session.commit()

    item = Item(content="Subtask", todo_id=todo.id)
    db_session.add(item)
    db_session.commit()

    fetched_user = db_session.get(User, fake_user.id)
    assert any(t.title == "Backref Test" for t in fetched_user.todos)

    fetched_todo = db_session.get(Todo, todo.id)
    assert any(i.content == "Subtask" for i in fetched_todo.items)
