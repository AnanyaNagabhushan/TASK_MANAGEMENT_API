"""
conftest.py
This module sets up reusable pytest fixtures and configuration for testing the Task Management API.
It provides:
- Global warning suppression for cleaner test outputs.
- Flask app and database setup/teardown using fixtures.
- Predefined fake user, todo, and item data for test scenarios.
"""

import warnings
import pytest
from main import create_app
from app.extensions import db
from app.models.user import User
from app.models.todo import Todo
from app.models.item import Item
from app.utils.security import hash_password
from app.business_logic import todo_logic

# Ignore Warnings #
# These suppress unnecessary warnings from external libraries and SQLite.
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", message=".*Query.get.*")  # Ignore SQLAlchemy legacy warning
warnings.filterwarnings("ignore", category=ResourceWarning)  # Ignore unclosed DB resource warnings


#  App Fixture #
@pytest.fixture(scope="session")
def test_app():
    """
    Creates a Flask app instance configured for testing.

    This fixture initializes the app using a lightweight SQLite in-memory database
    and disables unnecessary features like CSRF protection and migrations.

    Scope: session (shared across all tests)
    Yields:
        Flask app instance with application context pushed.
    """
    class TestConfig:
        SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        TESTING = True
        WTF_CSRF_ENABLED = False
        JWT_SECRET_KEY = "test-secret"

    # Create and configure test app
    app = create_app(test_config=TestConfig)

    # Push the application context for database and extensions
    ctx = app.app_context()
    ctx.push()

    yield app

    # Cleanup: Pop context after all tests are done
    ctx.pop()


# DB Fixture #
@pytest.fixture(scope="function")
def db_session(test_app):
    """
    Provides a clean database session for each test function.

    This fixture:
    - Creates all tables before each test.
    - Rolls back any uncommitted transactions.
    - Drops all tables and closes connections after each test.

    Scope: function (isolated for every test)
    Yields:
        SQLAlchemy session for database operations.
    """
    db.create_all()
    try:
        yield db.session
    finally:
        # Rollback and close session after test
        db.session.rollback()
        db.session.close()

        # Drop all tables to maintain test isolation
        db.drop_all()

        # Dispose engine to prevent "unclosed database" warnings
        db.engine.dispose()


#  Test Client Fixture #
@pytest.fixture
def client(test_app):
    """
    Returns a test client for simulating HTTP requests.

    This allows testing API endpoints without running the actual Flask server.

    Args:
        test_app: The Flask test application fixture.
    Returns:
        Flask test client object.
    """
    return test_app.test_client()


# Fake User Fixture #
@pytest.fixture
def fake_user(db_session):
    """
    Creates a sample user record for use in tests.

    This user acts as a base for other entities like todos and items.

    Args:
        db_session: Active database session.
    Returns:
        User: Persisted user object.
    """
    user = User(username="john", email="john@example.com", password=hash_password("pass123"))
    db_session.add(user)
    db_session.commit()
    return user


# Fake Todo Fixture #
@pytest.fixture
def fake_todo(db_session, fake_user):
    """
    Creates a fake 'Todo' entry associated with the fake user.

    Uses the todo_logic layer to simulate real-world behavior.

    Args:
        db_session: Active database session.
        fake_user: Pre-created user fixture.
    Returns:
        Todo: Persisted todo object.
    """
    todo = todo_logic.create_todo(
        title="Test Todo",
        description="This is a test todo",
        status="In Progress",
        user_id=fake_user.id,
    )
    return todo


# Fake Item Fixture #
@pytest.fixture
def fake_item(db_session, fake_todo):
    """
    Creates a fake 'Item' entry linked to the fake todo.

    This fixture helps in testing item-related logic and API endpoints.

    Args:
        db_session: Active database session.
        fake_todo: Pre-created todo fixture.
    Returns:
        Item: Persisted item object.
    """
    item = Item(content="Test Item", todo_id=fake_todo.id, status="Pending")
    db_session.add(item)
    db_session.commit()
    return item
