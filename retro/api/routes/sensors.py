from fastapi import APIRouter, HTTPException
from retro.api.schemas import SensorControlRequest, SensorStatusResponse
from retro.core.engine import engine
from retro.core.config import config

router = APIRouter(prefix="/sensors", tags=["sensors"])


@router.get("", response_model=list[SensorStatusResponse])
async def list_sensors():
    results = []
    for name, sensor_cfg in config.sensors.items():
        s = engine._sensors.get(name)
        results.append(SensorStatusResponse(
            name=name,
            running=s.is_running() if s else False,
            config={"enabled": sensor_cfg.enabled, "port": sensor_cfg.port} if hasattr(sensor_cfg, "port") else {"enabled": sensor_cfg.enabled},
        ))
    return results


@router.post("/{name}/start")
async def start_sensor(name: str):
    from retro.core.config import config as cfg
    sensor_cfg = cfg.sensors.get(name)
    if not sensor_cfg or not sensor_cfg.enabled:
        raise HTTPException(status_code=400, detail=f"Sensor '{name}' not enabled in config")
    sensor = engine._sensors.get(name)
    if not sensor:
        raise HTTPException(status_code=404, detail=f"Sensor '{name}' not found")
    if sensor.is_running():
        return {"status": "already_running", "name": name}
    import asyncio
    asyncio.create_task(sensor.start(engine.ingest_event))
    return {"status": "started", "name": name}


@router.post("/{name}/stop")
async def stop_sensor(name: str):
    sensor = engine._sensors.get(name)
    if not sensor:
        raise HTTPException(status_code=404, detail=f"Sensor '{name}' not found")
    await sensor.stop()
    return {"status": "stopped", "name": name}
