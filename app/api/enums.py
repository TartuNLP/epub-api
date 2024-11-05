from enum import Enum
from socket import VM_SOCKETS_INVALID_VERSION


class Speaker(str, Enum):
    Albert = "albert"
    Mari = "mari"
    Indrek = "indrek"
    Meelis = "meelis"
    Kalev = "kalev"
    Peeter = "peeter"
    Kylli = "kylli"
    Külli = "kylli"
    Tambet = "tambet"
    Liivika = "liivika"
    Vesta = "vesta"


class State(str, Enum):
    QUEUED = "queued"
    IN_PROGRESS = "in progress"
    COMPLETED = "completed"
    EXPIRED = "expired"
    ERROR = "error"
