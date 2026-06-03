from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from pathlib import Path
from retro.core.config import config
from retro.core.engine import engine
from retro.reporting.html_report import generate_html_report
from retro.reporting.pdf_report import generate_pdf_report

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/generate/{event_id}")
async def generate_report(event_id: str, format: str = "html"):
    events = await engine.get_events(limit=1000)
    event = next((e for e in events if e.id == event_id), None)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    incident = event.to_dict()
    incident["osint"] = {}
    profile = await engine.get_attacker(event.source_ip)
    if profile:
        incident["osint"] = profile.osint_data
    if format == "pdf":
        output_path = str(config.retro.data_dir / f"report_{event_id}.pdf")
        path = await generate_pdf_report(incident, output_path)
        return {"status": "generated", "path": path}
    html = await generate_html_report(incident)
    return HTMLResponse(content=html)
