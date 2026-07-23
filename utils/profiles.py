import os
import json
from typing import Optional

from modbus.models import ConnectionSettings, ConnectionType, Parity


class ProfileManager:
    def __init__(self, profile_dir: str = "profiles") -> None:
        self._profile_dir = profile_dir
        os.makedirs(profile_dir, exist_ok=True)

    def save(self, name: str, settings: ConnectionSettings) -> str:
        data = {
            "type": settings.connection_type.value,
            "host": settings.host,
            "port": settings.port,
            "com_port": settings.com_port,
            "baud_rate": settings.baud_rate,
            "parity": settings.parity.value,
            "stop_bits": settings.stop_bits,
            "data_bits": settings.data_bits,
            "timeout": settings.timeout,
            "slave_id": settings.slave_id,
            "auto_reconnect": settings.auto_reconnect,
            "retry_count": settings.retry_count,
        }
        fpath = os.path.join(self._profile_dir, f"{name}.json")
        with open(fpath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return fpath

    def load(self, name: str) -> ConnectionSettings:
        fpath = os.path.join(self._profile_dir, f"{name}.json")
        if not os.path.exists(fpath):
            raise FileNotFoundError(f"Profile '{name}' not found")
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return ConnectionSettings(
            connection_type=ConnectionType(data["type"]),
            host=data.get("host", "127.0.0.1"),
            port=data.get("port", 502),
            com_port=data.get("com_port", "COM1"),
            baud_rate=data.get("baud_rate", 9600),
            parity=Parity(data.get("parity", "N")),
            stop_bits=data.get("stop_bits", 1),
            data_bits=data.get("data_bits", 8),
            timeout=data.get("timeout", 3),
            slave_id=data.get("slave_id", 1),
            auto_reconnect=data.get("auto_reconnect", False),
            retry_count=data.get("retry_count", 3),
        )

    def list_profiles(self) -> list[str]:
        profiles = []
        for fname in os.listdir(self._profile_dir):
            if fname.endswith(".json"):
                profiles.append(fname[:-5])
        return sorted(profiles)

    def delete(self, name: str) -> None:
        fpath = os.path.join(self._profile_dir, f"{name}.json")
        if os.path.exists(fpath):
            os.remove(fpath)
