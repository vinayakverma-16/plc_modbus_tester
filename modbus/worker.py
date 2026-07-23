import time
import struct
from datetime import datetime
from typing import Optional, Callable

from PySide6.QtCore import QThread, Signal, QMutex, QMutexLocker

from modbus.models import (
    ConnectionSettings, ConnectionType, PollSettings,
    ModbusFunction, RegisterData, PacketRecord, ConnectionStats,
)


class ModbusWorker(QThread):
    data_received = Signal(list)
    packet_logged = Signal(object)
    connection_changed = Signal(bool, str)
    error_occurred = Signal(str)
    stats_updated = Signal(object)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._mutex = QMutex()
        self._running = False
        self._paused = False
        self._polling = False
        self._client: Optional[object] = None
        self._settings: ConnectionSettings = ConnectionSettings()
        self._poll_settings: PollSettings = PollSettings()
        self._stats: ConnectionStats = ConnectionStats()
        self._registers: dict[int, RegisterData] = {}

    @property
    def stats(self) -> ConnectionStats:
        return self._stats

    def connect_device(self, settings: ConnectionSettings) -> None:
        with QMutexLocker(self._mutex):
            self._settings = settings
            self._disconnect_client()
            self._stats = ConnectionStats()
            try:
                if settings.connection_type == ConnectionType.TCP:
                    from pymodbus.client import ModbusTcpClient
                    self._client = ModbusTcpClient(
                        host=settings.host,
                        port=settings.port,
                        timeout=settings.timeout,
                    )
                elif settings.connection_type == ConnectionType.RTU:
                    from pymodbus.client import ModbusSerialClient
                    self._client = ModbusSerialClient(
                        method="rtu",
                        port=settings.com_port,
                        baudrate=settings.baud_rate,
                        parity=settings.parity.value,
                        stopbits=settings.stop_bits,
                        bytesize=settings.data_bits,
                        timeout=settings.timeout,
                    )
                elif settings.connection_type == ConnectionType.ASCII:
                    from pymodbus.client import ModbusSerialClient
                    self._client = ModbusSerialClient(
                        method="ascii",
                        port=settings.com_port,
                        baudrate=settings.baud_rate,
                        parity=settings.parity.value,
                        stopbits=settings.stop_bits,
                        bytesize=settings.data_bits,
                        timeout=settings.timeout,
                    )
                result = self._client.connect()
                self._stats.connected = result
                self.connection_changed.emit(result, "Connected" if result else "Connection failed")
            except Exception as e:
                self._stats.connected = False
                self.connection_changed.emit(False, str(e))

    def disconnect(self) -> None:
        with QMutexLocker(self._mutex):
            self._disconnect_client()

    def _disconnect_client(self) -> None:
        if self._client and self._client.is_socket_open():
            try:
                self._client.close()
            except Exception:
                pass
        self._client = None
        self._stats.connected = False

    def start_polling(self, poll_settings: PollSettings) -> None:
        with QMutexLocker(self._mutex):
            self._poll_settings = poll_settings
            self._polling = True
            self._paused = False

    def stop_polling(self) -> None:
        with QMutexLocker(self._mutex):
            self._polling = False
            self._paused = False

    def pause_polling(self) -> None:
        with QMutexLocker(self._mutex):
            self._paused = True

    def resume_polling(self) -> None:
        with QMutexLocker(self._mutex):
            self._paused = False

    def write_register(self, address: int, value: int, slave_id: int) -> bool:
        with QMutexLocker(self._mutex):
            if not self._client or not self._client.is_socket_open():
                return False
            try:
                result = self._client.write_register(address, value, slave=slave_id)
                self._log_packet("TX", f"06 {address:04X} {value:04X}", "")
                if result:
                    self._stats.packets_sent += 1
                    self.stats_updated.emit(self._stats)
                return bool(result)
            except Exception as e:
                self._log_packet("TX", f"06 {address:04X} {value:04X}", str(e))
                return False

    def write_coil(self, address: int, value: bool, slave_id: int) -> bool:
        with QMutexLocker(self._mutex):
            if not self._client or not self._client.is_socket_open():
                return False
            try:
                result = self._client.write_coil(address, value, slave=slave_id)
                self._log_packet("TX", f"05 {address:04X} {1 if value else 0:04X}", "")
                if result:
                    self._stats.packets_sent += 1
                    self.stats_updated.emit(self._stats)
                return bool(result)
            except Exception as e:
                self._log_packet("TX", f"05 {address:04X} {1 if value else 0:04X}", str(e))
                return False

    def read_once(self) -> list[RegisterData]:
        with QMutexLocker(self._mutex):
            return self._do_read()

    def _do_read(self) -> list[RegisterData]:
        if not self._client or not self._client.is_socket_open():
            return []
        settings = self._poll_settings
        try:
            result = None
            if settings.function_code == ModbusFunction.READ_HOLDING_REGISTERS:
                result = self._client.read_holding_registers(
                    settings.start_address, settings.quantity, slave=self._settings.slave_id
                )
            elif settings.function_code == ModbusFunction.READ_INPUT_REGISTERS:
                result = self._client.read_input_registers(
                    settings.start_address, settings.quantity, slave=self._settings.slave_id
                )
            elif settings.function_code == ModbusFunction.READ_COILS:
                result = self._client.read_coils(
                    settings.start_address, settings.quantity, slave=self._settings.slave_id
                )
            elif settings.function_code == ModbusFunction.READ_INPUTS:
                result = self._client.read_discrete_inputs(
                    settings.start_address, settings.quantity, slave=self._settings.slave_id
                )

            if result and not result.isError():
                self._stats.packets_received += 1
                self.stats_updated.emit(self._stats)
                registers = []
                now = datetime.now().strftime("%H:%M:%S.%f")[:12]
                if hasattr(result, 'bits') and result.bits is not None:
                    hex_parts = []
                    ascii_parts = []
                    for i, bit in enumerate(result.bits):
                        addr = settings.start_address + i
                        prev = self._registers.get(addr, RegisterData(address=addr))
                        reg = RegisterData(address=addr, value=1 if bit else 0, previous_value=prev.value)
                        reg.changed = reg.value != reg.previous_value
                        self._registers[addr] = reg
                        registers.append(reg)
                        hex_parts.append(f"{'0001' if bit else '0000'}")
                        c = "1" if bit else "0"
                        if 32 <= ord(c) <= 126:
                            ascii_parts.append(c)
                        else:
                            ascii_parts.append(".")
                    self._log_packet("RX", " ".join(hex_parts), "".join(ascii_parts))
                elif hasattr(result, 'registers') and result.registers is not None:
                    hex_parts = []
                    ascii_parts = []
                    for i, val in enumerate(result.registers):
                        addr = settings.start_address + i
                        prev = self._registers.get(addr, RegisterData(address=addr))
                        reg = RegisterData(address=addr, value=val, previous_value=prev.value)
                        reg.changed = reg.value != reg.previous_value
                        self._registers[addr] = reg
                        registers.append(reg)
                        hex_parts.append(f"{val:04X}")
                        high = (val >> 8) & 0xFF
                        low = val & 0xFF
                        for b in (high, low):
                            if 32 <= b <= 126:
                                ascii_parts.append(chr(b))
                            else:
                                ascii_parts.append(".")
                    self._log_packet("RX", " ".join(hex_parts), "".join(ascii_parts))
                return registers
            elif result and result.isError():
                self._stats.errors += 1
                err_msg = str(result)
                self._stats.last_error = err_msg
                self.error_occurred.emit(err_msg)
                self.stats_updated.emit(self._stats)
            return []
        except Exception as e:
            self._stats.errors += 1
            self._stats.last_error = str(e)
            self.error_occurred.emit(str(e))
            self.stats_updated.emit(self._stats)
            return []

    def _log_packet(self, direction: str, hex_data: str, ascii_data: str) -> None:
        now = datetime.now().strftime("%H:%M:%S.%f")[:12]
        import binascii
        crc_val = binascii.crc_hqx(hex_data.replace(" ", "").encode(), 0)
        record = PacketRecord(
            timestamp=now,
            direction=direction,
            hex_data=hex_data,
            ascii_data=ascii_data,
            crc=f"{crc_val:04X}",
            length=len(hex_data.replace(" ", "")) // 2,
        )
        self.packet_logged.emit(record)

    def run(self) -> None:
        self._running = True
        while self._running:
            if not self._polling or self._paused:
                self.msleep(100)
                continue
            with QMutexLocker(self._mutex):
                registers = self._do_read()
                if registers:
                    self.data_received.emit(registers)
            self.msleep(self._poll_settings.poll_interval_ms)

    def stop(self) -> None:
        self._running = False
        self._polling = False
        with QMutexLocker(self._mutex):
            self._disconnect_client()
        self.wait()
