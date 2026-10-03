"""Shared model helpers: timestamps, repr and enum CHECK constraints."""
from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, inspect

from app.extensions import db


def utcnow() -> datetime:
    """Timezone-aware UTC 'now' used for column defaults."""
    return datetime.now(timezone.utc)


class CreatedAtMixin:
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)


class TimestampMixin(CreatedAtMixin):
    updated_at = db.Column(db.DateTime, nullable=False, default=utcnow, onupdate=utcnow)


class ReprMixin:
    def __repr__(self) -> str:
        pk = inspect(self.__class__).primary_key[0].name
        return f"<{self.__class__.__name__} {pk}={getattr(self, pk, None)}>"


def enum_check(column: str, enum_cls, name: str) -> CheckConstraint:
    """Build a CHECK constraint restricting `column` to the enum's values."""
    allowed = ", ".join(f"'{value}'" for value in enum_cls.values())
    return CheckConstraint(f"{column} IN ({allowed})", name=name)
