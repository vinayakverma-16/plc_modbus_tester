import os
import json
from typing import Optional

from modbus.models import ConnectionSettings, PollSettings, ConnectionType, Parity, ModbusFunction


class SessionManager:
    def __init__(self, session_dir: str = "sessions") -> None:
        self._session_dir = session_dir
        os.makedirs(session_dir, exist_ok=True)

    def save(self, name: str, conn: ConnectionSettings, poll: PollSettings) -> str:
        data = {
            "connection": {
                "type": conn.connection_type.value,
                "host": conn.host,
                "port": conn.port,
                "com_port": conn.com_port,
                "baud_rate": conn.baud_rate,
                "parity": conn.parity.value,
                "stop_bits": conn.stop_bits,
                "data_bits": conn.data_bits,
                "timeout": conn.timeout,
                "slave_id": conn.slave_id,
                "auto_reconnect": conn.auto_reconnect,
                "retry_count": conn.retry_count,
            },
            "poll": {
                "function_code": poll.function_code.value,
                "start_address": poll.start_address,
                "quantity": poll.quantity,
                "poll_interval_ms": poll.poll_interval_ms,
                "continuous": poll.continuous,
            }
        }
        fpath = os.path.join(self._session_dir, f"{name}.json")
        with open(fpath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return fpath

    def load(self, name: str) -> tuple[ConnectionSettings, PollSettings]:
        fpath = os.path.join(self._session_dir, f"{name}.json")
        if not os.path.exists(fpath):
            raise FileNotFoundError(f"Session '{name}' not found")
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)
        cd = data["connection"]
        conn = ConnectionSettings(
            connection_type=ConnectionType(cd["type"]),
            host=cd.get("host", "127.0.0.1"),
            port=cd.get("port", 502),
            com_port=cd.get("com_port", "COM1"),
            baud_rate=cd.get("baud_rate", 9600),
            parity=Parity(cd.get("parity", "N")),
            stop_bits=cd.get("stop_bits", 1),
            data_bits=cd.get("data_bits", 8),
            timeout=cd.get("timeout", 3),
            slave_id=cd.get("slave_id", 1),
            auto_reconnect=cd.get("auto_reconnect", False),
            retry_count=cd.get("retry_count", 3),
        )
        pd = data["poll"]
        poll = PollSettings(
            function_code=ModbusFunction(pd.get("function_code", 3)),
            start_address=pd.get("start_address", 0),
            quantity=pd.get("quantity", 10),
            poll_interval_ms=pd.get("poll_interval_ms", 1000),
            continuous=pd.get("continuous", True),
        )
        return conn, poll

    def list_sessions(self) -> list[str]:
        sessions = []
        for fname in os.listdir(self._session_dir):
            if fname.endswith(".json"):
                sessions.append(fname[:-5])
        return sorted(sessions)

    def delete(self, name: str) -> None:
        fpath = os.path.join(self._session_dir, f"{name}.json")
        if os.path.exists(fpath):
            os.remove(fpath)
