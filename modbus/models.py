from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class ConnectionType(Enum):
    TCP = "TCP"
    RTU = "RTU"
    ASCII = "ASCII"


class Parity(Enum):
    NONE = "N"
    EVEN = "E"
    ODD = "O"


class ModbusFunction(Enum):
    READ_COILS = 1
    READ_INPUTS = 2
    READ_HOLDING_REGISTERS = 3
    READ_INPUT_REGISTERS = 4
    WRITE_SINGLE_COIL = 5
    WRITE_SINGLE_REGISTER = 6
    WRITE_MULTIPLE_COILS = 15
    WRITE_MULTIPLE_REGISTERS = 16


@dataclass
class ConnectionSettings:
    connection_type: ConnectionType = ConnectionType.TCP
    host: str = "127.0.0.1"
    port: int = 502
    com_port: str = "COM1"
    baud_rate: int = 9600
    parity: Parity = Parity.NONE
    stop_bits: int = 1
    data_bits: int = 8
    timeout: int = 3
    slave_id: int = 1
    auto_reconnect: bool = False
    retry_count: int = 3


@dataclass
class PollSettings:
    function_code: ModbusFunction = ModbusFunction.READ_HOLDING_REGISTERS
    start_address: int = 0
    quantity: int = 10
    poll_interval_ms: int = 1000
    continuous: bool = True


@dataclass
class RegisterData:
    address: int
    value: int = 0
    previous_value: int = 0
    changed: bool = False

    @property
    def hex_str(self) -> str:
        return f"{self.value:04X}"

    @property
    def binary_str(self) -> str:
        return f"{self.value:016b}"

    @property
    def float_str(self) -> str:
        import struct
        try:
            b = struct.pack(">H", self.value)
            return f"{struct.unpack('>e', b)[0]:.6f}"
        except Exception:
            return "N/A"

    @property
    def signed_str(self) -> str:
        if self.value > 32767:
            return str(self.value - 65536)
        return str(self.value)

    @property
    def unsigned_str(self) -> str:
        return str(self.value)

    @property
    def ascii_str(self) -> str:
        try:
            high = (self.value >> 8) & 0xFF
            low = self.value & 0xFF
            chars = []
            if 32 <= high <= 126:
                chars.append(chr(high))
            else:
                chars.append(".")
            if 32 <= low <= 126:
                chars.append(chr(low))
            else:
                chars.append(".")
            return "".join(chars)
        except Exception:
            return ".."


@dataclass
class PacketRecord:
    timestamp: str
    direction: str
    hex_data: str
    ascii_data: str
    crc: str
    error: str = ""
    length: int = 0


@dataclass
class ConnectionStats:
    packets_sent: int = 0
    packets_received: int = 0
    errors: int = 0
    last_error: str = ""
    connected: bool = False
    latency_ms: float = 0.0
