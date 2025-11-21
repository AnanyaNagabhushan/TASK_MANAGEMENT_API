"""
Todo Model
==========

Defines the Todo database table with relationships to items.
Now includes description and status fields.
"""

from app.extensions import db


class Todo(db.Model):
    __tablename__ = "todos"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)

    # ✅ New fields
    description = db.Column(db.Text, nullable=True)
    status = db.Column(
        db.String(50),
        default="In Progress"
    )  # Completed, In Progress, Partially Complete

    completed = db.Column(db.Boolean, default=False)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # ✅ Cascade delete items
    items = db.relationship(
        "Item",
        back_populates="todo",
        cascade="all, delete-orphan"
    )
