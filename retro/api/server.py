from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from retro import __version__, __app_name__
from retro.api.routes import dashboard, sensors, countermeasures, protection, reports, settings, health, osint

app = FastAPI(title=__app_name__, version=__version__, docs_url="/docs", redoc_url="/redoc")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(health.router, prefix="/api/v1")
app.include_router(dashboard.router, prefix="/api/v1")
app.include_router(sensors.router, prefix="/api/v1")
app.include_router(countermeasures.router, prefix="/api/v1")
app.include_router(protection.router, prefix="/api/v1")
app.include_router(reports.router, prefix="/api/v1")
app.include_router(settings.router, prefix="/api/v1")
app.include_router(osint.router, prefix="/api/v1")


@app.on_event("startup")
async def startup():
    from retro.storage.connection import init_database
    from retro.core.engine import engine
    from retro.sensors.ssh_honeypot import SSHHoneypot
    from retro.sensors.http_honeypot import HTTPHoneypot
    from retro.sensors.port_scan import PortScanDetector
    from retro.sensors.log_importer import LogImporter
    engine.register_sensor("ssh_honeypot", SSHHoneypot())
    engine.register_sensor("http_honeypot", HTTPHoneypot())
    engine.register_sensor("port_scan_detector", PortScanDetector())
    engine.register_sensor("log_importer", LogImporter())
    await init_database()


@app.on_event("shutdown")
async def shutdown():
    from retro.core.engine import engine
    await engine.stop_sensors()
    from retro.storage.connection import close_database
    await close_database()
