from enum import Enum
from socket import VM_SOCKETS_INVALID_VERSION


class Speaker(str, Enum):
    Albert = "albert"
    Mari = "mari"
    Kalev = "kalev"
    Vesta = "vesta"
    Kylli = "kylli"
    Külli = "kylli"
    Meelis = "meelis"



class State(str, Enum):
    QUEUED = "queued"
    IN_PROGRESS = "in progress"
    COMPLETED = "completed"
    EXPIRED = "expired"
    ERROR = "error"
