"""
test_user_logic.py

Covers:
    • get_user_by_id
    • get_all_users

"""

import pytest
from app.business_logic import user_logic
from app.models.user import User
from app.utils.security import hash_password


#                  TESTS: get_user_by_id

@pytest.mark.user
@pytest.mark.sanity
def test_get_user_by_id_success(fake_user):
    """
    Retrieve an existing user by ID.
    """
    user = user_logic.get_user_by_id(fake_user.id)
    assert user is not None
    assert user.email == "john@example.com"


@pytest.mark.user
@pytest.mark.regression
def test_get_user_by_id_not_found(db_session):
    """
    Attempt to fetch a user with a non-existent ID.
    """
    user = user_logic.get_user_by_id(999)
    assert user is None


@pytest.mark.user
@pytest.mark.regression
@pytest.mark.parametrize(
    "user_id,expected_email",
    [
        (1, "john@example.com"),  # Existing user
        (999, None),              # Non-existent user
    ]
)
def test_get_user_by_id_parametrized(fake_user, user_id, expected_email):
    """
    Parametrized test: get_user_by_id for multiple scenarios.
    """
    user = user_logic.get_user_by_id(user_id)
    if expected_email is None:
        assert user is None
    else:
        assert user.email == expected_email


#                   TESTS: get_all_users

@pytest.mark.user
@pytest.mark.sanity
def test_get_all_users_empty(db_session):
    """
    Returns an empty list when no users exist.
    """
    users = user_logic.get_all_users()
    assert isinstance(users, list)
    assert len(users) == 0


@pytest.mark.user
@pytest.mark.regression
def test_get_all_users_with_users(db_session):
    """
    Returns a list of all users in the database.
    """
    u1 = User(username="alice", email="alice@example.com", password=hash_password("pw1"))
    u2 = User(username="bob", email="bob@example.com", password=hash_password("pw2"))
    db_session.add_all([u1, u2])
    db_session.commit()

    users = user_logic.get_all_users()
    assert len(users) == 2
    assert {u.email for u in users} == {"alice@example.com", "bob@example.com"}


@pytest.mark.user
@pytest.mark.regression
@pytest.mark.parametrize(
    "user_data_list,expected_count,expected_emails",
    [
        ([], 0, set()),  # No users
        ([("alice", "alice@example.com"), ("bob", "bob@example.com")], 2, {"alice@example.com", "bob@example.com"}),
    ]
)
def test_get_all_users_parametrized(db_session, user_data_list, expected_count, expected_emails):
    """
    Parametrized test: get_all_users with different user setups.
    """
    for username, email in user_data_list:
        user = User(username=username, email=email, password=hash_password("pw"))
        db_session.add(user)
    db_session.commit()

    users = user_logic.get_all_users()
    assert len(users) == expected_count
    assert {u.email for u in users} == expected_emails
