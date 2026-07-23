import binascii
from typing import Union


class CRCConverter:
    @staticmethod
    def crc16_modbus(data: Union[bytes, str]) -> int:
        if isinstance(data, str):
            data = data.encode()
        crc = 0xFFFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x0001:
                    crc = (crc >> 1) ^ 0xA001
                else:
                    crc >>= 1
        return crc

    @staticmethod
    def crc16_hex(data: Union[bytes, str]) -> str:
        crc = CRCConverter.crc16_modbus(data)
        return f"{crc:04X}"

    @staticmethod
    def crc32(data: Union[bytes, str]) -> str:
        if isinstance(data, str):
            data = data.encode()
        return f"{binascii.crc32(data) & 0xFFFFFFFF:08X}"

    @staticmethod
    def hex_string_to_bytes(hex_str: str) -> bytes:
        hex_str = hex_str.replace(" ", "").replace("\n", "").replace("\r", "")
        return bytes(int(hex_str[i:i+2], 16) for i in range(0, len(hex_str), 2))

    @staticmethod
    def verify_crc16(hex_packet: str) -> bool:
        hex_str = hex_packet.replace(" ", "").replace("\n", "").replace("\r", "")
        if len(hex_str) < 4:
            return False
        data_hex = hex_str[:-4]
        received_crc = int(hex_str[-4:], 16)
        data_bytes = CRCConverter.hex_string_to_bytes(data_hex)
        calculated_crc = CRCConverter.crc16_modbus(data_bytes)
        return calculated_crc == received_crc
