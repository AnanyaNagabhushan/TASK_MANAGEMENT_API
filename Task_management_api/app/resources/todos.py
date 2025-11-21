"""
Todo Resource
=============

API endpoints for managing todos, including bulk operations.
"""

from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.schemas.todo import TodoSchema
from app.business_logic.todo_logic import (
    create_todo, get_todo_by_id, get_todos,
    update_todo, delete_todo, bulk_update_todos  # ✅ Import bulk function
)

blp = Blueprint("Todos", "todos", description="Manage Todos")


@blp.route("/todos", methods=["GET", "POST", "PUT"])
@blp.route("/todos/<int:todo_id>", methods=["GET", "PUT", "DELETE"])
class TodoResource(MethodView):

    @jwt_required()
    def post(self):
        """
        Create a new todo for the logged-in user.
        Required: title
        Optional: description, status
        """
        data = request.get_json()
        if not data or "title" not in data:
            abort(400, message="Missing field: title")

        user_id = int(get_jwt_identity())
        todo = create_todo(
            title=data["title"],
            description=data.get("description"),
            status=data.get("status", "In Progress"),
            user_id=user_id
        )
        return TodoSchema().dump(todo), 201

    @jwt_required()
    def get(self, todo_id=None):
        """
        Get todos (all or one) for the logged-in user.
        Supports pagination for list view.
        """
        user_id = int(get_jwt_identity())

        if todo_id:
            todo = get_todo_by_id(todo_id, user_id)
            if not todo:
                abort(403, message="Forbidden: Not your Todo or doesn't exist")
            return TodoSchema().dump(todo), 200
        else:
            page = request.args.get("page", 1, type=int)
            per_page = request.args.get("per_page", 10, type=int)
            todos = get_todos(user_id, page, per_page)
            return TodoSchema(many=True).dump(todos), 200

    @jwt_required()
    def put(self, todo_id=None):
        """
        Update a todo (title, description, status, completed)
        or perform bulk actions with JSON containing todo_ids and action.
        """
        data = request.get_json()
        if not data:
            abort(400, message="Missing request body")

        user_id = int(get_jwt_identity())

        # ✅ Bulk update/delete
        if "todo_ids" in data and "action" in data:
            success, error = bulk_update_todos(
                user_id=user_id,
                todo_ids=data["todo_ids"],
                action=data["action"],
                status=data.get("status")
            )
            if not success:
                abort(400, message=error)
            return {"message": "Bulk operation successful"}, 200

        # ✅ Single todo update
        if todo_id is None:
            abort(400, message="todo_id is required for single update")

        todo, error = update_todo(todo_id, user_id, data)
        if error:
            abort(403, message=error)
        return TodoSchema().dump(todo), 200

    @jwt_required()
    def delete(self, todo_id):
        """
        Delete a todo (and cascade its items).
        """
        user_id = int(get_jwt_identity())
        success, error = delete_todo(todo_id, user_id)
        if not success:
            abort(403, message=error)
        return {"message": "Todo deleted"}, 200
