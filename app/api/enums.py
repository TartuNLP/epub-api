from enum import Enum


class Language(str, Enum):
    ESTONIAN = "et"


class State(str, Enum):
    QUEUED = "queued"
    IN_PROGRESS = "in progress"
    COMPLETED = "completed"
    EXPIRED = "expired"
    ERROR = "error"
