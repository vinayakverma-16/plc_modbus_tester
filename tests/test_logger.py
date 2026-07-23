import os
import pytest
from logger.log_manager import LogManager


class TestLogManager:
    def test_start_session(self, tmp_path) -> None:
        lm = LogManager(str(tmp_path))
        fpath = lm.start_session()
        assert fpath is not None
        assert os.path.exists(str(tmp_path))

    def test_log_txt(self, tmp_path) -> None:
        lm = LogManager(str(tmp_path))
        lm.set_format("txt")
        lm.log({"timestamp": "12:00:00", "type": "INFO", "message": "test"})
        files = os.listdir(str(tmp_path))
        assert len(files) > 0
        assert any(f.endswith(".txt") for f in files)

    def test_log_csv(self, tmp_path) -> None:
        lm = LogManager(str(tmp_path))
        lm.set_format("csv")
        lm.log({"timestamp": "12:00:00", "type": "INFO", "message": "test", "data": {}})
        files = os.listdir(str(tmp_path))
        assert any(f.endswith(".csv") for f in files)

    def test_log_json(self, tmp_path) -> None:
        lm = LogManager(str(tmp_path))
        lm.set_format("json")
        lm.log({"timestamp": "12:00:00", "type": "INFO", "message": "test", "data": {}})
        files = os.listdir(str(tmp_path))
        assert any(f.endswith(".json") for f in files)

    def test_clear_logs(self, tmp_path) -> None:
        lm = LogManager(str(tmp_path))
        lm.set_format("txt")
        lm.log({"timestamp": "12:00:00", "type": "INFO", "message": "test"})
        lm.clear_logs()
        files = os.listdir(str(tmp_path))
        assert len(files) == 0
