"""Allowed values for status/type columns (stored as strings in the DB)."""
from enum import Enum


class StrEnum(str, Enum):
    """String enum with a helper to list raw values."""

    def __str__(self) -> str:
        return self.value

    @classmethod
    def values(cls) -> list[str]:
        return [member.value for member in cls]


class DoctorStatus(StrEnum):
    AVAILABLE = "AVAILABLE"
    BUSY = "BUSY"
    ON_BREAK = "ON_BREAK"
    UNAVAILABLE = "UNAVAILABLE"


class AppointmentStatus(StrEnum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"
    NO_SHOW = "NO_SHOW"


class QueueStatus(StrEnum):
    WAITING = "WAITING"
    READY = "READY"
    CALLED = "CALLED"
    IN_CONSULTATION = "IN_CONSULTATION"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class AvailabilityStatus(StrEnum):
    AVAILABLE = "AVAILABLE"
    BREAK = "BREAK"
    UNAVAILABLE = "UNAVAILABLE"


class QueueEventType(StrEnum):
    PATIENT_JOINED = "PATIENT_JOINED"
    COMPLETED = "COMPLETED"
    EMERGENCY_ADDED = "EMERGENCY_ADDED"
    BREAK = "BREAK"
    UNAVAILABLE = "UNAVAILABLE"
    DELAY = "DELAY"


class PredictionType(StrEnum):
    WAIT_TIME = "WAIT_TIME"
    LOAD = "LOAD"
    QUEUE_LENGTH = "QUEUE_LENGTH"


class LoadLevel(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
