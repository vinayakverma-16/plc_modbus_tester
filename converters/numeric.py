from typing import Union


class NumericConverter:
    @staticmethod
    def to_hex(value: Union[int, str], from_base: int = 10) -> str:
        if isinstance(value, str):
            value = int(value, from_base)
        return f"{value:X}"

    @staticmethod
    def to_bin(value: Union[int, str], from_base: int = 10) -> str:
        if isinstance(value, str):
            value = int(value, from_base)
        return f"{value:b}"

    @staticmethod
    def to_oct(value: Union[int, str], from_base: int = 10) -> str:
        if isinstance(value, str):
            value = int(value, from_base)
        return oct(value)[2:]

    @staticmethod
    def to_dec(value: Union[int, str], from_base: int = 10) -> str:
        if isinstance(value, str):
            if from_base == 16:
                return str(int(value, 16))
            if from_base == 2:
                return str(int(value, 2))
            if from_base == 8:
                return str(int(value, 8))
        return str(value)

    @staticmethod
    def signed_to_unsigned(value: int, bits: int = 16) -> int:
        return value & ((1 << bits) - 1)

    @staticmethod
    def unsigned_to_signed(value: int, bits: int = 16) -> int:
        mask = (1 << bits) - 1
        value &= mask
        if value >= (1 << (bits - 1)):
            value -= (1 << bits)
        return value
