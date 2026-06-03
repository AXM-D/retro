from datetime import datetime
from pydantic import BaseModel, Field


class DashboardResponse(BaseModel):
    total_events: int = 0
    unique_attackers: int = 0
    blocked_attackers: int = 0
    reported_attackers: int = 0
    recent_events: list[dict] = Field(default_factory=list)
    recent_alerts: list[dict] = Field(default_factory=list)


class AttackEventResponse(BaseModel):
    id: str
    sensor: str
    event_type: str
    source_ip: str
    timestamp: str
    data: dict = Field(default_factory=dict)
    processed: bool = False
    threat_score: float = 0.0
    investigation_id: str | None = None


class AttackerResponse(BaseModel):
    ip: str
    first_seen: str
    last_seen: str
    total_events: int = 0
    event_types: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    osint_data: dict = Field(default_factory=dict)
    threat_score: float = 0.0
    blocked: bool = False
    reported: bool = False


class CountermeasureRequest(BaseModel):
    action: str
    target: str
    target_type: str = "ip"
    comment: str = ""
    auto_approve: bool = False


class SensorControlRequest(BaseModel):
    action: str = "start"


class SensorStatusResponse(BaseModel):
    name: str
    running: bool
    config: dict = Field(default_factory=dict)


class AlertResponse(BaseModel):
    id: int
    title: str
    message: str
    severity: str = "info"
    source_ip: str | None = None
    read: bool = False
    created_at: str


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "0.1.0"
    app: str = "RETRO"
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
