from typing import Optional

from modbus.models import ConnectionSettings, PollSettings, ConnectionStats, ConnectionType
from modbus.worker import ModbusWorker


class ModbusClient:
    def __init__(self) -> None:
        self._worker: Optional[ModbusWorker] = None
        self._create_worker()

    def _create_worker(self) -> None:
        if self._worker is not None:
            self._worker.stop()
        self._worker = ModbusWorker()

    @property
    def worker(self) -> ModbusWorker:
        if self._worker is None:
            self._create_worker()
        return self._worker

    @property
    def stats(self) -> ConnectionStats:
        return self.worker.stats

    def connect(self, settings: ConnectionSettings) -> None:
        self.worker.connect_device(settings)

    def disconnect(self) -> None:
        self.worker.disconnect()

    def start_polling(self, poll_settings: PollSettings) -> None:
        self.worker.start_polling(poll_settings)
        if not self.worker.isRunning():
            self.worker.start()

    def stop_polling(self) -> None:
        self.worker.stop_polling()

    def pause_polling(self) -> None:
        self.worker.pause_polling()

    def resume_polling(self) -> None:
        self.worker.resume_polling()

    def read_once(self):
        return self.worker.read_once()

    def write_register(self, address: int, value: int, slave_id: int) -> bool:
        return self.worker.write_register(address, value, slave_id)

    def write_coil(self, address: int, value: bool, slave_id: int) -> bool:
        return self.worker.write_coil(address, value, slave_id)

    def cleanup(self) -> None:
        if self._worker is not None:
            self._worker.stop()
            self._worker = None
