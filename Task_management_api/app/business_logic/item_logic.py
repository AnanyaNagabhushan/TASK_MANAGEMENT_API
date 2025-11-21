from app.models.item import Item
from app.models.todo import Todo
from app.extensions import db

VALID_STATUSES = ["Pending", "Partially Completed", "Completed"]


def add_item_to_todo(todo_id, user_id, content, due_date=None, status="Pending"):
    user_id = int(user_id)
    todo = Todo.query.filter_by(id=todo_id, user_id=user_id).first()
    if not todo:
        return None, "Todo not found or you don't have permission"

    item = Item(content=content, todo_id=todo.id, due_date=due_date, status=status)
    db.session.add(item)
    db.session.commit()
    return item, None


def update_item_status(item_id, user_id, new_status):
    user_id = int(user_id)
    item = Item.query.join(Item.todo).filter(Item.id == item_id, Todo.user_id == user_id).first()
    if not item:
        return None, "Item not found or you don't have permission"

    if new_status not in VALID_STATUSES:
        return None, f"Invalid status. Must be one of {VALID_STATUSES}"

    item.status = new_status
    db.session.commit()
    return item, None


def delete_item(item_id, user_id):
    user_id = int(user_id)
    item = Item.query.join(Item.todo).filter(Item.id == item_id, Todo.user_id == user_id).first()
    if not item:
        return False, "Item not found or you don't have permission"
    db.session.delete(item)
    db.session.commit()
    return True, None


def get_items_for_todo(todo_id, user_id, page=1, per_page=10):
    user_id = int(user_id)
    todo = Todo.query.filter_by(id=todo_id, user_id=user_id).first()
    if not todo:
        return None, "Todo not found or you don't have permission"

    query = Item.query.filter_by(todo_id=todo_id)
    pagination = query.paginate(page=page, per_page=min(per_page, 100), error_out=False)

    return {
        "items": pagination.items,
        "total": pagination.total,
        "page": pagination.page,
        "pages": pagination.pages,
        "per_page": pagination.per_page,
    }, None


def get_item_by_id(item_id, user_id):
    return Item.query.join(Item.todo).filter(Item.id == item_id, Todo.user_id == user_id).first()


def bulk_update_items(user_id, item_ids, action):
    user_id = int(user_id)
    items = Item.query.join(Item.todo).filter(Item.id.in_(item_ids), Todo.user_id == user_id).all()
    if not items:
        return False, "Item not found or you don't have permission"

    if action == "delete":
        for item in items:
            db.session.delete(item)
    elif action in VALID_STATUSES:
        for item in items:
            item.status = action
    else:
        return False, f"Invalid action. Must be one of {VALID_STATUSES} or 'delete'"

    db.session.commit()
    return True, None
