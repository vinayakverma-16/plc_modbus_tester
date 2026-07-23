import pytest
from modbus.models import (
    ConnectionSettings, ConnectionType, Parity, ModbusFunction,
    PollSettings, RegisterData, PacketRecord, ConnectionStats,
)


class TestConnectionSettings:
    def test_defaults(self) -> None:
        settings = ConnectionSettings()
        assert settings.connection_type == ConnectionType.TCP
        assert settings.host == "127.0.0.1"
        assert settings.port == 502
        assert settings.timeout == 3
        assert settings.slave_id == 1

    def test_rtu_settings(self) -> None:
        settings = ConnectionSettings(
            connection_type=ConnectionType.RTU,
            com_port="COM3",
            baud_rate=19200,
            parity=Parity.EVEN,
        )
        assert settings.connection_type == ConnectionType.RTU
        assert settings.com_port == "COM3"
        assert settings.baud_rate == 19200
        assert settings.parity == Parity.EVEN


class TestRegisterData:
    def test_hex_str(self) -> None:
        reg = RegisterData(address=0, value=0xABCD)
        assert reg.hex_str == "ABCD"

    def test_binary_str(self) -> None:
        reg = RegisterData(address=0, value=0b1010101010101010)
        assert reg.binary_str == "1010101010101010"

    def test_signed_positive(self) -> None:
        reg = RegisterData(address=0, value=100)
        assert reg.signed_str == "100"

    def test_signed_negative(self) -> None:
        reg = RegisterData(address=0, value=65535)
        assert reg.signed_str == "-1"

    def test_changed_flag(self) -> None:
        reg = RegisterData(address=0, value=100)
        assert reg.changed is False
        reg2 = RegisterData(address=0, value=100, previous_value=100)
        reg2.changed = reg2.value != reg2.previous_value
        assert reg2.changed is False
        reg3 = RegisterData(address=0, value=200, previous_value=100)
        reg3.changed = reg3.value != reg3.previous_value
        assert reg3.changed is True


class TestPollSettings:
    def test_defaults(self) -> None:
        poll = PollSettings()
        assert poll.function_code == ModbusFunction.READ_HOLDING_REGISTERS
        assert poll.start_address == 0
        assert poll.quantity == 10
        assert poll.poll_interval_ms == 1000
        assert poll.continuous is True


class TestConnectionStats:
    def test_defaults(self) -> None:
        stats = ConnectionStats()
        assert stats.packets_sent == 0
        assert stats.packets_received == 0
        assert stats.errors == 0
        assert stats.connected is False
