"""
Pagination Schema
=================

Defines query parameter schema for paginated responses.
"""

from marshmallow import Schema, fields


class PaginationSchema(Schema):
    class Meta:
        name = "PaginationSchema"
        ordered = True

    page = fields.Int(load_default=1, metadata={"description": "Page number (default: 1)"})
    per_page = fields.Int(load_default=10, metadata={"description": "Items per page (default: 10, max: 100)"})
