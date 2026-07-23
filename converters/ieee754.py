import struct
from typing import Union


class IEEE754Converter:
    @staticmethod
    def float_to_hex(value: float) -> str:
        return f"{struct.unpack('>I', struct.pack('>f', value))[0]:08X}"

    @staticmethod
    def hex_to_float(hex_str: str) -> float:
        val = int(hex_str, 16)
        return struct.unpack('>f', struct.pack('>I', val))[0]

    @staticmethod
    def double_to_hex(value: float) -> str:
        return f"{struct.unpack('>Q', struct.pack('>d', value))[0]:016X}"

    @staticmethod
    def hex_to_double(hex_str: str) -> float:
        val = int(hex_str, 16)
        return struct.unpack('>d', struct.pack('>Q', val))[0]

    @staticmethod
    def two_registers_to_float(high: int, low: int) -> float:
        combined = (high << 16) | low
        return struct.unpack('>f', struct.pack('>I', combined))[0]

    @staticmethod
    def float_to_two_registers(value: float) -> tuple[int, int]:
        packed = struct.pack('>f', value)
        combined = struct.unpack('>I', packed)[0]
        return (combined >> 16) & 0xFFFF, combined & 0xFFFF

    @staticmethod
    def four_registers_to_double(r1: int, r2: int, r3: int, r4: int) -> float:
        combined = (r1 << 48) | (r2 << 32) | (r3 << 16) | r4
        return struct.unpack('>d', struct.pack('>Q', combined))[0]

    @staticmethod
    def double_to_four_registers(value: float) -> tuple[int, int, int, int]:
        packed = struct.pack('>d', value)
        combined = struct.unpack('>Q', packed)[0]
        return (
            (combined >> 48) & 0xFFFF,
            (combined >> 32) & 0xFFFF,
            (combined >> 16) & 0xFFFF,
            combined & 0xFFFF,
        )
