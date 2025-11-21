from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import (
    jwt_required,
    get_jwt,
    get_jwt_identity,
    create_access_token,
    create_refresh_token,
)
from app.extensions import db
from app.models.token_blocklist import TokenBlocklist
from app.schemas.user import (
    UserSchema,
    UserCreateSchema,
    UserLoginSchema,
    UserResetPasswordSchema,
    UserForgotPasswordSchema,
)
from app.business_logic.auth_logic import (
    register_user,
    login_user,
    forgot_password_logic,
    reset_password_logic
)

blp = Blueprint("Auth", "auth", description="Authentication")

@blp.route("/auth/register")
class RegisterResource(MethodView):
    @blp.arguments(UserCreateSchema)
    @blp.response(201, UserSchema)
    def post(self, user_data):
        user, error = register_user(
            username=user_data["username"],
            email=user_data["email"],
            password=user_data["password"]
        )
        if error:
            abort(400, message=error)
        return user

@blp.route("/auth/login")
class LoginResource(MethodView):
    @blp.arguments(UserLoginSchema)
    def post(self, login_data):
        token_data, error = login_user(
            email=login_data["email"],
            password=login_data["password"]
        )
        if error:
            abort(401, message=error)
        return token_data

@blp.route("/auth/refresh")
class TokenRefreshResource(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        user_id = get_jwt_identity()
        new_access_token = create_access_token(identity=str(user_id))
        return {"access_token": new_access_token}

@blp.route("/auth/forgot-password")
class ForgotPasswordResource(MethodView):
    @blp.arguments(UserForgotPasswordSchema)
    def post(self, data):
        success, error = forgot_password_logic(data["email"])
        if not success:
            abort(404, message=error)
        return {"message": "Email exists, you may reset password"}, 200

@blp.route("/auth/reset-password")
class ResetPasswordResource(MethodView):
    @blp.arguments(UserResetPasswordSchema)
    def post(self, data):
        success, error = reset_password_logic(data["email"], data["password"])
        if not success:
            abort(400, message=error)
        return {"message": "Password reset successful"}, 200

# ------------------ LOGOUT ------------------
@blp.route("/auth/logout")
class LogoutUser(MethodView):
    @jwt_required()
    def post(self):
        try:
            jti = get_jwt()["jti"]
            db.session.add(TokenBlocklist(jti=jti))
            db.session.commit()
            return {"message": "Successfully logged out"}, 200
        except Exception as e:
            db.session.rollback()
            abort(500, message=f"Server error during logout: {str(e)}")
