from __future__ import annotations

from typing import Any

from sqlalchemy import JSON, TypeDecorator, Uuid
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import sqltypes


class JSONType(TypeDecorator):
    """JSONB on Postgres, plain JSON elsewhere."""

    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(postgresql.JSONB())
        return dialect.type_descriptor(JSON())


class ArrayType(TypeDecorator):
    """ARRAY on Postgres, JSON-encoded list elsewhere."""

    impl = JSON
    cache_ok = True

    def __init__(self, item_type: sqltypes.TypeEngine[Any], *, as_tuple: bool = False) -> None:
        self.item_type = item_type
        self.as_tuple = as_tuple
        super().__init__()

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(postgresql.ARRAY(self.item_type, as_tuple=self.as_tuple))
        return dialect.type_descriptor(JSON())

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if dialect.name == "postgresql":
            return value
        return list(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return list(value)


GuidType = Uuid
