from flask.views import MethodView
from flask_smorest import Blueprint, abort
from marshmallow import Schema, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError

from app.models.item import Item
from app.models.todo import Todo
from app.schemas.item import ItemSchema
from app.extensions import db
from app.business_logic.item_logic import bulk_update_items


# URL now matches: /todos/<todo_id>/items/<item_id>
blp = Blueprint("Items", "items", url_prefix="/todos", description="Operations on todo items")


# ----- Single Item CRUD ----- #
@blp.route("/<int:todo_id>/items")
class ItemsResource(MethodView):
    @jwt_required()
    @blp.response(200, ItemSchema(many=True))
    def get(self, todo_id):
        """Get all items for a todo"""
        user_id = get_jwt_identity()
        todo = Todo.query.filter_by(id=todo_id, user_id=user_id).first()
        if not todo:
            abort(404, message="Todo not found or you don't have permission")
        return todo.items

    @jwt_required()
    @blp.arguments(ItemSchema)
    @blp.response(201, ItemSchema)
    def post(self, item_data, todo_id):
        """Add new item to a todo"""
        user_id = get_jwt_identity()
        todo = Todo.query.filter_by(id=todo_id, user_id=user_id).first()
        if not todo:
            abort(404, message="Todo not found or you don't have permission")

        item = Item(**item_data, todo_id=todo.id)
        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, message=str(e))
        return item


@blp.route("/<int:todo_id>/items/<int:item_id>")
class ItemResource(MethodView):
    @jwt_required()
    @blp.response(200, ItemSchema)
    def get(self, todo_id, item_id):
        """Get item by ID"""
        user_id = get_jwt_identity()
        item = Item.query.join(Item.todo).filter(
            Item.id == item_id,
            Todo.id == todo_id,
            Todo.user_id == user_id
        ).first()
        if not item:
            abort(404, message="Item not found or you don't have permission")
        return item

    @jwt_required()
    @blp.arguments(ItemSchema(partial=True))
    @blp.response(200, ItemSchema)
    def put(self, item_data, todo_id, item_id):
        """Update item"""
        user_id = get_jwt_identity()
        item = Item.query.join(Item.todo).filter(
            Item.id == item_id,
            Todo.id == todo_id,
            Todo.user_id == user_id
        ).first()
        if not item:
            abort(404, message="Item not found or you don't have permission")

        for key, value in item_data.items():
            setattr(item, key, value)

        try:
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, message=str(e))
        return item

    @jwt_required()
    def delete(self, todo_id, item_id):
        """Delete item"""
        user_id = get_jwt_identity()
        item = Item.query.join(Item.todo).filter(
            Item.id == item_id,
            Todo.id == todo_id,
            Todo.user_id == user_id
        ).first()
        if not item:
            abort(404, message="Item not found or you don't have permission")

        try:
            db.session.delete(item)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, message=str(e))

        return {"success": True, "message": f"Item {item_id} deleted successfully"}


# ----- Bulk Update/Delete ----- #
class BulkUpdateSchema(Schema):
    item_ids = fields.List(fields.Int(), required=True)
    action = fields.Str(required=True)


@blp.route("/items/bulk")
class ItemsBulkResource(MethodView):
    @jwt_required()
    @blp.arguments(BulkUpdateSchema)
    @blp.response(200)
    def put(self, data):
        """Bulk update items (status or delete)"""
        user_id = get_jwt_identity()
        item_ids = data.get("item_ids", [])
        action = data.get("action")

        if not item_ids or not isinstance(item_ids, list):
            abort(400, message="item_ids must be a non-empty list of integers")

        success, error = bulk_update_items(user_id, item_ids, action)
        if not success:
            abort(404, message=error)

        if action == "delete":
            return {"success": True, "message": f"Items {item_ids} deleted successfully"}
        return {"success": True, "message": f"Items {item_ids} updated to '{action}' successfully"}
