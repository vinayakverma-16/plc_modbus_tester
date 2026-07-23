import pytest
from converters.numeric import NumericConverter
from converters.ieee754 import IEEE754Converter
from converters.ascii import ASCIIConverter
from converters.crc import CRCConverter


class TestNumericConverter:
    def test_dec_to_hex(self) -> None:
        assert NumericConverter.to_hex(255) == "FF"

    def test_hex_to_dec(self) -> None:
        assert NumericConverter.to_dec("FF", 16) == "255"

    def test_signed_to_unsigned(self) -> None:
        assert NumericConverter.signed_to_unsigned(-1, 16) == 65535

    def test_unsigned_to_signed(self) -> None:
        assert NumericConverter.unsigned_to_signed(65535, 16) == -1


class TestIEEE754Converter:
    def test_float_roundtrip(self) -> None:
        val = 3.14
        hex_str = IEEE754Converter.float_to_hex(val)
        result = IEEE754Converter.hex_to_float(hex_str)
        assert abs(result - val) < 0.001

    def test_double_roundtrip(self) -> None:
        val = 3.14159265358979
        hex_str = IEEE754Converter.double_to_hex(val)
        result = IEEE754Converter.hex_to_double(hex_str)
        assert abs(result - val) < 0.0001

    def test_two_registers_float(self) -> None:
        val = 3.14
        high, low = IEEE754Converter.float_to_two_registers(val)
        result = IEEE754Converter.two_registers_to_float(high, low)
        assert abs(result - val) < 0.001


class TestASCIIConverter:
    def test_text_to_hex(self) -> None:
        assert ASCIIConverter.text_to_hex("ABC") == "41 42 43"

    def test_hex_to_text(self) -> None:
        assert ASCIIConverter.hex_to_text("41 42 43") == "ABC"

    def test_utf8_roundtrip(self) -> None:
        text = "Hello, 世界"
        hex_str = ASCIIConverter.text_to_utf8_hex(text)
        result = ASCIIConverter.utf8_hex_to_text(hex_str)
        assert result == text


class TestCRCConverter:
    def test_crc16_modbus(self) -> None:
        data = bytes([0x01, 0x03, 0x00, 0x00, 0x00, 0x0A])
        crc = CRCConverter.crc16_modbus(data)
        assert crc > 0

    def test_verify_crc16_valid(self) -> None:
        data = bytes([0x01, 0x03, 0x00, 0x00, 0x00, 0x0A])
        crc = CRCConverter.crc16_modbus(data)
        packet = "01 03 00 00 00 0A " + f"{crc:04X}"
        assert CRCConverter.verify_crc16(packet)
