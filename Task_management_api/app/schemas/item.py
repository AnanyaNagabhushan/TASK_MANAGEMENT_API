from marshmallow import Schema, fields, validate
from datetime import date

class ItemSchema(Schema):
    class Meta:
        name = "ItemSchema"
        ordered = True

    id = fields.Int(dump_only=True)
    content = fields.Str(required=True)
    status = fields.Str(
        validate=validate.OneOf(["Pending", "Partially Completed", "Completed"]),
        load_default="Pending",  # Default value when not provided
    )
    due_date = fields.Date(allow_none=True)
    todo_id = fields.Int(dump_only=True)

    # Computed field: True if due_date is in the past and item is not completed
    overdue = fields.Method("get_overdue", dump_only=True)

    def get_overdue(self, obj):
        if obj.due_date and obj.status != "Completed" and obj.due_date < date.today():
            return True
        return False
