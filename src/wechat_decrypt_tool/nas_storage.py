from __future__ import annotations

import json
import os
import stat
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import paramiko

from .logging_config import get_logger

logger = get_logger(__name__)

NAS_CRED_TARGET = "WeChatDataAnalysis_NAS"


@dataclass
class NasConfig:
    address: str = ""
    username: str = ""
    remote_path: str = ""

    @property
    def host(self) -> str:
        addr = str(self.address or "").strip().strip("/\\")
        host = addr
        port = "22"
        if ":" in addr:
            host, _, port = addr.partition(":")
            port = port.strip() or "22"
        return host.strip()

    @property
    def port(self) -> str:
        addr = str(self.address or "").strip().strip("/\\")
        if ":" in addr:
            _, _, port = addr.partition(":")
            return port.strip() or "22"
        return "22"

    @property
    def sftp_path(self) -> str:
        rp = str(self.remote_path or "").strip().strip("/\\")
        if not rp:
            return ""
        return "/" + rp.replace("\\", "/").strip("/")

    @property
    def full_unc_path(self) -> str:
        return f"{self.host}:{self.sftp_path}"

    @property
    def webdav_url(self) -> str:
        return self.full_unc_path

    @property
    def mount_point(self) -> str:
        return ""

    def is_valid(self) -> bool:
        return bool(str(self.address or "").strip())


# --- paramiko SSH/SFTP helpers ---

def _get_ssh_client(config: NasConfig, password: str) -> paramiko.SSHClient:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        hostname=config.host,
        port=int(config.port),
        username=config.username,
        password=password,
        timeout=10,
        allow_agent=False,
        look_for_keys=False,
    )
    return client


def _ssh_exec(config: NasConfig, password: str, command: str, timeout: int = 30) -> tuple[bool, str]:
    try:
        client = _get_ssh_client(config, password)
        try:
            _stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
            out = stdout.read().decode("utf-8", errors="replace").strip()
            err = stderr.read().decode("utf-8", errors="replace").strip()
            exit_code = stdout.channel.recv_exit_status()
            if exit_code == 0:
                return True, out or "OK"
            return False, err or out or f"exit_code={exit_code}"
        finally:
            client.close()
    except paramiko.AuthenticationException:
        return False, "SSH 认证失败，请检查用户名和密码"
    except Exception as e:
        return False, str(e)


def _sftp_connect(config: NasConfig, password: str) -> paramiko.SFTPClient:
    client = _get_ssh_client(config, password)
    return client.open_sftp()


def _sftp_exec(config: NasConfig, password: str, action, timeout: int = 60) -> tuple[bool, str]:
    try:
        client = _get_ssh_client(config, password)
        try:
            sftp = client.open_sftp()
            try:
                result = action(sftp)
                return True, result
            finally:
                sftp.close()
        finally:
            client.close()
    except paramiko.AuthenticationException:
        return False, "SSH 认证失败，请检查用户名和密码"
    except Exception as e:
        return False, str(e)


# --- Password storage ---

def _password_store_path():
    from .runtime_settings import get_runtime_settings_path
    return get_runtime_settings_path().parent / "nas_password.dat"


def _save_password(account: str, password: str) -> None:
    import base64
    path = _password_store_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass
    data = base64.b64encode(password.encode("utf-8")).decode("ascii")
    try:
        path.write_text(data, encoding="utf-8")
        logger.info("[nas] 密码已保存")
    except Exception as e:
        logger.warning("[nas] 保存密码失败: %s", e)


def _load_password() -> Optional[str]:
    import base64
    path = _password_store_path()
    try:
        if path.is_file():
            data = path.read_text(encoding="utf-8").strip()
            return base64.b64decode(data).decode("utf-8")
    except Exception:
        pass
    return None


def _delete_password() -> None:
    path = _password_store_path()
    try:
        if path.is_file():
            path.unlink()
    except Exception:
        pass


# --- Config persistence ---

