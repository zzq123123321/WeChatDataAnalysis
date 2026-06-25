from fastapi import APIRouter, Query
from ..gpu_monitor import GPU_MONITOR

router = APIRouter()


@router.get("/api/gpu/status", summary="获取 GPU 实时状态")
async def get_gpu_status():
    return GPU_MONITOR.get_summary()


@router.get("/api/gpu/history", summary="获取 GPU 历史数据")
async def get_gpu_history(count: int = Query(default=60, ge=1, le=120)):
    history = GPU_MONITOR.get_history(count)
    return {
        "count": len(history),
        "history": [
            {
                "timestamp": s.timestamp,
                "gpus": [
                    {
                        "index": g.index,
                        "name": g.name,
                        "temperature": g.temperature,
                        "utilization": g.utilization,
                        "memory_used_mb": g.memory_used_mb,
                        "memory_total_mb": g.memory_total_mb,
                        "memory_percent": g.memory_percent,
                        "power_watts": g.power_watts,
                        "fan_speed": g.fan_speed,
                    }
                    for g in s.gpus
                ],
            }
            for s in history
        ],
    }


@router.get("/api/gpu/available", summary="检测 GPU 是否可用")
async def get_gpu_available():
    return {
        "nvidia_available": GPU_MONITOR.nvidia_available,
    }
