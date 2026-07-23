import pytest
from utils.session import SessionManager
from utils.profiles import ProfileManager
from modbus.models import ConnectionSettings, ConnectionType, PollSettings, Parity, ModbusFunction


class TestSessionManager:
    def test_save_and_load(self, tmp_path) -> None:
        mgr = SessionManager(str(tmp_path))
        conn = ConnectionSettings(
            connection_type=ConnectionType.TCP,
            host="10.0.0.1",
            port=502,
        )
        poll = PollSettings(
            function_code=ModbusFunction.READ_HOLDING_REGISTERS,
            start_address=100,
            quantity=20,
        )
        mgr.save("test_session", conn, poll)
        loaded_conn, loaded_poll = mgr.load("test_session")
        assert loaded_conn.host == "10.0.0.1"
        assert loaded_conn.port == 502
        assert loaded_poll.start_address == 100
        assert loaded_poll.quantity == 20

    def test_list_sessions(self, tmp_path) -> None:
        mgr = SessionManager(str(tmp_path))
        conn = ConnectionSettings()
        poll = PollSettings()
        mgr.save("session1", conn, poll)
        mgr.save("session2", conn, poll)
        sessions = mgr.list_sessions()
        assert "session1" in sessions
        assert "session2" in sessions

    def test_delete(self, tmp_path) -> None:
        mgr = SessionManager(str(tmp_path))
        conn = ConnectionSettings()
        poll = PollSettings()
        mgr.save("to_delete", conn, poll)
        mgr.delete("to_delete")
        assert "to_delete" not in mgr.list_sessions()
