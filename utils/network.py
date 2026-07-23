import subprocess
import platform
import socket
from typing import Optional


class NetworkUtils:
    @staticmethod
    def ping(host: str, count: int = 4, timeout: int = 5) -> dict:
        result = {"host": host, "reachable": False, "avg_ms": 0.0, "output": ""}
        try:
            param = "-n" if platform.system().lower() == "windows" else "-c"
            timeout_param = "-w" if platform.system().lower() == "windows" else "-W"
            timeout_val = str(timeout * 1000) if platform.system().lower() == "windows" else str(timeout)
            output = subprocess.run(
                ["ping", param, str(count), timeout_param, timeout_val, host],
                capture_output=True, text=True, timeout=timeout + 5
            )
            result["output"] = output.stdout + output.stderr
            result["reachable"] = output.returncode == 0
            for line in output.stdout.split("\n"):
                if "avg" in line.lower() or "average" in line.lower() or "mdev" in line.lower():
                    import re
                    nums = re.findall(r"(\d+\.?\d*)\s*ms", line)
                    if nums:
                        vals = [float(n) for n in nums]
                        result["avg_ms"] = sum(vals) / len(vals)
                        break
        except Exception as e:
            result["output"] = str(e)
        return result

    @staticmethod
    def check_tcp_port(host: str, port: int, timeout: int = 3) -> dict:
        result = {"host": host, "port": port, "open": False, "error": ""}
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            code = sock.connect_ex((host, port))
            sock.close()
            result["open"] = code == 0
        except Exception as e:
            result["error"] = str(e)
        return result

    @staticmethod
    def scan_serial_ports() -> list[dict]:
        ports = []
        try:
            import serial.tools.list_ports
            for p in serial.tools.list_ports.comports():
                ports.append({
                    "device": p.device,
                    "description": p.description,
                    "hwid": p.hwid,
                    "vid": p.vid,
                    "pid": p.pid,
                })
        except Exception:
            if platform.system().lower() == "windows":
                import glob
                for i in range(256):
                    try:
                        port = f"COM{i}"
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.settimeout(0.1)
                        s.connect((port, 0))
                        s.close()
                    except Exception:
                        pass
        return ports

    @staticmethod
    def get_network_interfaces() -> list[dict]:
        interfaces = []
        try:
            import psutil
            for name, addrs in psutil.net_if_addrs().items():
                for addr in addrs:
                    if addr.family == socket.AF_INET:
                        interfaces.append({
                            "name": name,
                            "ip": addr.address,
                            "netmask": addr.netmask,
                            "broadcast": addr.broadcast,
                        })
        except ImportError:
            hostname = socket.gethostname()
            try:
                ip = socket.gethostbyname(hostname)
                interfaces.append({"name": "default", "ip": ip, "netmask": "", "broadcast": ""})
            except Exception:
                pass
        return interfaces
