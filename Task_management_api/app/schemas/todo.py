"""
Todo Schema
===========

Defines serialization and deserialization rules for Todo objects.
"""

from marshmallow import Schema, fields
from app.schemas.item import ItemSchema


class TodoSchema(Schema):
    class Meta:
        name = "TodoSchema"
        ordered = True

    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)

    # ✅ New fields
    description = fields.Str()
    status = fields.Str()

    user_id = fields.Int(dump_only=True)
    completed = fields.Bool()

    # ✅ Include related items
    items = fields.List(fields.Nested(ItemSchema), dump_only=True)
