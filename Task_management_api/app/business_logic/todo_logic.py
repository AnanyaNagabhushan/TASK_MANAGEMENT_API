"""
Todo Business Logic
===================

Encapsulates database operations for Todo model.
"""

from app.models.todo import Todo
from app.extensions import db


def create_todo(title, user_id, description=None, status="In Progress"):
    """Create a new Todo for a given user."""
    user_id = int(user_id)
    todo = Todo(title=title, description=description, status=status, user_id=user_id)
    db.session.add(todo)
    db.session.commit()
    return todo


def get_todos(user_id, page=1, per_page=10):
    """Retrieve paginated list of todos for a user."""
    user_id = int(user_id)
    return Todo.query.filter_by(user_id=user_id).paginate(
        page=page, per_page=per_page, error_out=False
    ).items


def get_todo_by_id(todo_id, user_id):
    """Retrieve a specific Todo by ID for a user."""
    return Todo.query.filter_by(id=todo_id, user_id=user_id).first()


def update_todo(todo_id, user_id, data):
    """Update a Todo (title, description, status, completed)."""
    user_id = int(user_id)
    todo = Todo.query.filter_by(id=todo_id, user_id=user_id).first()
    if not todo:
        return None, "Todo not found"

    if "title" in data:
        todo.title = data["title"]
    if "description" in data:
        todo.description = data["description"]
    if "status" in data:
        todo.status = data["status"]
    if "completed" in data:
        todo.completed = data["completed"]

    db.session.commit()
    return todo, None


def delete_todo(todo_id, user_id):
    """Delete a Todo (cascade delete items)."""
    user_id = int(user_id)
    todo = Todo.query.filter_by(id=todo_id, user_id=user_id).first()
    if not todo:
        return False, "Todo not found"

    db.session.delete(todo)
    db.session.commit()
    return True, None



def bulk_update_todos(user_id, todo_ids, action, status=None):
    try:
        todos = Todo.query.filter(Todo.id.in_(todo_ids), Todo.user_id == user_id).all()
        if not todos:
            return False, "No matching todos found"

        if action == "delete":
            for t in todos:
                db.session.delete(t)
        elif action == "update_status":
            if not status:
                return False, "Missing status for bulk update"
            for t in todos:
                t.status = status
        else:
            return False, "Invalid action"

        db.session.commit()
        return True, None
    except Exception as e:
        db.session.rollback()
        return False, str(e)

