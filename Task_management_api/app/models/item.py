from app.extensions import db
from datetime import date


class Item(db.Model):
    __tablename__ = "items"

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(255), nullable=False)

    # Replace done with status
    status = db.Column(db.String(50), default="Pending", nullable=False)

    due_date = db.Column(db.Date, nullable=True)

    todo_id = db.Column(db.Integer, db.ForeignKey("todos.id"), nullable=False)
    todo = db.relationship("Todo", back_populates="items")
