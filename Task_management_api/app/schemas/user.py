from marshmallow import Schema, fields
from app.schemas.todo import TodoSchema


class UserSchema(Schema):
    class Meta:
        name = "UserResponse"
        ordered = True

    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(load_only=True, required=True)
    todos = fields.List(fields.Nested(TodoSchema), dump_only=True)


class UserCreateSchema(Schema):
    class Meta:
        name = "UserCreate"
        ordered = True

    username = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(load_only=True, required=True)


class UserLoginSchema(Schema):
    class Meta:
        name = "UserLogin"
        ordered = True

    email = fields.Email(required=True)
    password = fields.Str(load_only=True, required=True)


class UserResetPasswordSchema(Schema):
    class Meta:
        name = "UserResetPassword"
        ordered = True

    email = fields.Email(required=True)
    password = fields.Str(load_only=True, required=True)


class UserForgotPasswordSchema(Schema):
    class Meta:
        name = "UserForgotPassword"
        ordered = True

    email = fields.Email(required=True)
