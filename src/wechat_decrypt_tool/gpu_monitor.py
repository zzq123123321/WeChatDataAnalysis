import subprocess
import json
import re
import threading
import time
from dataclasses import dataclass, field, asdict
from typing import Optional

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


@dataclass
class GPUInfo:
    index: int
    name: str
    temperature: Optional[float] = None
    utilization: Optional[float] = None
    memory_used_mb: Optional[float] = None
    memory_total_mb: Optional[float] = None
    memory_percent: Optional[float] = None
    power_watts: Optional[float] = None
    power_limit_watts: Optional[float] = None
    fan_speed: Optional[int] = None
    driver_version: Optional[str] = None
    cuda_version: Optional[str] = None
    processes: list[dict] = field(default_factory=list)


@dataclass
class GPUSnapshot:
    timestamp: float
    gpus: list[GPUInfo]


class GPUMonitor:
    _instance: Optional["GPUMonitor"] = None
    _lock = threading.Lock()

    def __init__(self):
        self._history: list[GPUSnapshot] = []
        self._max_history = 120
        self._nvidia_smi_available: Optional[bool] = None
        self._poll_interval = 2.0
        self._running = False
        self._thread: Optional[threading.Thread] = None

    @classmethod
    def instance(cls) -> "GPUMonitor":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    @property
    def nvidia_available(self) -> bool:
        if self._nvidia_smi_available is None:
            self._nvidia_smi_available = self._check_nvidia_smi()
        return self._nvidia_smi_available

    @staticmethod
    def _check_nvidia_smi() -> bool:
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
                capture_output=True, text=True, timeout=5,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0,
            )
            return result.returncode == 0 and bool(result.stdout.strip())
        except Exception:
            return False

    def _query_nvidia(self) -> list[GPUInfo]:
        query_fields = [
            "index", "name", "temperature.gpu", "utilization.gpu",
            "memory.used", "memory.total", "power.draw", "power.limit",
            "fan.speed", "driver_version",
        ]
        query_str = ",".join(query_fields)
        try:
            result = subprocess.run(
                ["nvidia-smi", f"--query-gpu={query_str}", "--format=csv,noheader,nounits"],
                capture_output=True, text=True, timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0,
            )
            if result.returncode != 0:
                return []

            gpus = []
            for line in result.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = [p.strip() for p in line.split(",")]
                if len(parts) < 10:
                    continue

                def _float_or_none(s: str) -> Optional[float]:
                    s = s.strip().replace("%", "")
                    try:
                        return float(s) if s and s.lower() not in ("[not supported]", "n/a", "") else None
                    except ValueError:
                        return None

                def _int_or_none(s: str) -> Optional[int]:
                    s = s.strip().replace("%", "")
                    try:
                        return int(s) if s and s.lower() not in ("[not supported]", "n/a", "") else None
                    except ValueError:
                        return None

                mem_used = _float_or_none(parts[4])
                mem_total = _float_or_none(parts[5])
                mem_pct = round((mem_used / mem_total) * 100, 1) if mem_used is not None and mem_total and mem_total > 0 else None

                gpu = GPUInfo(
                    index=int(parts[0]) if parts[0].isdigit() else 0,
                    name=parts[1],
                    temperature=_float_or_none(parts[2]),
                    utilization=_float_or_none(parts[3]),
                    memory_used_mb=mem_used,
                    memory_total_mb=mem_total,
                    memory_percent=mem_pct,
                    power_watts=_float_or_none(parts[6]),
                    power_limit_watts=_float_or_none(parts[7]),
                    fan_speed=_int_or_none(parts[8]),
                    driver_version=parts[9] if parts[9].lower() not in ("[not supported]", "n/a", "") else None,
                )
                gpu.processes = self._query_nvidia_processes(gpu.index)
                gpus.append(gpu)

            if gpus:
                cuda_ver = self._query_cuda_version()
                for g in gpus:
                    g.cuda_version = cuda_ver

            return gpus
        except Exception:
            return []

    def _query_nvidia_processes(self, gpu_index: int) -> list[dict]:
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-compute-apps=pid,process_name,used_memory", "--format=csv,noheader,nounits", f"--id={gpu_index}"],
                capture_output=True, text=True, timeout=5,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0,
            )
            if result.returncode != 0:
                return []

            procs = []
            for line in result.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = [p.strip() for p in line.split(",")]
                if len(parts) < 3:
                    continue
                try:
                    procs.append({
                        "pid": int(parts[0]),
                        "name": parts[1],
                        "memory_mb": float(parts[2]) if parts[2] else 0,
                    })
                except (ValueError, IndexError):
                    continue
            return procs
        except Exception:
            return []

    def _query_cuda_version(self) -> Optional[str]:
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=cuda_version", "--format=csv,noheader"],
                capture_output=True, text=True, timeout=5,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0,
            )
            if result.returncode == 0:
                ver = result.stdout.strip().split("\n")[0].strip()
                return ver if ver and ver.lower() not in ("[not supported]", "n/a", "") else None
        except Exception:
            pass
        return None

    def _query_wmi(self) -> list[GPUInfo]:
        try:
            import wmi
            c = wmi.WMI()
            gpus = []
            for i, gpu in enumerate(c.Win32_VideoController()):
                info = GPUInfo(
                    index=i,
                    name=gpu.Name or "Unknown GPU",
                    driver_version=gpu.DriverVersion or None,
                    memory_total_mb=round(int(gpu.AdapterRAM) / (1024 * 1024), 0) if gpu.AdapterRAM else None,
                )
                gpus.append(info)
            return gpus
        except ImportError:
            pass
        except Exception:
            pass
        return []

    def _query_dxdiag(self) -> list[GPUInfo]:
        try:
            result = subprocess.run(
                ["wmic", "path", "Win32_VideoController", "get", "Name,AdapterRAM,DriverVersion", "/format:csv"],
                capture_output=True, text=True, timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0,
            )
            if result.returncode != 0:
                return []

            gpus = []
            lines = result.stdout.strip().split("\n")
            for line in lines[1:]:
                if not line.strip():
                    continue
                parts = [p.strip() for p in line.split(",")]
                if len(parts) < 3:
                    continue
                try:
                    ram_bytes = int(parts[2]) if parts[2].isdigit() else 0
                    gpus.append(GPUInfo(
                        index=len(gpus),
                        name=parts[1],
                        driver_version=parts[3] if len(parts) > 3 and parts[3] else None,
                        memory_total_mb=round(ram_bytes / (1024 * 1024), 0) if ram_bytes else None,
                    ))
                except (ValueError, IndexError):
                    continue
            return gpus
        except Exception:
            return []

    def snapshot(self) -> GPUSnapshot:
        gpus: list[GPUInfo] = []
        if self.nvidia_available:
            gpus = self._query_nvidia()
        if not gpus:
            gpus = self._query_wmi()
        if not gpus:
            gpus = self._query_dxdiag()
        return GPUSnapshot(timestamp=time.time(), gpus=gpus)

    def _poll_loop(self):
        while self._running:
            snap = self.snapshot()
            with self._lock:
                self._history.append(snap)
                if len(self._history) > self._max_history:
                    self._history = self._history[-self._max_history:]
            time.sleep(self._poll_interval)

    def start(self, interval: float = 2.0):
        if self._running:
            return
        self._poll_interval = max(1.0, interval)
        self._running = True
        self._thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)

    def get_current(self) -> Optional[GPUSnapshot]:
        with self._lock:
            if self._history:
                return self._history[-1]
        return None

    def get_history(self, count: int = 60) -> list[GPUSnapshot]:
        with self._lock:
            return list(self._history[-count:])

    def get_summary(self) -> dict:
        snap = self.get_current()
        if not snap or not snap.gpus:
            return {"available": False, "gpu_count": 0, "gpus": []}

        gpu_list = []
        for g in snap.gpus:
            gpu_list.append({
                "index": g.index,
                "name": g.name,
                "temperature": g.temperature,
                "utilization": g.utilization,
                "memory_used_mb": g.memory_used_mb,
                "memory_total_mb": g.memory_total_mb,
                "memory_percent": g.memory_percent,
                "power_watts": g.power_watts,
                "power_limit_watts": g.power_limit_watts,
                "fan_speed": g.fan_speed,
                "driver_version": g.driver_version,
                "cuda_version": g.cuda_version,
                "process_count": len(g.processes),
                "processes": g.processes[:10],
            })

        return {
            "available": True,
            "gpu_count": len(snap.gpus),
            "timestamp": snap.timestamp,
            "gpus": gpu_list,
        }


GPU_MONITOR = GPUMonitor.instance()
