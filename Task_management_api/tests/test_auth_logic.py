import pytest
from unittest.mock import patch
from app.business_logic import auth_logic

#                     REGISTER USER TESTS

@pytest.mark.auth
@pytest.mark.parametrize("username,email,password", [
    ("alice", "alice@example.com", "mypassword"),
])
def test_register_user_success(db_session, username, email, password):
    user, err = auth_logic.register_user(username, email, password)
    assert user is not None
    assert err is None


@pytest.mark.auth
@pytest.mark.parametrize("username,email,password", [
    ("john", "john@example.com", "pass123"),
])
def test_register_user_already_exists(fake_user, username, email, password):
    user, err = auth_logic.register_user(username, email, password)
    assert user is None
    assert "already exists" in err


#                         LOGIN TESTS

@pytest.mark.auth
@pytest.mark.parametrize("email,password", [
    ("john@example.com", "pass123"),
])
def test_login_user_success(fake_user, email, password):
    tokens, err = auth_logic.login_user(email, password)
    assert tokens is not None
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    assert err is None


@pytest.mark.auth
@pytest.mark.parametrize("email,password,expected_err", [
    ("john@example.com", "wrong", "Invalid email or password"),
])
def test_login_user_invalid_password(fake_user, email, password, expected_err):
    tokens, err = auth_logic.login_user(email, password)
    assert tokens is None
    assert err == expected_err


#                  PARAMETRIZED LOGIN TESTS

@pytest.mark.auth
@pytest.mark.parametrize("email,password,expected", [
    ("john@example.com", "wrong", "Invalid email or password"),  # Wrong password
    ("doesnotexist@example.com", "pass123", "Invalid email or password"),  # Non-existent user
])
def test_login_user_parametrized(fake_user, email, password, expected):
    tokens, err = auth_logic.login_user(email, password)
    assert tokens is None
    assert err == expected


#                 MOCKED LOGIN TOKEN TESTS

@pytest.mark.auth
@patch("app.business_logic.auth_logic.create_access_token", return_value="fake_access")
@patch("app.business_logic.auth_logic.create_refresh_token", return_value="fake_refresh")
def test_login_user_with_mocks(mock_refresh, mock_access, fake_user):
    tokens, err = auth_logic.login_user("john@example.com", "pass123")
    assert tokens["access_token"] == "fake_access"
    assert tokens["refresh_token"] == "fake_refresh"
    assert err is None


#                 FORGOT PASSWORD TESTS

@pytest.mark.auth
@pytest.mark.parametrize("email,expected_success,expected_err", [
    ("john@example.com", True, None),
])
def test_forgot_password_success(fake_user, email, expected_success, expected_err):
    success, err = auth_logic.forgot_password_logic(email)
    assert success is expected_success
    assert err is expected_err


@pytest.mark.auth
@pytest.mark.parametrize("email,expected_success,expected_err", [
    ("ghost@example.com", False, "User not found"),
])
def test_forgot_password_user_not_found(db_session, email, expected_success, expected_err):
    success, err = auth_logic.forgot_password_logic(email)
    assert success is expected_success
    assert err == expected_err


#                 RESET PASSWORD TESTS

@pytest.mark.auth
@pytest.mark.parametrize("email,new_password", [
    ("john@example.com", "newpass123"),
])
def test_reset_password_success(fake_user, email, new_password):
    success, err = auth_logic.reset_password_logic(email, new_password)
    assert success is True
    assert err is None

    from app.utils.security import verify_password
    updated_user = auth_logic.User.query.filter_by(email=email).first()
    assert verify_password(new_password, updated_user.password)


@pytest.mark.auth
@pytest.mark.parametrize("email,new_password,expected_success,expected_err", [
    ("ghost@example.com", "whatever", False, "User not found"),
])
def test_reset_password_user_not_found(db_session, email, new_password, expected_success, expected_err):
    success, err = auth_logic.reset_password_logic(email, new_password)
    assert success is expected_success
    assert err == expected_err


#           MOCKED HASH FUNCTION (RESET PASSWORD)

@pytest.mark.auth
@patch("app.business_logic.auth_logic.hash_password", return_value="mocked_hashed")
def test_reset_password_with_mock(mock_hash, fake_user, db_session):
    success, err = auth_logic.reset_password_logic("john@example.com", "irrelevant")
    assert success is True
    assert err is None

    user = auth_logic.User.query.filter_by(email="john@example.com").first()
    assert user.password == "mocked_hashed"
    

#              EXCEPTION HANDLING & FAILURE TESTS

@pytest.mark.auth
def test_register_user_db_commit_failure(monkeypatch, db_session):
    def fake_commit():
        raise Exception("Simulated DB error")

    monkeypatch.setattr(auth_logic.db.session, "commit", fake_commit)

    user, err = auth_logic.register_user("bob", "bob@example.com", "secretpw")
    assert user is None
    assert err == "Internal server error"


@pytest.mark.auth
def test_login_user_db_failure(monkeypatch, test_app):
    class FakeQuery:
        def filter_by(self, *args, **kwargs):
            raise Exception("DB failure")

    with test_app.app_context():
        monkeypatch.setattr(auth_logic.User, "query", FakeQuery())
        tokens, err = auth_logic.login_user("john@example.com", "pass123")
        assert tokens is None
        assert err == "Internal server error"
