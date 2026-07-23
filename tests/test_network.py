import pytest
from utils.network import NetworkUtils


class TestNetworkUtils:
    def test_check_tcp_port_closed(self) -> None:
        result = NetworkUtils.check_tcp_port("127.0.0.1", 1, timeout=1)
        assert result["host"] == "127.0.0.1"
        assert result["port"] == 1

    def test_ping_localhost(self) -> None:
        result = NetworkUtils.ping("127.0.0.1", count=1, timeout=2)
        assert result["host"] == "127.0.0.1"

    def test_scan_serial_ports(self) -> None:
        ports = NetworkUtils.scan_serial_ports()
        assert isinstance(ports, list)
