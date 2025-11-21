from app.extensions import db
from app.models.user import User
from app.utils.security import hash_password, verify_password
from flask_jwt_extended import create_access_token, create_refresh_token


def register_user(username, email, password):
    """
    Register a new user with hashed password.
    Returns (user, error_message)
    """
    try:
        # Check if user already exists (username or email)
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()
        if existing_user:
            return None, "User with this username or email already exists."

        # Hash the password before storing
        hashed_pw = hash_password(password)

        new_user = User(
            username=username,
            email=email,
            password=hashed_pw
        )
        db.session.add(new_user)
        db.session.commit()

        return new_user, None

    except Exception as e:
        print("Register user error:", e)
        db.session.rollback()
        return None, "Internal server error"


def login_user(email, password):
    """
    Authenticate user and return JWT tokens.
    Returns (token_data, error_message)
    """
    try:
        user = User.query.filter_by(email=email).first()

        if user and verify_password(password, user.password):
            access_token = create_access_token(identity=str(user.id))
            refresh_token = create_refresh_token(identity=str(user.id))
            return {
                "access_token": access_token,
                "refresh_token": refresh_token
            }, None

        return None, "Invalid email or password"

    except Exception as e:
        print("Login error:", e)
        return None, "Internal server error"
def forgot_password_logic(email):
    user = User.query.filter_by(email=email).first()
    if not user:
        return False, "User not found"
    # No email sending for now
    return True, None

def reset_password_logic(email, new_password):
    user = User.query.filter_by(email=email).first()
    if not user:
        return False, "User not found"
    user.password = hash_password(new_password)
    db.session.commit()
    return True, None