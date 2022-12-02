from enum import Enum

class PacketType(Enum):
    DATA = 1
    ACK = 2
    SYN = 3
    SYN_ACK = 4
    NAK = 5