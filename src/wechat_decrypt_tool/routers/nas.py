from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..logging_config import get_logger
from ..nas_storage import (
    NasConfig,
    cancel_sync,
    clear_nas_config,
    connect_nas,
    disconnect_nas,
    get_nas_status,
    get_sync_status,
    load_nas_config,
    load_nas_password,
    save_nas_config,
    sync_databases_to_nas,
)
from ..path_fix import PathFixRoute

router = APIRouter(route_class=PathFixRoute)
logger = get_logger(__name__)


class NasConnectRequest(BaseModel):
    address: str = ""
    username: str = ""
    password: str = ""
    remote_path: str = ""


class NasSetOutputRequest(BaseModel):
    path: str = ""


class NasSyncRequest(BaseModel):
    account: str = ""


class NasAutoSyncRequest(BaseModel):
    startup_auto_sync: bool = False
    realtime_auto_sync: bool = False


@router.post("/api/nas/connect", summary="连接 NAS")
async def api_nas_connect(req: NasConnectRequest):
    config = NasConfig(
        address=req.address.strip(),
        username=req.username.strip(),
        remote_path=req.remote_path.strip(),
    )
    if not config.is_valid():
        raise HTTPException(status_code=400, detail="NAS 地址不能为空")

    password = req.password
    ok, msg = connect_nas(config, password)
    if ok:
        save_nas_config(config, password)
        return {
            "success": True,
            "message": "连接成功",
            "path": f"sftp://{config.host}:{config.port}{config.sftp_path}",
            "mount": config.sftp_path,
            "sftp_host": config.host,
            "sftp_port": config.port,
            "sftp_user": config.username,
            "sftp_path": config.sftp_path,
        }
    raise HTTPException(status_code=400, detail=f"连接失败: {msg}")


@router.post("/api/nas/disconnect", summary="断开 NAS")
async def api_nas_disconnect():
    config = load_nas_config()
    if not config.is_valid():
        raise HTTPException(status_code=400, detail="未配置 NAS")

    ok, msg = disconnect_nas(config)
    return {"success": ok, "message": msg if not ok else "已断开"}


@router.get("/api/nas/status", summary="查询 NAS 连接状态")
async def api_nas_status():
    config = load_nas_config()
    status = get_nas_status(config)
    status["config"] = {
        "address": config.address,
        "username": config.username,
        "remote_path": config.remote_path,
    }
    status["has_password"] = bool(load_nas_password())
    status["mount"] = config.sftp_path
    status["sftp_host"] = config.host
    status["sftp_port"] = config.port
    status["sftp_user"] = config.username
    status["sftp_path"] = config.sftp_path
    from ..app_paths import get_output_dir, get_output_databases_dir
    status["output_dir"] = str(get_output_dir())
    status["output_databases_dir"] = str(get_output_databases_dir())
    return status


@router.post("/api/nas/sync", summary="触发数据库增量同步到 NAS")
async def api_nas_sync(req: NasSyncRequest = NasSyncRequest()):
    ok, msg = sync_databases_to_nas(account=req.account)
    if ok:
        return {"success": True, "message": msg}
    from fastapi import HTTPException
    raise HTTPException(status_code=400, detail=msg)


@router.post("/api/nas/sync/cancel", summary="取消正在运行的同步")
async def api_nas_sync_cancel():
    ok, msg = cancel_sync()
    if ok:
        return {"success": True, "message": msg}
    from fastapi import HTTPException
    raise HTTPException(status_code=400, detail=msg)


@router.get("/api/nas/sync/status", summary="查询同步进度")
async def api_nas_sync_status():
    return get_sync_status()


@router.get("/api/nas/auto-sync", summary="读取自动同步配置")
async def api_nas_auto_sync_get():
    settings_path = _get_nas_settings_path()
    data = {}
    if settings_path.is_file():
        try:
            existing = json.loads(settings_path.read_text(encoding="utf-8") or "{}")
            if isinstance(existing, dict):
                data = existing
        except Exception:
            pass
    auto = data.get("nas_auto_sync", {}) or {}
    return {
        "startup_auto_sync": bool(auto.get("startup_auto_sync", False)),
        "realtime_auto_sync": bool(auto.get("realtime_auto_sync", False)),
    }


@router.post("/api/nas/auto-sync", summary="保存自动同步配置")
async def api_nas_auto_sync_set(req: NasAutoSyncRequest):
    settings_path = _get_nas_settings_path()
    try:
        settings_path.parent.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass
    data: dict = {}
    if settings_path.is_file():
        try:
            existing = json.loads(settings_path.read_text(encoding="utf-8") or "{}")
            if isinstance(existing, dict):
                data = existing
        except Exception:
            pass
    data["nas_auto_sync"] = {
        "startup_auto_sync": bool(req.startup_auto_sync),
        "realtime_auto_sync": bool(req.realtime_auto_sync),
    }
    settings_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"success": True}


def _get_nas_settings_path() -> Path:
    from ..app_paths import get_data_dir
    p = get_data_dir() / "output" / "runtime_settings.json"
    if not p.parent.is_dir():
        p = Path.cwd() / "output" / "runtime_settings.json"
    return p

@router.post("/api/nas/set-output", summary="将 NAS 路径设为 output 目录")
async def api_nas_set_output(req: NasSetOutputRequest):
    target_path = str(req.path or "").strip()
    if not target_path:
        raise HTTPException(status_code=400, detail="路径不能为空")

    target = Path(target_path)
    try:
        target.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"无法创建目录: {e}")

    if not target.is_dir():
        raise HTTPException(status_code=400, detail="路径不是有效目录")

    settings_path = _get_nas_settings_path()
    try:
        settings_path.parent.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass
    data: dict = {}
    if settings_path.is_file():
        try:
            existing = json.loads(settings_path.read_text(encoding="utf-8") or "{}")
            if isinstance(existing, dict):
                data = existing
        except Exception:
            pass
    data["nas_output_dir"] = target_path
    settings_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("[nas] output 目录已设为: %s", target_path)
    return {"success": True, "path": target_path}


@router.post("/api/nas/clear-output", summary="清除 NAS output 目录设置，恢复默认")
async def api_nas_clear_output():
    settings_path = _get_nas_settings_path()
    changed = False
    if settings_path.is_file():
        try:
            data = json.loads(settings_path.read_text(encoding="utf-8") or "{}")
            if isinstance(data, dict) and "nas_output_dir" in data:
                data.pop("nas_output_dir")
                settings_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
                changed = True
        except Exception:
            pass
    return {"success": True, "changed": changed}


@router.post("/api/nas/clear-config", summary="清除全部 NAS 配置")
async def api_nas_clear_config():
    clear_nas_config()
    return {"success": True}
