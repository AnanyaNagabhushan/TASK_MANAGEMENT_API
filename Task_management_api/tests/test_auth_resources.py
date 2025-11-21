"""
test_auth_resources.py
This test module verifies the REST API endpoints under `resources/auth.py` for user authentication
and account management. It tests both successful and failure scenarios for:

    • User Registration
    • User Login
    • Forgot Password
    • Reset Password
    • Token Refresh and Logout

The tests use Flask’s test client for API simulation and Pytest fixtures for
database setup. Mocking (`unittest.mock.patch`) is used to isolate logic layers
where needed (e.g., forgot/reset password operations).

Fixtures used:
    - db_session: Temporary database session for each test.
    - client: Flask test client for simulating HTTP requests.
    - registered_user: Inserts a sample user for authentication tests.
"""

import pytest
from unittest.mock import patch
from app.models.user import User
from app.utils.security import hash_password


#                     REGISTER USER TESTS

@pytest.mark.parametrize(
    "payload, expected_status, expected_message",
    [
        ({"username": "alice", "email": "alice@example.com", "password": "mypassword"}, 201, "alice@example.com"),
        ({"username": "john", "email": "john@example.com", "password": "pass123"}, 400, "already exists")
    ]
)
def test_register_users(client, db_session, fake_user, payload, expected_status, expected_message):
    """
    Test: Parametrized registration endpoint test.

    Function tested:
        POST /auth/register

    Scenarios:
        1. Register a new user successfully (expected 201).
        2. Attempt to register an already existing user (expected 400).

    Expected Results:
        - Success → Returns user email, and user is present in DB.
        - Failure → Returns error message indicating duplication.
    """
    resp = client.post("/auth/register", json=payload)
    assert resp.status_code == expected_status
    if expected_status == 201:
        assert resp.json["email"] == expected_message
        user_in_db = db_session.query(User).filter_by(email=payload["email"]).first()
        assert user_in_db is not None
        assert user_in_db.username == payload["username"]
    else:
        assert expected_message in resp.json["message"]


#                         LOGIN TESTS

@pytest.mark.parametrize(
    "payload, expected_status, token_check",
    [
        ({"email": "john@example.com", "password": "pass123"}, 200, True),
        ({"email": "ghost@example.com", "password": "wrong"}, 401, False)
    ]
)
def test_login_users(client, fake_user, payload, expected_status, token_check):
    """
    Test: User login via POST /auth/login

    Scenarios:
        1. Successful login → Valid credentials.
        2. Invalid credentials → Nonexistent or wrong password.

    Expected Results:
        - Success → Returns access_token and refresh_token.
        - Failure → Returns HTTP 401 with message "Invalid email or password".
    """
    resp = client.post("/auth/login", json=payload)
    assert resp.status_code == expected_status
    if token_check:
        assert "access_token" in resp.json
        assert "refresh_token" in resp.json
    else:
        assert "Invalid email or password" in resp.json["message"]


#                    FORGOT PASSWORD TESTS

@pytest.mark.parametrize(
    "mock_return, email, expected_status, expected_message",
    [
        ((True, None), "john@example.com", 200, "Email exists, you may reset password"),
        ((False, "User not found"), "ghost@example.com", 404, "User not found")
    ]
)
@patch("app.resources.auth.forgot_password_logic")
def test_forgot_password(mock_forgot, client, mock_return, email, expected_status, expected_message):
    """
    Test: Forgot Password flow via POST /auth/forgot-password

    Mocked:
        - app.resources.auth.forgot_password_logic

    Scenarios:
        1. Existing user requests password reset → success.
        2. Nonexistent user → "User not found".

    Expected Results:
        - HTTP 200 with success message for valid user.
        - HTTP 404 for unknown email.
    """
    mock_forgot.return_value = mock_return
    resp = client.post("/auth/forgot-password", json={"email": email})
    assert resp.status_code == expected_status
    assert expected_message in resp.json["message"]


#                    RESET PASSWORD TESTS

@pytest.mark.parametrize(
    "mock_return, payload, expected_status, expected_message",
    [
        ((True, None), {"email": "john@example.com", "password": "newpass"}, 200, "Password reset successful"),
        ((False, "User not found"), {"email": "ghost@example.com", "password": "newpass"}, 400, "User not found")
    ]
)
@patch("app.resources.auth.reset_password_logic")
def test_reset_password(mock_reset, client, mock_return, payload, expected_status, expected_message):
    """
    Test: Reset Password flow via POST /auth/reset-password

    Mocked:
        - app.resources.auth.reset_password_logic

    Scenarios:
        1. Valid user resets password successfully.
        2. Nonexistent user triggers failure message.

    Expected Results:
        - HTTP 200 for successful reset.
        - HTTP 400 for invalid user with error message.
    """
    mock_reset.return_value = mock_return
    resp = client.post("/auth/reset-password", json=payload)
    assert resp.status_code == expected_status
    assert expected_message in resp.json["message"]


#             TOKEN REFRESH AND LOGOUT TESTS

def test_refresh_and_logout(client, fake_user):
    """
    Test: Full authentication token flow — login → refresh → logout.

    Functions tested:
        - POST /auth/login
        - POST /auth/refresh
        - POST /auth/logout

    Flow:
        1. Login to obtain access and refresh tokens.
        2. Use refresh token to generate a new access token.
        3. Logout using the access token to invalidate the session.

    Expected Results:
        - Login returns both tokens.
        - Refresh returns new access token.
        - Logout returns success message.
    """
    # Step 1: Login
    login_resp = client.post("/auth/login", json={
        "email": "john@example.com",
        "password": "pass123",
    })
    assert login_resp.status_code == 200
    refresh_token = login_resp.json["refresh_token"]
    access_token = login_resp.json["access_token"]

    # Step 2: Refresh token
    headers_refresh = {"Authorization": f"Bearer {refresh_token}"}
    refresh_resp = client.post("/auth/refresh", headers=headers_refresh)
    assert refresh_resp.status_code == 200
    assert "access_token" in refresh_resp.json

    # Step 3: Logout
    headers_access = {"Authorization": f"Bearer {access_token}"}
    logout_resp = client.post("/auth/logout", headers=headers_access)
    assert logout_resp.status_code == 200
    assert "Successfully logged out" in logout_resp.json["message"]

