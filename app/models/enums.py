from enum import Enum


class AppointmentStatus(str, Enum):
    SCHEDULED = "SCHEDULED"
    CONFIRMED = "CONFIRMED"
    CHECKED_IN = "CHECKED_IN"
    IN_CONSULTATION = "IN_CONSULTATION"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    NO_SHOW = "NO_SHOW"


class QueueStatus(str, Enum):
    WAITING = "WAITING"
    READY = "READY"
    CALLED = "CALLED"
    IN_CONSULTATION = "IN_CONSULTATION"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    NO_SHOW = "NO_SHOW"


class ConsultationType(str, Enum):
    IN_PERSON = "IN_PERSON"
    ONLINE = "ONLINE"
    FOLLOW_UP = "FOLLOW_UP"


class NotificationType(str, Enum):
    GENERAL = "GENERAL"
    APPOINTMENT = "APPOINTMENT"
    QUEUE = "QUEUE"
    MEDICAL = "MEDICAL"
    SYSTEM = "SYSTEM"