def save_nas_config(config: NasConfig, password: str = "") -> None:
    from .runtime_settings import get_runtime_settings_path
    path = get_runtime_settings_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass
    data: dict = {}
    if path.is_file():
        try:
            existing = json.loads(path.read_text(encoding="utf-8") or "{}")
            if isinstance(existing, dict):
                data = existing
        except Exception:
            pass
    data["nas_config"] = {
        "address": config.address,
        "username": config.username,
        "remote_path": config.remote_path,
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    if password:
        _save_password(config.username, password)
    else:
        _delete_password()


def load_nas_config() -> NasConfig:
    from .runtime_settings import get_runtime_settings_path
    path = get_runtime_settings_path()
    config = NasConfig()
    try:
        if path.is_file():
            data = json.loads(path.read_text(encoding="utf-8") or "{}")
            if isinstance(data, dict):
                nc = data.get("nas_config", {}) or {}
                if isinstance(nc, dict):
                    config.address = str(nc.get("address", "") or "")
                    config.username = str(nc.get("username", "") or "")
                    config.remote_path = str(nc.get("remote_path", "") or "")
    except Exception:
        pass
    return config


def load_nas_password() -> str:
    try:
        return _load_password() or ""
    except Exception:
        return ""


def clear_nas_config() -> None:
    from .runtime_settings import get_runtime_settings_path
    path = get_runtime_settings_path()
    try:
        if path.is_file():
            data = json.loads(path.read_text(encoding="utf-8") or "{}")
            if isinstance(data, dict):
                data.pop("nas_config", None)
                data.pop("nas_output_dir", None)
                path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        _delete_password()
    except Exception:
        pass


# --- NAS connection ---

def _verify_sftp(config: NasConfig, password: str) -> tuple[bool, str]:
    sftp_path = config.sftp_path
    try:
        client = _get_ssh_client(config, password)
        try:
            sftp = client.open_sftp()
            try:
                sftp.stat(sftp_path)
                return True, ""
            except IOError:
                try:
                    sftp.mkdir(sftp_path)
                    return True, "目录已创建"
                except IOError as e:
                    return False, f"远程路径不存在且无法创建: {sftp_path}: {e}"
            finally:
                sftp.close()
        finally:
            client.close()
    except paramiko.AuthenticationException:
        return False, "SSH 认证失败，请检查用户名和密码"
    except Exception as e:
        return False, f"SSH 连接失败: {e}"


def connect_nas(config: NasConfig, password: str) -> tuple[bool, str]:
    if not config.is_valid():
        return False, "NAS 地址无效"
    if not password:
        stored = load_nas_password()
        if stored:
            password = stored
    if not password and config.username:
        return False, "密码为空"
    if not password:
        return False, "密码为空"

    ok, msg = _verify_sftp(config, password)
    if ok:
        logger.info("[nas] SFTP 连接成功: %s@%s:%s", config.username, config.host, config.sftp_path)
    else:
        logger.warning("[nas] SFTP 连接失败: %s", msg)
    return ok, msg


def disconnect_nas(config: NasConfig) -> tuple[bool, str]:
    return True, "SFTP 无需断开"


def get_nas_status(config: NasConfig) -> dict:
    result = {
        "connected": False,
        "path": "",
        "mount": "",
        "error": "",
    }
    if not config.is_valid():
        result["error"] = "未配置 NAS"
        return result
    sftp_path = config.sftp_path
    result["path"] = f"sftp://{config.host}:{config.port}{sftp_path}"
    try:
        client = _get_ssh_client(config, load_nas_password())
        try:
            client.close()
            result["connected"] = True
        finally:
            try:
                client.close()
            except Exception:
                pass
    except Exception as e:
        result["error"] = str(e)
    return result


# --- File upload via SFTP ---

def upload_file_to_nas(local_path: str, remote_path: str) -> tuple[bool, str]:
    cfg = load_nas_config()
    password = load_nas_password()
    if not cfg.is_valid() or not password:
        return False, "NAS 未配置"

    try:
        client = _get_ssh_client(cfg, password)
        try:
            sftp = client.open_sftp()
            try:
                sftp.put(local_path, remote_path, confirm=True)
                return True, "上传成功"
            finally:
                sftp.close()
        finally:
            client.close()
    except Exception as e:
        return False, str(e)


def ensure_remote_dir(remote_dir: str) -> tuple[bool, str]:
    cfg = load_nas_config()
    password = load_nas_password()
    if not cfg.is_valid() or not password:
        return False, "NAS 未配置"

    try:
        client = _get_ssh_client(cfg, password)
        try:
            sftp = client.open_sftp()
            try:
                _sftp_mkdirs(sftp, remote_dir)
                return True, "OK"
            finally:
                sftp.close()
        finally:
            client.close()
    except Exception as e:
        return False, str(e)


def _sftp_mkdirs(sftp: paramiko.SFTPClient, remote_dir: str):
    dirs = []
    d = remote_dir.rstrip("/")
    while d and d != "/":
        dirs.append(d)
        d = "/".join(d.split("/")[:-1]) or "/"
    dirs.reverse()
    for d in dirs:
        try:
            sftp.stat(d)
        except IOError:
            sftp.mkdir(d)


# --- Sync progress & background sync ---

_sync_progress: dict = {}
_sync_lock = threading.Lock()
_sync_thread: Optional[threading.Thread] = None


def _get_sync_progress() -> dict:
    with _sync_lock:
        return dict(_sync_progress)


def _set_sync_progress(**kwargs):
    with _sync_lock:
        _sync_progress.update(kwargs)


def _reset_sync_progress():
    with _sync_lock:
        _sync_progress.clear()
        _sync_progress.update({
            "running": False,
            "completed": False,
            "stage": "",
            "total": 0,
            "current": 0,
            "current_file": "",
            "message": "",
            "error": "",
        })


_reset_sync_progress()


def _scan_local_databases(db_dir: Path) -> list[tuple[str, int]]:
    files = []
    if not db_dir.is_dir():
        return files
    for entry in db_dir.rglob("*"):
        if entry.is_file():
            rel = entry.relative_to(db_dir).as_posix()
            files.append((rel, entry.stat().st_size))
    return sorted(files, key=lambda x: x[0])


def _get_remote_file_map_sftp(sftp: paramiko.SFTPClient, remote_path: str) -> dict[str, int]:
    result = {}
    try:
        _walk_sftp(sftp, remote_path, "", result)
    except Exception as e:
        logger.warning("[nas] 远程文件扫描失败: %s", e)
    return result


def _walk_sftp(sftp: paramiko.SFTPClient, base: str, prefix: str, result: dict[str, int]):
    try:
        entries = sftp.listdir_attr(base)
    except IOError:
        return
    for entry in entries:
        name = entry.filename
        if name in (".", ".."):
            continue
        remote_full = base.rstrip("/") + "/" + name
        rel = (prefix + "/" + name).lstrip("/") if prefix else name
        if stat.S_ISDIR(entry.st_mode or 0):
            _walk_sftp(sftp, remote_full, rel, result)
        else:
            result[rel] = entry.st_size or 0


def _sync_databases_thread(local_db_dir_str: str, remote_base: str, account: str = ""):
    try:
        cfg = load_nas_config()
        password = load_nas_password()
        if not cfg.is_valid() or not password:
            _set_sync_progress(running=False, completed=False, stage="error",
                               message="NAS 未配置", error="NAS 未配置")
            return

        local_db_dir = Path(local_db_dir_str)
        if not local_db_dir.is_dir():
            _set_sync_progress(running=False, completed=False, stage="error",
                               message="本地数据库目录不存在", error="本地数据库目录不存在")
            return

        _set_sync_progress(stage="scanning", total=0, current=0,
                           current_file="", message="正在扫描本地文件...")

        local_files = _scan_local_databases(local_db_dir)
        if account:
            prefix = account.rstrip("/") + "/"
            local_files = [(p, s) for p, s in local_files if p.startswith(prefix)]
        total_local = len(local_files)
        _set_sync_progress(total=total_local, message=f"扫描到 {total_local} 个本地文件")

        _set_sync_progress(message="正在连接 NAS 并比对远程文件列表...")

        try:
            client = _get_ssh_client(cfg, password)
        except Exception as e:
            _set_sync_progress(running=False, completed=False, stage="error",
                               message=f"SSH 连接失败: {e}", error=str(e))
            return

        try:
            sftp = client.open_sftp()
            try:
                remote_databases_dir = remote_base.rstrip("/") + "/databases"
                remote_files = _get_remote_file_map_sftp(sftp, remote_databases_dir)
            finally:
                sftp.close()
        finally:
            client.close()

        to_upload = []
        for rel_path, local_size in local_files:
            remote_size = remote_files.get(rel_path)
            if remote_size is None or remote_size != local_size:
                to_upload.append((rel_path, local_size))

        if not to_upload:
            _set_sync_progress(running=False, completed=True, stage="done",
                               total=total_local, current=total_local,
                               message="同步完成，所有文件已是最新")
            return

        _set_sync_progress(stage="syncing", total=len(to_upload), current=0,
                           message=f"需要同步 {len(to_upload)} 个文件")

        # Reconnect for upload phase
        try:
            client = _get_ssh_client(cfg, password)
        except Exception as e:
            _set_sync_progress(running=False, completed=False, stage="error",
                               message=f"SSH 连接失败: {e}", error=str(e))
            return

        try:
            sftp = client.open_sftp()
            try:
                remote_databases_dir = remote_base.rstrip("/") + "/databases"
                _sftp_mkdirs(sftp, remote_databases_dir)

                for i, (rel_path, _) in enumerate(to_upload):
                    if not _get_sync_progress().get("running", False):
                        _set_sync_progress(running=False, completed=False, stage="cancelled",
                                           message="同步已取消")
                        return

                    local_file = local_db_dir / rel_path
                    remote_file = remote_databases_dir + "/" + rel_path

                    _set_sync_progress(current=i + 1, current_file=rel_path,
                                       message=f"({i + 1}/{len(to_upload)}) {rel_path}")

                    remote_dir = "/".join(remote_file.split("/")[:-1])
                    _sftp_mkdirs(sftp, remote_dir)

                    try:
                        sftp.put(str(local_file), remote_file, confirm=True)
                    except Exception as e:
                        _set_sync_progress(running=False, completed=False, stage="error",
                                           message=f"上传失败: {rel_path}: {e}",
                                           error=f"上传失败: {rel_path}: {e}")
                        return

                _set_sync_progress(running=False, completed=True, stage="done",
                                   total=len(to_upload), current=len(to_upload),
                                   message=f"同步完成，已更新 {len(to_upload)} 个文件")
            finally:
                sftp.close()
        finally:
            client.close()

    except Exception as e:
        _set_sync_progress(running=False, completed=False, stage="error",
                           message=str(e), error=str(e))


def sync_databases_to_nas(account: str = "") -> tuple[bool, str]:
    global _sync_thread
    with _sync_lock:
        if _sync_progress.get("running", False):
            return False, "同步已在运行中"
        _sync_progress.clear()
        _sync_progress.update({
            "running": False,
            "completed": False,
            "stage": "",
            "total": 0,
            "current": 0,
            "current_file": "",
            "message": "",
            "error": "",
        })

    from .app_paths import get_output_databases_dir
    cfg = load_nas_config()
    local_db_dir = get_output_databases_dir()
    remote_base = cfg.sftp_path

    if not local_db_dir.is_dir():
        return False, "本地数据库目录不存在"

    if not remote_base:
        return False, "NAS 远程路径未配置"

    label = account if account else "全部账号"
    _set_sync_progress(running=True, stage="starting", message=f"正在同步 {label}...")

    t = threading.Thread(
        target=_sync_databases_thread,
        args=(str(local_db_dir), remote_base, account),
        daemon=True,
    )
    t.start()
    _sync_thread = t
    return True, f"已开始同步 {label}"


def cancel_sync() -> tuple[bool, str]:
    with _sync_lock:
        if not _sync_progress.get("running", False):
            return False, "当前没有正在运行的同步任务"
        _sync_progress["running"] = False
    return True, "同步已取消"


def get_sync_status() -> dict:
    return _get_sync_progress()
