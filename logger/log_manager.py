import os
import json
import csv
from datetime import datetime
from typing import Optional


class LogManager:
    def __init__(self, log_dir: str = "logs") -> None:
        self._log_dir = log_dir
        self._log_file: Optional[str] = None
        self._format: str = "txt"
        self._max_size: int = 10 * 1024 * 1024
        self._max_files: int = 5
        os.makedirs(log_dir, exist_ok=True)

    @property
    def log_dir(self) -> str:
        return self._log_dir

    def set_format(self, fmt: str) -> None:
        self._format = fmt

    def start_session(self) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ext = self._format
        self._log_file = os.path.join(self._log_dir, f"session_{timestamp}.{ext}")
        return self._log_file

    def log(self, entry: dict) -> None:
        if not self._log_file:
            self.start_session()
        try:
            if self._format == "txt":
                self._log_txt(entry)
            elif self._format == "csv":
                self._log_csv(entry)
            elif self._format == "json":
                self._log_json(entry)
            self._check_rotation()
        except Exception:
            pass

    def _log_txt(self, entry: dict) -> None:
        line = (
            f"[{entry.get('timestamp', '')}] "
            f"[{entry.get('type', 'INFO')}] "
            f"{entry.get('message', '')}\n"
        )
        with open(self._log_file, "a", encoding="utf-8") as f:
            f.write(line)

    def _log_csv(self, entry: dict) -> None:
        file_exists = os.path.exists(self._log_file)
        with open(self._log_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["timestamp", "type", "message", "data"])
            if not file_exists:
                writer.writeheader()
            writer.writerow({
                "timestamp": entry.get("timestamp", ""),
                "type": entry.get("type", "INFO"),
                "message": entry.get("message", ""),
                "data": json.dumps(entry.get("data", {})),
            })

    def _log_json(self, entry: dict) -> None:
        entries = []
        if os.path.exists(self._log_file):
            with open(self._log_file, "r", encoding="utf-8") as f:
                try:
                    entries = json.load(f)
                except (json.JSONDecodeError, ValueError):
                    entries = []
        entries.append(entry)
        with open(self._log_file, "w", encoding="utf-8") as f:
            json.dump(entries, f, indent=2)

    def _check_rotation(self) -> None:
        if not self._log_file or not os.path.exists(self._log_file):
            return
        if os.path.getsize(self._log_file) > self._max_size:
            base = os.path.splitext(self._log_file)[0]
            ext = os.path.splitext(self._log_file)[1]
            for i in range(self._max_files - 1, 0, -1):
                old_name = f"{base}.{i}{ext}"
                new_name = f"{base}.{i+1}{ext}"
                if os.path.exists(old_name):
                    os.rename(old_name, new_name)
            os.rename(self._log_file, f"{base}.1{ext}")
            self._log_file = None
            self.start_session()

    def clear_logs(self) -> None:
        for fname in os.listdir(self._log_dir):
            fpath = os.path.join(self._log_dir, fname)
            try:
                if os.path.isfile(fpath):
                    os.remove(fpath)
            except Exception:
                pass
        self._log_file = None
